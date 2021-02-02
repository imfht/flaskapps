import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Tuple, TypeVar, Union, cast

import attr
from click import confirm, prompt, secho, style

import bento.util

# Return type for renderer
R = TypeVar("R", covariant=True)

# Represents a text transformation
Processor = Callable[[str], str]


@attr.s(auto_attribs=True)
class Link:
    """
    Represents a link definition

    :param anchor: Link anchor text
    :param href: Link target
    """

    anchor: str
    href: str


class Processors:
    identity: Processor = lambda text: text

    @staticmethod
    def ljust(extra: int = 0, char: str = " ") -> Processor:
        """
        Left-justifies text, filling width with specified character

        :param extra: Number of extra characters to add to justification (useful for
                      accommodating ANSI control characters
        :param char: The fill character
        """
        return lambda text: text.ljust(bento.util.PRINT_WIDTH + extra, char)

    @staticmethod
    def wrap(extra: int = 0) -> Processor:
        """
        Wraps text to print width

        :param extra: Number of extra characters to add to margin (useful for
                      accommodating ANSI control characters
        """
        return lambda text: bento.util.wrap(text, extra)

    @staticmethod
    def wrap_link(links: List[Link], extra: int = 0, **kwargs: Any) -> Processor:
        """
        Per wrap, except links are rendered without affecting the wrap width.

        In addition to the specification of process_wrap, a sequence of "link" values controls link processing.

        Links are only rendered if the terminal is a known supporting terminal for OSC8 links. If not,
        links are rendered as their anchor text only.

        :param links: Link definitions
        :param extra: Any extra width to apply
        :param kwargs: Styling rules passed to text
        """

        def _wrap_link(text: str) -> str:
            wrapped = bento.util.wrap(text, extra)

            def find_loc(anchor: str) -> Tuple[int, str]:
                """
                Finds the position of the anchor string in the wrapped text

                Note that the anchor string itself may be wrapped, so we return
                both the position, and the value of the (possibly wrapped) anchor string.
                """
                pos = wrapped.find(anchor)
                if pos < 0:
                    # Text was likely wrapped
                    anchor_it = [
                        f"{anchor[:ix].rstrip()}\n{anchor[ix:]}"
                        for ix in range(len(anchor))
                    ]
                    pos_it = ((wrapped.find(a), a) for a in anchor_it)
                    pos, anchor = next(
                        ((p, a) for p, a in pos_it if p > 0), (-1, anchor)
                    )
                    if pos < 0:
                        raise ValueError(f"'{anchor}' does not appear in '{text}'")
                return pos, anchor

            with_locs = sorted(
                [(find_loc(link.anchor), link.href) for link in links],
                key=(lambda t: t[0][0]),
            )
            out = ""
            current = 0
            for loc_anchor, href in with_locs:
                loc, anchor = loc_anchor
                out += style(wrapped[current:loc], **kwargs)
                out += bento.util.render_link(
                    anchor, href, print_alternative=False, pipe=sys.stderr
                )
                current = loc + len(anchor)
            out += style(wrapped[current:], **kwargs)

            return out

        return _wrap_link


class Content(ABC):
    """
    Represents styled, processed, textual content

    Each implementation of this class should define the following keyword arguments:
    :param processor: The text processor to apply
    :param style: Style rules to apply
    """

    def __init__(self) -> None:
        self.processor = Processors.identity
        self.style: Dict[str, Any] = {}

    @abstractmethod
    def make(self, *args: Any) -> str:
        pass

    def expand(self, *args: Any, apply_style: bool = False) -> str:
        text = self.processor(self.make(*args))
        if apply_style:
            return style(text, **self.style)
        else:
            return text


@attr.s()
class Sub(Content):
    """
    Represents text taken from an argument

    Substitution uses the argument's `str` value.

    :param index: The index of the argument list to substitute
    """

    index = attr.ib(type=int)
    style = attr.ib(type=Dict[str, Any], kw_only=True, default={})
    processor = attr.ib(
        type=Callable[[str], str], kw_only=True, default=Processors.identity
    )

    def make(self, *args: Any) -> str:
        return str(args[self.index])


@attr.s()
class Text(Content):
    """
    Represents literal text

    :param text: The text
    """

    text = attr.ib(type=str)
    style = attr.ib(type=Dict[str, Any], kw_only=True, default={})
    processor = attr.ib(
        type=Callable[[str], str], kw_only=True, default=Processors.identity
    )

    def make(self, *args: Any) -> str:
        return self.text


@attr.s()
class Multi(Content):
    """
    Represents a concatenation of other content

    :param items: The wrapped content; a literal string may also be used instead of unstyled, unprocessed Text content
    """

    items = attr.ib(type=List[Union[str, Content]])
    style = attr.ib(type=Dict[str, Any], kw_only=True, default={})
    processor = attr.ib(
        type=Callable[[str], str], kw_only=True, default=Processors.identity
    )

    def make(self, *args: Any) -> str:
        converted = (c if isinstance(c, Content) else Text(c) for c in self.items)
        parts = (c.expand(*args, apply_style=True) for c in converted)
        return "".join(parts)


@attr.s
class Renderer(ABC, Generic[R]):
    """
    Renders content from a YAML file

    To create, use:

      [RendererType](content, ...)

    To use, invoke:

      renderer.echo(*args, **kwargs)

    `args` are a list of arguments to be used in substitution content;
    `kwargs` are passed directly to the renderer, and their allowed values depend
    on the renderer in question.

    :param content: A Content object, defaults to empty text
    :param styling: A styling dictionary, defaults to no styling
    """

    content = attr.ib(type=Union[str, Content], default=Text(""))
    styling = attr.ib(type=Dict[str, Any], init=False)

    def __attrs_post_init__(self) -> None:
        if isinstance(self.content, str):
            self.content = Text(self.content)
        self.styling = self.content.style

    @abstractmethod
    def render(self, text: str, **kwargs: Any) -> R:
        """
        Renders content

        :param text: The styled and processed content
        :param kwargs: Any keyword arguments to be used by this renderer
        :return: This renderer's return value
        """
        pass

    def text(self, *args: Any) -> str:
        """
        Returns un-rendered (but styled) content text

        :param args: Arguments for substitution content
        """
        return cast(Content, self.content).expand(*args, apply_style=True)

    def echo(self, *args: Any, **kwargs: Any) -> R:
        """
        Renders content

        :param args: Arguments for substitution content
        :param kwargs: Renderer-specific arguments (see help for that renderer's `render` method)
        """
        text = cast(Content, self.content).expand(*args, apply_style=False)
        return self.render(text, **kwargs)


@attr.s
class Box(Renderer[None]):
    """
    Renders content in a Unicode-drawn box to stderr
    """

    def render(self, text: str, **kwargs: Any) -> None:
        bento.util.echo_box(text)


@attr.s(auto_attribs=True)
class Confirm(Renderer[bool]):
    """
    Renders a confirmation prompt, and returns confirmation state.

    :param options: Arguments to be passed to click.confirm
    """

    options: Dict[str, Any] = {}

    def render(self, text: str, **kwargs: Any) -> bool:
        """
        :param kwargs: Arguments passed to click.confirm (in addition to self.options)
        :return: The entered value
        """
        options = {**self.options, **kwargs}
        return confirm(style(text, **self.styling), err=True, **options)


@attr.s(auto_attribs=True)
class Prompt(Renderer[str]):
    """
    Renders a text prompt, and returns text state.

    :param options: Arguments to be passed to click.prompt
    """

    options: Dict[str, Any] = {}

    def render(self, text: str, **kwargs: Any) -> str:
        """
        :param kwargs: Arguments passed to click.prompt (in addition to self.options)
        :return: The entered value
        """
        options = {**self.options, **kwargs}
        return prompt(style(text, **self.styling), err=True, **options)


@attr.s(auto_attribs=True)
class Echo(Renderer[None]):
    """
    Renders content, appended together, to stderr

    :param newline: Whether to render a newline at the end of content (default True)
    """

    newline: bool = True

    def render(self, text: str, **kwargs: Any) -> None:
        secho(text, err=True, nl=self.newline, **self.styling)


@attr.s(auto_attribs=True)
class Error(Renderer[None]):
    """
    Renders error content to stderr
    """

    def render(self, text: str, **kwargs: Any) -> None:
        bento.util.echo_error(text)


@attr.s(auto_attribs=True)
class Newline(Renderer[None]):
    """
    Renders a newline

    :raises ValueError: If content is not empty text
    """

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.content, Text) or self.content.text:
            raise ValueError("Newline renderer should not have content")

    def render(self, text: str, **kwargs: Any) -> None:
        bento.util.echo_newline()


@attr.s(auto_attribs=True)
class Success(Renderer[None]):
    """
    Renders success content to stderr
    """

    def render(self, text: str, **kwargs: Any) -> None:
        bento.util.echo_success(text)


@attr.s(auto_attribs=True)
class Warn(Renderer[None]):
    """
    Renders warning content to stderr
    """

    def render(self, text: str, **kwargs: Any) -> None:
        bento.util.echo_warning(text)


@attr.s(auto_attribs=True)
class Progress(Renderer[Callable[[], None]]):
    """
    Renders a progress bar

    For more information, see bento.util.echo_progress.

    :param extra: Extra width to pass to `echo_progress`
    :return: The progress done callback
    """

    extra: int = 0

    def render(self, text: str, **kwargs: Any) -> Callable[[], None]:
        return bento.util.echo_progress(text, self.extra, **kwargs)


class Steps:
    """
    Successively renders multiple Renderer objects
    """

    def __init__(self, *steps: Renderer) -> None:
        self.steps = steps

    def echo(self, *args: Any, **kwargs: Any) -> List[Any]:
        return [s.echo(*args, **kwargs) for s in self.steps]
