import logging
import os
import platform
import traceback
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from bento.util import EMPTY_DICT

BASE_URL = "https://bento.r2c.dev"
# Add default timeout so that we do not block the user's main thread from exiting
# 1 second value is so that user does not get impatient
TIMEOUT = 1  # sec

if TYPE_CHECKING:
    # Only import when type checking to avoid loading module when unecessary
    from requests.models import Response  # noqa


PostData = List[Dict[str, Any]]


def _get_version() -> str:
    from bento import __version__

    return __version__


def _get_default_shell() -> str:
    return os.environ.get("SHELL", "")


def _get_default_headers() -> Dict[str, str]:
    """
    Headers for all bento http/s requests
    """
    return {
        "X-R2C-BENTO-User-Platform": f"{platform.platform()}",
        "X-R2C-BENTO-User-Shell": f"{_get_default_shell()}",
        "X-R2C-BENTO-Cli-Version": f"{_get_version()}",
        "Accept": "application/json",
    }


def no_auth_get(
    url: str,
    params: Dict[str, str] = EMPTY_DICT,
    headers: Dict[str, str] = EMPTY_DICT,
    **kwargs: Any,
) -> "Response":
    # import inside def for performance
    import requests

    """Perform a requests.get and default headers set"""
    headers = {**_get_default_headers(), **headers}
    r = requests.get(
        url, headers=headers, params=params, **{"timeout": TIMEOUT, **kwargs}
    )
    return r


def no_auth_post(
    url: str,
    json: Any = EMPTY_DICT,
    params: Dict[str, str] = EMPTY_DICT,
    headers: Dict[str, str] = EMPTY_DICT,
    timeout: float = TIMEOUT,
) -> "Response":
    # import inside def for performance
    import requests

    """Perform a requests.post and default headers set"""
    headers = {**_get_default_headers(), **headers}
    r = requests.post(url, headers=headers, params=params, json=json, timeout=timeout)
    return r


def _get_base_url() -> str:
    return BASE_URL


def fetch_latest_version() -> Tuple[Optional[str], Optional[str]]:
    try:
        url = f"{_get_base_url()}/bento/api/v1/version"
        r = no_auth_get(url)
        response_json = r.json()
        return response_json.get("latest", None), response_json.get("uploadTime", None)
    except Exception as e:
        logging.exception(e)
        return None, None


def post_metrics(data: PostData, is_finding: bool = False) -> bool:
    try:
        url = f"{_get_base_url()}/bento/api/v4/metrics/"
        if is_finding:
            url = f"{url}finding/"
        # logging.debug(data)  # This spams the log when many findings
        r = no_auth_post(url, json=data)
        r.raise_for_status()
        return True
    except Exception as e:
        logging.warning(
            f"Exception while posting metrics {e}\n{traceback.format_exc()}"
        )
        return False
