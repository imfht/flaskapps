# !/usr/bin/env python3
import sys

import git


def get_current_commit() -> str:
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    return sha


def check_commit_merged_to_master(commit: str) -> bool:
    g = git.Git()
    log = g.log("--format='format:%d'", "-1")
    return "origin/master" in log or "origin/release-" in log


def main() -> None:
    c = get_current_commit()
    merged = check_commit_merged_to_master(c)
    if not merged:
        print(f"Current commit {c} is not merged. Aborting release!")
        sys.exit(1)


if __name__ == "__main__":
    main()
