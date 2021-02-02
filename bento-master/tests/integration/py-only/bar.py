import os
import subprocess


def do_it(cmd: str) -> None:
    subprocess.run(f"bash -c {cmd}", shell=True)


def bad_types(cmd: str) -> str:
    x: int = cmd + 5 + os.getenv('doesnotexist')
    return None
