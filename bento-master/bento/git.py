import configparser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# XXX: This is hacky. This should maybe use the Context object or something to
# determine the base directory.

if TYPE_CHECKING:
    # Only import when type checking to avoid loading module when unecessary
    import git  # noqa


def repo(path: Optional[Path] = None) -> Optional["git.Repo"]:
    # import inside def for performance
    import git.exc

    try:
        r = git.Repo(str(path or Path.cwd()), search_parent_directories=True)
        return r
    except git.exc.InvalidGitRepositoryError:
        return None


# N.B. See https://stackoverflow.com/a/42613047
def user_email(path: Optional[Path] = None) -> Optional[str]:
    r = repo(path)
    if r is None:
        return None
    try:
        return r.config_reader().get_value("user", "email").strip("\"'")
    except configparser.NoSectionError:
        return None
    except configparser.NoOptionError:
        return None


def global_ignore_path(path: Optional[Path] = None) -> Optional[Path]:
    r = repo(path)
    if r is None:
        return None

    try:
        config_value = r.config_reader("global").get_value("core", "excludesfile")
        return Path(config_value.strip()).expanduser()
    except configparser.NoSectionError:
        return None
    except configparser.NoOptionError:
        return None


def url(path: Optional[Path] = None) -> Optional[str]:
    """Get remote.origin.url for git dir at dirPath"""
    r = repo(path)
    if r and r.remotes:
        if any(rr.name == "origin" for rr in r.remotes):
            return r.remotes.origin.url
        else:
            return r.remotes[0].url
    else:
        return None


def commit(path: Optional[Path] = None) -> Optional[str]:
    """Get head commit for git dir at dirPath"""
    r = repo()
    if r is None:
        return None
    try:
        return str(r.head.commit)
    except ValueError:
        # catch case where local git repo without remote master
        return None
