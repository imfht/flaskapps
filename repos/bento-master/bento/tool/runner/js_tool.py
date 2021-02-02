import json
import logging
import subprocess
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Optional, Set

import attr
from semantic_version import NpmSpec, Version

from bento.error import NodeError
from bento.tool.tool import Tool

NODE_VERSION_RANGE = NpmSpec("^8.10.0 || ^10.13.0 || >=11.10.1")

VersionDict = Dict[str, Version]


@attr.s(auto_attribs=True)
class NpmDeps:
    """Represents top-level npm package dependencies for a project"""

    main: Dict[str, NpmSpec]
    dev: Dict[str, NpmSpec]

    def __contains__(self, item: str) -> bool:
        return item in self.main or item in self.dev


class JsTool(Tool):
    @property
    @abstractmethod
    def install_location(self) -> Path:
        pass

    def _dependencies(self, location: Path) -> NpmDeps:
        """
        Returns an inventory of all top-level dependencies (not necessarily installed)

        :return: The dependencies, with versions
        """
        package_json_path = location / "package.json"
        with package_json_path.open() as stream:
            packages = json.load(stream)

        return NpmDeps(
            packages.get("dependencies", {}), packages.get("devDependencies", {})
        )

    def _installed_version(self, package: str, location: Path) -> Optional[Version]:
        """
        Gets the version of a package that was installed.

        Returns None if that package has not been installed.
        """
        package_json_path = location / "node_modules" / package / "package.json"
        try:
            with package_json_path.open() as f:
                package_json = json.load(f)
        except FileNotFoundError:
            return None
        if "version" in package_json:
            return Version(package_json["version"])
        else:
            return None

    def _npm_install(self, packages: VersionDict) -> None:
        """Runs npm install $package@^$version for each package."""
        logging.info(f"Installing {packages}...")
        args = [f"{name}@^{version}" for name, version in packages.items()]
        cmd = ["npm", "install", "--save-dev"]
        result = self.execute(
            cmd + args,
            cwd=self.install_location,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logging.info(result.stdout)
        logging.info(result.stderr)

    def _ensure_packages(self, packages: VersionDict) -> Set[str]:
        """Ensures that the given packages are installed.

        Returns the list of all packages that were installed.

        The argument maps package names to the minimum version. This is morally
        equivalent to a plain `npm install --save`, except it's faster in the
        case where all the packages are already installed.
        """
        to_install = {}
        for name, required_version in packages.items():
            installed = self._installed_version(name, location=self.install_location)
            if not (installed and installed >= required_version):
                to_install[name] = required_version
        if not to_install:
            return set()

        self._npm_install(to_install)
        return set(to_install)

    def _ensure_node_version(self) -> None:
        """Ensures that Node.js version installed on the system is compatible with ESLint v6
        per https://github.com/eslint/eslint/blob/master/docs/user-guide/migrating-to-6.0.0.md#-nodejs-6-is-no-longer-supported
        Suppored Node.js version  ^8.10.0 || ^10.13.0 || >=11.10.1
        """
        version = self.execute(
            ["node", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        node_version = version.stdout.rstrip().strip("v")
        if version.returncode > 0 or not NODE_VERSION_RANGE.match(
            Version(node_version)
        ):
            raise NodeError(
                f"Node.js is not installed, or its version is not >8.10.0, >10.13.0, or >=11.10.1 (found {node_version})."
            )
