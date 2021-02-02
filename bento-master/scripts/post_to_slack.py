# !/usr/bin/env python3

import subprocess
from typing import Any, Dict

import requests

URL = str


def get_pkg_version() -> str:
    version = subprocess.check_output(["poetry", "version"]).decode("utf-8")
    v = version.split(" ")[-1].strip()
    return v


def get_post_data(version: str) -> Dict[str, Any]:
    """ Given semver version like 0.0.0, translate it to slack post like
    `@here Bento 0.0.0 is released`
  """
    return {"text": f"@here Bento {version} is released!"}


def main(webhook: str, version: str) -> None:
    """
    Post to #ops-announce, #bento channels
    about the release
  """
    try:
        headers = headers = {"content-type": "application/json"}
        data = get_post_data(version)
        resp = requests.post(webhook, json=data, headers=headers)
        if resp.status_code == requests.codes.ok:
            print("Successfully posted")
        else:
            print("Failed to post to slack")
    except Exception:
        print("Failed to post to slack")


if __name__ == "__main__":
    print(f"Input channel webhook from 1password")
    webhook: URL = input()
    main(webhook, get_pkg_version())
