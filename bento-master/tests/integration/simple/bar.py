import subprocess


def do_it(cmd: str) -> None:
    subprocess.run(f"bash -c {cmd}", shell=True)
