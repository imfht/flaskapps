import json
import logging
import os
import re
import subprocess
import sys
import venv
from abc import abstractmethod
from pathlib import Path
from time import time
from typing import Dict, Generic, Iterable, List, Optional, Pattern

from semantic_version import SimpleSpec, Version

import bento.constants as constants
from bento.tool.tool import R, Tool


class PythonTool(Generic[R], Tool[R]):
    # On most environments, just "pip" will point to the wrong Python installation
    # Fix by using the virtual environment's python3
    # we hard code to python3
    PIP_CMD = ["python3", "-m", "pip"]
    PACKAGES: Dict[str, SimpleSpec] = {}
    PYTHON_FILE_PATTERN = re.compile(r".*\.py$")
    SHEBANG_PATTERN = re.compile(r"^#!.*python")

    @property
    def shebang_pattern(self) -> Optional[Pattern]:
        return self.SHEBANG_PATTERN

    def matches_project(self, files: Iterable[Path]) -> bool:
        return self.project_has_file_paths(files)

    @property
    def file_name_filter(self) -> Pattern:
        return self.PYTHON_FILE_PATTERN

    @classmethod
    @abstractmethod
    def venv_subdir_name(cls) -> str:
        pass

    @classmethod
    def required_packages(cls) -> Dict[str, SimpleSpec]:
        return cls.PACKAGES

    @classmethod
    def venv_dir(cls) -> Path:
        return constants.VENV_PATH / cls.venv_subdir_name()

    def venv_create(self) -> None:
        """
        Creates a virtual environment for this tool
        """
        if not self.venv_dir().exists():
            logging.info(f"Creating virtual environment for {self.tool_id()}")
            # If we are already in a virtual environment, venv.create() will fail to install pip,
            # but we probably have virtualenv in the path, so try that first.
            try:
                # Don't litter stdout with virtualenv spam
                # Create virtualenv using same version as currently running executable
                subprocess.run(
                    ["virtualenv", f"--python={sys.executable}", self.venv_dir()],
                    stdout=subprocess.DEVNULL,
                    check=True,
                )
            except Exception:
                venv.create(str(self.venv_dir()), with_pip=True)

    def venv_exec(self, cmd: List[str], check_output: bool = True) -> str:
        """
        Executes tool set-up or check within its virtual environment
        """
        logging.debug(f"{self.tool_id()}: Running '{cmd}'")
        before = time()
        env = dict(os.environ)
        env["VIRTUAL_ENV"] = str(self.venv_dir())
        env["PATH"] = f"{self.venv_dir()}:{self.venv_dir()}/bin:" + env["PATH"]
        if "PYTHONHOME" in env:
            del env["PYTHONHOME"]
        v = subprocess.Popen(
            cmd,
            cwd=str(self.base_path),
            encoding="utf8",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = v.communicate()
        after = time()
        logging.debug(f"{self.tool_id()}: Command completed in {after - before:2f} s")
        logging.debug(f"{self.tool_id()}: stderr[:4000]:\n" + stderr[0:4000])
        logging.debug(f"{self.tool_id()}: stdout[:4000]:\n" + stdout[0:4000])
        if check_output and v.returncode != 0:
            raise subprocess.CalledProcessError(
                v.returncode, cmd, output=stdout, stderr=stderr
            )
        return stdout

    def _packages_installed(self) -> Dict[str, SimpleSpec]:
        """
        Checks whether the given packages are installed.

        The value for each package is the version specification.
        """
        installed: Dict[str, Version] = {}
        for package in json.loads(
            self.venv_exec([*PythonTool.PIP_CMD, "list", "--format", "json"])
        ):
            try:
                installed[package["name"]] = Version(package["version"])
            except ValueError:
                # skip it
                pass

        to_install: Dict[str, SimpleSpec] = {}
        for name, spec in self.required_packages().items():
            if name not in installed or not spec.match(installed[name]):
                to_install[name] = spec
        return to_install

    def setup(self) -> None:
        self.venv_create()
        to_install = self._packages_installed()
        if not to_install:
            return

        install_list = [f"{p}{s.expression}" for p, s in to_install.items()]
        logging.info(f"Installing Python packages: {', '.join(install_list)}")
        self.venv_exec(
            [*PythonTool.PIP_CMD, "install", "-q", *install_list], check_output=True
        )
