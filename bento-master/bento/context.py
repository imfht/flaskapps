import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Tuple, Type

import attr

import bento.extra
import bento.formatter
from bento.base_context import BaseContext
from bento.error import EnabledToolNotFoundException, MultipleErrorsException
from bento.formatter import Formatter
from bento.tool import Tool

if TYPE_CHECKING:
    from bento.error import BentoException


@attr.s(repr=False)
class Context(BaseContext):
    _formatters = attr.ib(type=List[Formatter], default=None, init=False)
    _start = attr.ib(type=float, default=time.time(), init=False)
    _user_start = attr.ib(type=float, default=None, init=False)
    _user_duration = attr.ib(type=float, default=0.0, init=False)
    _timestamp = attr.ib(
        type=str, default=str(datetime.utcnow().isoformat("T")), init=False
    )
    _tool_inventory = attr.ib(type=Dict[str, Type[Tool]], init=False, default=None)
    _tools = attr.ib(type=Dict[str, Tool], init=False, default=None)
    _configured_tools = attr.ib(
        type=Optional[Dict[str, Tool]], init=False, default=None
    )
    _errors_on_exit = attr.ib(type=List["BentoException"], init=False, factory=list)

    def __repr__(self) -> str:
        return f"Context({self.base_path})"

    @property
    def formatters(self) -> List[Formatter]:
        if self._formatters is None:
            self._formatters = self._load_formatters()
        return self._formatters

    @property
    def tools(self) -> Dict[str, Tool]:
        """
        Returns all enabled tools
        """
        if self._tools is None:
            self._tools = self._load_enabled_tools()
        return self._tools

    @property
    def configured_tools(self) -> Dict[str, Tool]:
        """
        Returns all configured tools (whether or not they are disabled)
        """
        if self._configured_tools is None:
            self._configured_tools = self._load_configured_tools()
        return self._configured_tools

    @property
    def tool_inventory(self) -> Dict[str, Type[Tool]]:
        if self._tool_inventory is None:
            self._tool_inventory = self._load_tool_inventory()
        return self._tool_inventory

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def elapsed(self) -> float:
        return time.time() - self._start

    def user_duration(self) -> Optional[float]:
        """
        Returns elapsed time in seconds since formatter was opened
        """
        return self._user_duration

    def tool(self, tool_id: str) -> Tool:
        """
        Returns a specific configured tool

        Raises:
            AttributeError: If the requested tool is not configured
        """
        tt = self.tools
        if tool_id not in tt:
            raise AttributeError(f"{tool_id} not one of {', '.join(tt.keys())}")
        return tt[tool_id]

    def start_user_timer(self) -> None:
        self._user_start = time.perf_counter()

    def stop_user_timer(self) -> None:
        if self._user_start is None:
            return
        self._user_duration += time.perf_counter() - self._user_start

    def error_on_exit(self, exc: "BentoException") -> None:
        """
        Queue up an exception to cause Bento to fail at the end of invocation.
        """
        self._errors_on_exit.append(exc)

    @property
    def on_exit_exception(self) -> Optional["BentoException"]:
        """
        The exception to raise at the end of Bento's invocation.

        :return: `None` if no errors were queued,
                 a `BentoException` if one error was queued,
                 or a `MultipleErrorsException` if several errors were queued.
        """
        if not self._errors_on_exit:
            return None
        elif len(self._errors_on_exit) == 1:
            return self._errors_on_exit[0]
        else:
            return MultipleErrorsException(self._errors_on_exit)

    def _load_tool_inventory(self) -> Dict[str, Type[Tool]]:
        """
        Loads all tools in the module into a dictionary indexed by tool_id
        """
        all_tools = {}
        for tt in bento.extra.TOOLS:
            tool_id = tt.tool_id()
            all_tools[tool_id] = tt
        logging.debug(f"Known tool IDs are {', '.join(all_tools.keys())}")
        return all_tools

    def _load_enabled_tools(self) -> Dict[str, Tool]:
        """
        Returns a list of this project's enabled tools
        These are the tools in the configuration file that do
        not have "run" option set to False
        """
        tools: Dict[str, Tool] = {}
        inventory = self.tool_inventory
        for tn, tool_config in self.config["tools"].items():
            if "run" in tool_config and not tool_config["run"]:
                continue

            ti = inventory.get(tn, None)
            if not ti:
                self.error_on_exit(EnabledToolNotFoundException(tool=tn))
                continue

            tools[tn] = ti(self)

        return tools

    def _load_configured_tools(self) -> Dict[str, Tool]:
        """
        Returns list of this project's configured tools (disabled and enabled)
        """
        tools: Dict[str, Tool] = {}
        inventory = self.tool_inventory
        for tn in self.config["tools"].keys():
            ti = inventory.get(tn, None)
            if not ti:
                # skip, we will only error if the tool is enabled
                continue

            tools[tn] = ti(self)

        return tools

    def _load_formatters(self) -> List[Formatter]:
        """
        Returns this project's configured formatter
        """
        if "formatter" not in self.config:
            return [bento.formatter.stylish.Stylish(self, {})]
        else:
            FormatterConfig = Dict[str, Any]
            FormatterSpec = Tuple[str, FormatterConfig]

            cfg = self.config["formatter"]

            # Before 0.6, configuration is a simple (unordered) dictionary:
            it: Iterator[FormatterSpec]
            if isinstance(cfg, dict):
                it = iter(cfg.items())
            # After 0.6, configuration is ordered list of dictionaries,
            # Convert to ordered list of tuples.
            else:
                it = (next(iter(f.items())) for f in cfg)

            return [bento.formatter.for_name(f_class, self, cfg) for f_class, cfg in it]
