#!/usr/bin/env python3

__name__ = "bento-cli"
__author__ = "Return To Corporation"
R2C_SUPPORT_EMAIL = "support@r2c.dev"

try:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("bento-cli").version
except:  # noqa: E722
    __version__ = "0.0.0+unknown"
