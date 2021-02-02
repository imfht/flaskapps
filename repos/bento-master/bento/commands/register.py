import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import attr
import click
from packaging.version import InvalidVersion, Version

import bento.commands.autocomplete as autocomplete
import bento.constants as constants
import bento.content.register as content
import bento.decorators
import bento.extra
import bento.git
import bento.metrics
import bento.tool_runner
import bento.util
from bento.context import Context
from bento.error import InvalidVersionException, NonInteractiveTerminalException
from bento.network import post_metrics
from bento.util import echo_newline, persist_global_config, read_global_config

GLOBAL_GITIGNORE_PATTERN = ".bento/\n.bentoignore"


@attr.s(auto_attribs=True)
class Registrar:
    click_context: click.Context
    agree: bool
    is_first_run: bool = False
    context: Context = attr.ib(init=False)
    global_config: Dict[str, Any] = attr.ib(factory=read_global_config, init=False)
    email: Optional[str] = attr.ib()
    _displays_progress_bars: bool = attr.ib(init=False, default=False)

    @email.default
    def _get_email_from_environ(self) -> Optional[str]:
        return os.environ.get(constants.BENTO_EMAIL_VAR)

    def __attrs_post_init__(self) -> None:
        self.context = self.click_context.obj
        if self.global_config is None:
            self.is_first_run = True
            self.global_config = {}

    def _validate_interactivity(self) -> None:
        """
        Validates that this Bento session is running interactively

        :raises: SystemExit(3) if not interactive
        """
        is_interactive = sys.stdin.isatty() and sys.stderr.isatty()
        if not is_interactive:
            content.not_registered.echo()
            raise NonInteractiveTerminalException()

    def _show_welcome_message(self) -> None:
        """
        Displays a 'welcome to Bento' message

        Message is only displayed if registration is not skipped via command-line arguments

        :param agree: If the user has agreed to all prompts via the command line
        :param email: The user's email, if supplied via command line
        """
        if (
            self.email is None
            and "email" not in self.global_config
            or not self.agree
            and constants.TERMS_OF_SERVICE_KEY not in self.global_config
        ):
            content.welcome.echo()

    def _update_email(self) -> None:
        """
        Updates the user's global config with their email address

        If the user has passed an email on the command line, this logic is skipped.
        """
        # import inside def for performance
        from validate_email import validate_email

        if not self.email:
            self.email = self.global_config.get("email")

        if not self.email or not validate_email(self.email):
            content.UpdateEmail.leader.echo()

            email = None
            while not (email and validate_email(email)):
                self.context.start_user_timer()
                self._validate_interactivity()
                email = content.UpdateEmail.prompt.echo(
                    type=str, default=bento.git.user_email()
                )
                self.context.stop_user_timer()
                echo_newline()

            if email != constants.QA_TEST_EMAIL_ADDRESS:
                r = self._post_email_to_mailchimp(email)
                if not r:
                    content.UpdateEmail.failure.echo()

            self.global_config["email"] = email
            persist_global_config(self.global_config)

    @staticmethod
    def _post_email_to_mailchimp(email: str) -> bool:
        """
        Subscribes this email to the Bento mailing list

        :return: Mailchimp's response status
        """
        # import inside def for performance
        import requests

        r = requests.post(
            "https://waitlist.r2c.dev/subscribe", json={"email": email}, timeout=5
        )
        status: bool = r.status_code == requests.codes.ok
        data = [
            {
                "message": "Tried adding user to Bento waitlist",
                "user-email": email,
                "mailchimp_response": r.status_code,
                "success": status,
            }
        ]
        logging.info(f"Registering user with data {data}")
        post_metrics(data)
        return status

    def _confirm_tos_update(self) -> bool:
        """
        Interactive process to confirm updated agreement to the Terms of Service

        :return: If the user has agreed to the updated ToS
        """
        if constants.TERMS_OF_SERVICE_KEY not in self.global_config:
            content.ConfirmTos.fresh.echo()
        else:
            # We care that the user has agreed to the current terms of service
            tos_version = self.global_config[constants.TERMS_OF_SERVICE_KEY]

            try:
                agreed_to_version = Version(tos_version)
                if agreed_to_version == Version(constants.TERMS_OF_SERVICE_VERSION):
                    logging.info("User ToS agreement is current")
                    return True
            except InvalidVersion:
                content.ConfirmTos.invalid_version.echo()
                raise InvalidVersionException()

            content.ConfirmTos.upgrade.echo()

        self.context.start_user_timer()
        self._validate_interactivity()
        agreed = content.ConfirmTos.prompt.echo()
        echo_newline()
        self.context.stop_user_timer()

        if agreed:
            self.global_config[
                constants.TERMS_OF_SERVICE_KEY
            ] = constants.TERMS_OF_SERVICE_VERSION

            persist_global_config(self.global_config)
            return True
        else:
            content.ConfirmTos.error.echo()
            return False

    def _query_gitignore_update(self) -> Tuple[Path, bool]:
        """
        Determines if gitignore should be updated by init

        Requirements:
        - Interactive terminal
        - bento/ not in ignore file
        - User hasn't previously opted out
        - User agrees

        :return: A tuple of (the path to the global git ignore, whether to update the file)
        """

        gitignore_path = (
            bento.git.global_ignore_path(self.context.base_path)
            or constants.DEFAULT_GLOBAL_GIT_IGNORE_PATH
        )

        if sys.stderr.isatty() and sys.stdin.isatty():
            opt_out_value = self.global_config.get(constants.GLOBAL_GIT_IGNORE_OPT_OUT)
            user_opted_out = opt_out_value is not None and opt_out_value is True
            if user_opted_out:
                return gitignore_path, False
            has_ignore = None
            if gitignore_path.exists():
                with gitignore_path.open("r") as fd:
                    has_ignore = next(filter(lambda l: ".bento" in l, fd), None)
            if has_ignore is None:
                self.context.start_user_timer()
                if content.UpdateGitignore.confirm.echo(gitignore_path):
                    gitignore_path.parent.resolve().mkdir(exist_ok=True, parents=True)
                    content.UpdateGitignore.confirm_yes.echo()
                    return gitignore_path, True
                else:
                    self.global_config[constants.GLOBAL_GIT_IGNORE_OPT_OUT] = True

                    persist_global_config(self.global_config)
                    content.UpdateGitignore.confirm_no.echo()
                self.context.stop_user_timer()
        return gitignore_path, False

    def _update_gitignore_if_necessary(self, ignore_path: Path, update: bool) -> None:
        """
        Adds bento patterns to global git ignore if _query_gitignore_update returned a path
        """
        if update:
            self._displays_progress_bars = True
            on_done = content.UpdateGitignore.update.echo(ignore_path)
            bento.util.append_text_to_file(
                ignore_path,
                f"# Ignore bento tool run paths (this line added by `bento init`)\n{GLOBAL_GITIGNORE_PATTERN}",
            )
            on_done()
            logging.info(f"Added '.bento/' to {ignore_path}")

    def _suggest_autocomplete(self) -> None:
        """
        Suggests code to add to the user's shell config to set up autocompletion
        """
        shell = os.environ.get("SHELL")
        if not shell:
            return

        self._validate_interactivity()
        shell_cmd = shell.split("/")[-1]
        if shell_cmd in autocomplete.SUPPORTED:
            self.context.start_user_timer()
            should_add = content.SuggestAutocomplete.confirm.echo()
            self.context.stop_user_timer()
            if should_add:
                content.SuggestAutocomplete.confirm_yes.echo()
                self._displays_progress_bars = True
                on_done = content.SuggestAutocomplete.install.echo(
                    autocomplete.SUPPORTED[shell_cmd][0]
                )
                self.click_context.invoke(autocomplete.install_autocomplete, [False])
                on_done()
            else:
                content.SuggestAutocomplete.confirm_no.echo()

    def verify(self) -> bool:
        """
        Performs all necessary steps to ensure user registration:

        - Global config exists
        - User has agreed to Terms of Service
        - User has registered with email

        :param agree: If True, automatically confirms all yes/no prompts
        :param email: If exists, registers with this email
        :param context: The CLI context
        :return: Whether the user is properly registered after this function terminates
        """

        self._show_welcome_message()
        self._update_email()

        if not self.agree and not self._confirm_tos_update():
            return False

        # only ask about updating gitignore in init
        ignore_path: Optional[Path] = None
        update_ignore: Optional[bool] = None
        if not self.agree and self.context.is_init:
            ignore_path, update_ignore = self._query_gitignore_update()

        if self.is_first_run and not self.agree:
            self._suggest_autocomplete()

        if ignore_path is not None and update_ignore is not None:
            self._update_gitignore_if_necessary(ignore_path, update_ignore)

        if self._displays_progress_bars:
            content.finalize.echo()

        return True
