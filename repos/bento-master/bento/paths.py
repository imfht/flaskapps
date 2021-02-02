import os
from typing import Any, List

from bento.util import AutocompleteSuggestions


def list_paths(ctx: Any, args: List[str], incomplete: str) -> AutocompleteSuggestions:
    """
    Lists paths when tab autocompletion is used on a path argument.

    Note that click always adds a space at the end of a suggestion, so repeated tabbing
    can not be used to fill a path. :(

    :param ctx: Unused
    :param args: Unused
    :param incomplete: Any partial completion currently under the cursor
    :return: A list of completion suggestions
    """
    # Cases for "incomplete" variable:
    #   - '': Search '.', no filtering
    #   - 'part_of_file': Search '.', filter
    #   - 'path/to/dir/': Search 'path/to/dir', no filter
    #   - 'path/to/dir/part_of_file': Search 'path/to/dir', filter
    dir_root = os.path.dirname(incomplete)
    path_stub = incomplete[len(dir_root) :]
    if path_stub.startswith("/"):
        path_stub = path_stub[1:]
    if dir_root == "":
        dir_to_list = "."
    else:
        dir_to_list = dir_root
    return [
        os.path.join(dir_root, p)
        for p in os.listdir(dir_to_list)
        if not path_stub or p.startswith(path_stub)
    ]
