from bento.renderer import (
    Box,
    Confirm,
    Echo,
    Error,
    Link,
    Multi,
    Newline,
    Processors,
    Progress,
    Prompt,
    Steps,
    Sub,
    Text,
    Warn,
)

not_registered = Steps(
    Error("This installation of Bento is not registered."),
    Echo(
        """
Please either:
◦ Register Bento by running it in an interactive terminal
◦ Run Bento with `--agree --email [EMAIL]`"""
    ),
)

welcome = Steps(
    Box("Global Bento Configuration"),
    Echo(
        Text(
            "Thanks for installing Bento, a free and opinionated toolkit for gradually adopting linters and program "
            "analysis in your codebase!",
            processor=Processors.wrap(),
        )
    ),
    Newline(),
)


finalize = Newline()


class UpdateEmail:
    leader = Steps(
        Echo(
            Multi(
                [
                    "Registration: ",
                    Text(
                        "We’ll use your email to provide support and share product updates. You can unsubscribe at "
                        "any time.",
                        style={"dim": True},
                    ),
                ],
                processor=Processors.wrap(extra=8),
            )
        ),
        Newline(),
    )
    prompt = Prompt("What is your email address?")
    failure = Steps(
        Newline(),
        Warn(
            "We were unable to subscribe you to the Bento mailing list (which means you may miss out on "
            "announcements!). Bento will continue running. Please shoot us a note via support@r2c.dev to debug. "
        ),
    )


class ConfirmTos:
    fresh = Steps(
        Echo(
            Multi(
                [
                    "Privacy: ",
                    Text(
                        "We take privacy seriously. Bento runs exclusively on your computer. It will never send your "
                        "code anywhere.",
                        style={"dim": True},
                    ),
                ],
                processor=Processors.wrap(extra=8),
            )
        ),
        Newline(),
        Echo(
            Text(
                "We’re constantly looking to make Bento better. To that end, we collect limited usage and results "
                "data. To learn more, see bento.dev/privacy.",
                processor=Processors.wrap_link(
                    [Link("bento.dev/privacy", "https://bento.dev/privacy")]
                ),
                style={"dim": True},
            )
        ),
        Newline(),
    )

    invalid_version = Error(
        "~/.bento/config.yml is malformed. Please remove this file and re-run Bento. "
    )

    upgrade = Steps(
        Echo(
            Text(
                "We've made changes to our terms of service. Please review the new terms. If you have any questions "
                "or concerns please reach out via support@r2c.dev.",
                processor=Processors.wrap_link(
                    [Link("support@r2c.dev", "mailto:support@r2c.dev")]
                ),
                style={"dim": True},
            )
        ),
        Newline(),
    )

    prompt = Confirm(
        "Continue and agree to Bento's terms of service and privacy policy?",
        options={"default": True},
    )
    error = Error(
        "Bento did NOT install. Bento beta users must agree to the terms of service to continue. Please reach out to "
        "us at support@r2c.dev with questions or concerns. "
    )


class UpdateGitignore:
    confirm = Confirm(
        content=Multi(
            [
                "Some Bento files should be excluded from version control. Should Bento append them to ",
                Sub(0, style={"bold": True}),
                "?",
            ],
            processor=Processors.wrap(),
        ),
        options={"default": True},
    )
    confirm_yes = Newline()
    confirm_no = Newline()
    update = Progress(
        content=Multi(["Updating ", Sub(0, style={"bold": True, "dim": True})]),
        extra=12,
    )


class SuggestAutocomplete:
    confirm = Confirm(
        Text(
            "Bento supports tab autocompletion. Do you want to add it to your shell profile now?",
            processor=Processors.wrap(),
        ),
        options={"default": True},
    )
    install = Progress(
        content=Multi(
            ["Adding autocompletion to ", Sub(0, style={"bold": True, "dim": True})]
        ),
        extra=12,
    )
    confirm_yes = Newline()
    confirm_no = Echo(
        Multi(
            [
                "\nTo enable autocompletion later, run $ ",
                Text("bento enable autocomplete", style={"bold": True}),
                ".\n",
            ]
        )
    )
