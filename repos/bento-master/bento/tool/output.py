from bento.tool.tool import JsonR, Tool

"""
Classes that define the output format of a tool
"""

Str = Tool[str]
"""Output is a raw string"""

Json = Tool[JsonR]
"""Output is parsed JSON (of type bento.tool.JsonR)"""
