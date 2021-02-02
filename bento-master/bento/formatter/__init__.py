from typing import Any, Dict

import bento.util
from bento.base_context import BaseContext
from bento.formatter import base, clippy, histo, json, reporter, stylish

FORMATTERS = {
    "stylish": stylish.Stylish,
    "json": json.Json,
    "clippy": clippy.Clippy,
    "histo": histo.Histo,
    "reporter": reporter.Reporter,
}


def for_name(name: str, context: BaseContext, config: Dict[str, Any]) -> base.Formatter:
    """
    Reflectively instantiates a formatter from a preset name or python identifier

    E.g.
      for_name("stylish", {})
      for_name("bento.formatter.stylish.Stylish", {})
    both return a new instance of the Stylish formatter

    Parameters:
        name (str): The formatter name, as a key of FORMATTERS, or a python fully qualified identifier
        config (dict): The formatter's configuration (formatter-specific)
    """
    tpe = FORMATTERS.get(name.lower(), None)
    if tpe is None:
        tpe = bento.util.for_name(name)
    fmt = tpe(context, config)  # type: ignore
    return fmt


FindingsMap = base.FindingsMap
Formatter = base.Formatter
