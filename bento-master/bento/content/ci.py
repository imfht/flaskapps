from bento.renderer import (
    Confirm,
    Echo,
    Link,
    Multi,
    Newline,
    Processors,
    Progress,
    Steps,
    Sub,
    Text,
    Warn,
)


class Install:
    learn_more = Text(
        "To learn more, see the README.",
        processor=Processors.wrap_link(
            [
                Link(
                    "README",
                    "https://github.com/returntocorp/bento/blob/master/README.md#running-in-cicd",
                )
            ]
        ),
    )

    banner = Steps(
        Echo(
            Multi(
                [
                    "Configuring a GitHub Action to automatically check your team's pull requests. ",
                    learn_more,
                ],
                processor=Processors.wrap(),
            )
        ),
        Newline(),
    )

    progress = Progress(
        content=Multi(
            [
                "Creating GitHub Action configuration at ",
                Sub(0, style={"bold": True, "dim": True}),
                Text("/", style={"bold": True, "dim": True}),
            ]
        ),
        extra=24,
    )
    after_progress = Newline()

    finalize_ci = Steps(
        Warn("To finalize configuration of Bento's GitHub Action, please:"),
        Echo(
            Multi(
                [
                    "  $ git add .github/\n",
                    '  $ git commit -m "Add Bento GitHub Action"\n',
                    "  $ git push\n",
                ]
            )
        ),
    )


class Overwrite:
    warn = Steps(
        Echo(
            Multi(
                [
                    "It seems Bento is already installed for GitHub Actions at ",
                    Sub(0, style={"bold": True}),
                ]
            )
        ),
        Newline(),
        Warn(
            "If you continue, Bento will revert any changes "
            "you might have made manually to this CI configuration file."
        ),
        Newline(),
    )

    confirm = Confirm(
        "Do you want to revert Bento's GitHub Action to the default configuration?"
    )

    after_confirm = Newline()
