import os
import shutil
from pathlib import Path, PurePath
from typing import List, Optional, Type

import bento.constants as constants
from bento.extra.base_sgrep import BaseSgrepParser, BaseSgrepTool
from bento.parser import Parser


class SgrepParser(BaseSgrepParser):
    @classmethod
    def tool_id(cls) -> str:
        return SgrepTool.TOOL_ID


class SgrepTool(BaseSgrepTool):
    CONFIG_PATH = PurePath("sgrep.yml")
    CONFIG_ENV: str = "BENTO_REGISTRY"
    REGISTRY_ROOT: str = "https://sgrep.live/c/"
    PARSER = SgrepParser
    TOOL_ID = "sgrep"

    @classmethod
    def tool_id(cls) -> str:
        return cls.TOOL_ID

    def can_use_cache(self) -> bool:
        return self.CONFIG_ENV not in os.environ

    def get_config_path(self) -> Optional[Path]:
        if self.CONFIG_ENV not in os.environ:
            return self.context.resource_path / self.CONFIG_PATH
        else:
            return None

    def extra_cache_paths(self) -> List[Path]:
        cp = self.get_config_path()
        return [cp.resolve()] if cp else []

    @property
    def config_str(self) -> str:
        """
        Returns the configuration argument and optional path to pass to sgrep


        If the config environment variable is set, uses that value verbatim.

        Otherwise, ensures that the default config file exists and uses that location.
        """
        config_path = self.get_config_path()
        if config_path is None:
            return self.REGISTRY_ROOT + os.environ[self.CONFIG_ENV]

        if not config_path.exists():
            os.makedirs(self.base_path / constants.RESOURCE_PATH, exist_ok=True)
            template = (
                Path(os.path.dirname(__file__)).parent / "configs" / self.CONFIG_PATH
            )
            shutil.copy(template, config_path)
        return str(constants.RESOURCE_PATH / self.CONFIG_PATH)

    @property
    def parser_type(self) -> Type[Parser]:
        return self.PARSER
