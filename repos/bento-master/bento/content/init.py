from bento.renderer import (
    Box,
    Confirm,
    Content,
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

from . import ci as ci_content


def _step_item(desc: str, cmd: str, nl: bool = True) -> Content:
    """
    Echoes

      desc․․․․․․․․․․․․․․․․․․․․․․․․․․․․․․․․․․ $ cmd

    with styling.

    If 'nl' is False, does not emit a newline at the end of the line
    """
    return Multi(
        [
            "  ",
            Text(desc, processor=Processors.ljust(-40, "․"), style={"dim": True}),
            f" $ {cmd}\n",
        ]
    )


class InstallConfig:
    install = Progress(
        content=Multi(
            [
                "Creating default configuration at ",
                Sub(0, style={"bold": True, "dim": True}),
            ]
        ),
        extra=12,
    )


class InstallIgnore:
    install = Progress(
        content=Multi(
            [
                "Creating default ignore file at ",
                Sub(0, style={"bold": True, "dim": True}),
            ]
        ),
        extra=12,
    )


class InstallAutorun:
    install = Progress(
        Multi(
            [
                "Enabling autorun (see $ ",
                Text("bento enable autorun --help", style={"dim": True, "bold": True}),
                Text(")", style={"dim": True}),
            ]
        ),
        extra=20,
    )


class InstallCI:
    pitch = Steps(
        Echo(
            Multi(
                [
                    "Bento can configure a GitHub Action to automatically check your team's pull requests. ",
                    ci_content.Install.learn_more,
                ],
                processor=Processors.wrap(),
            )
        ),
        Newline(),
    )

    confirm = Confirm("Do you want to configure Bento's GitHub Action now?")
    after_confirm = Newline()

    progress = ci_content.Install.progress
    finalize_ci = ci_content.Install.finalize_ci


class InstallTools:
    install = Echo("Installing tools:\n")


class Clean:
    tools = Steps(Echo("Reinstalling tools due to passed --clean flag."), Newline())
    check = Warn(
        """
Removing archive due to passed --clean flag.
"""
    )


class Identify:
    success = Steps(
        Newline(),
        Echo(Multi(["Bento initialized for ", Sub(0, style={"bold": True})])),
        Newline(),
    )
    failure = Steps(
        Newline(),
        Warn(
            "Bento can't automatically identify this project. Please manually configure this project:"
        ),
        Echo(
            Multi(
                [
                    _step_item("configure a tool manually", "bento enable tool TOOL"),
                    _step_item("list available tools", "bento enable tool --help"),
                ]
            )
        ),
    )


class Finish:
    body = Steps(
        Box("Thank You"),
        Echo(
            Text(
                "From all of us at r2c, thank you for trying Bento! We can’t wait to hear what you think.",
                processor=Processors.wrap(),
            )
        ),
        Newline(),
        Echo(
            Multi(
                [
                    "Help and feedback: ",
                    Text("Reach out to us at ", style={"dim": True}),
                    "support@r2c.dev",
                    Text(" or file an issue on ", style={"dim": True}),
                    "GitHub",
                    Text(". We’d love to hear from you!", style={"dim": True}),
                ],
                processor=Processors.wrap_link(
                    [
                        Link("support@r2c.dev", "mailto:support@r2c.dev"),
                        Link("GitHub", "https://github.com/returntocorp/bento/issues"),
                    ],
                    extra=16,
                ),
            )
        ),
        Newline(),
        Echo(
            Multi(
                [
                    "Community: ",
                    Text("Join ", style={"dim": True}),
                    "#bento",
                    Text(
                        " on our community Slack. Get support, talk with other users, and share feedback.",
                        style={"dim": True},
                    ),
                ],
                processor=Processors.wrap_link(
                    [
                        Link(
                            "#bento",
                            "https://join.slack.com/t/r2c-community/shared_invite/enQtNjU0NDYzMjAwODY4LWE3NTg1MGNhYTAwMzk5ZGRhMjQ2MzVhNGJiZjI1ZWQ0NjQ2YWI4ZGY3OGViMGJjNzA4ODQ3MjEzOWExNjZlNTA",
                        )
                    ],
                    extra=16,
                ),
            )
        ),
        Newline(),
        Echo("Go forth and write great code! To use Bento:"),
        Echo(
            Multi(
                [
                    _step_item("commit code", "git commit"),
                    _step_item(
                        "get help for a command", "bento [COMMAND] --help", nl=False
                    ),
                ]
            )
        ),
    )


class Start:
    banner = Steps(
        Box("Bento Initialization"),
        Echo(
            Text(
                "Bento configures itself for personal use by default. This means that it:",
                processor=Processors.wrap(),
            )
        ),
        Newline(),
        Echo(
            Text(
                "1. Automatically checks for issues introduced by your code, as you commit it",
                processor=Processors.wrap(),
            )
        ),
        Echo(
            Text(
                "2. Only affects you; it won’t change anything for other project contributors",
                processor=Processors.wrap(),
            )
        ),
        Newline(),
        Echo(
            Text(
                "Learn more about personal and team use at bento.dev/workflows.",
                processor=Processors.wrap_link(
                    [Link("bento.dev/workflows", "https://bento.dev/workflows")]
                ),
            )
        ),
        Newline(),
    )
    confirm = Steps(Confirm("Press ENTER to add Bento to this project"), Newline())
