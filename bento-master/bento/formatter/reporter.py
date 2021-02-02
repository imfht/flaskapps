import collections
import itertools
import logging
from abc import ABC, abstractmethod
from typing import Any, Collection, Iterator, Mapping, Type

import attr

from bento.constants import RESOURCE_PATH
from bento.formatter.base import FindingsMap, Formatter
from bento.formatter.json import Json
from bento.git import url
from bento.network import no_auth_post


class Serializer(ABC):
    @abstractmethod
    def serialize(
        self, config: Mapping[str, Any], findings: FindingsMap
    ) -> Mapping[str, Any]:
        pass


class Circle(Serializer):
    def serialize(
        self, config: Mapping[str, Any], findings: FindingsMap
    ) -> Mapping[str, Any]:
        return {
            "meta": {"repo_url": url()},
            "config": config,
            "findings": Json.to_py(findings),
        }


SCHEMATA: Mapping[str, Type[Serializer]] = {"circle": Circle}

DEFAULT_TIMEOUT_SECONDS = 2.0


class IterColl(collections.Collection):
    def __init__(self, length: int, *iters: Iterator[str]) -> None:
        self.length = length
        self.iters = iters

    def __contains__(self, __x: object) -> bool:
        return False

    def __iter__(self) -> Iterator[str]:
        return itertools.chain(*self.iters)

    def __len__(self) -> int:
        return self.length


@attr.s
class Reporter(Formatter):
    def inner(self) -> Serializer:
        key: str = self.config.get("schema", "circle")
        if key not in SCHEMATA:
            raise Exception(f"Unknown reporter schema '{key}'")
        return SCHEMATA[key]()

    def url(self) -> str:
        if "url" not in self.config:
            raise Exception(
                f"Config for reporter formatter is missing 'url'. Please add 'url: URL' to the configuration for 'reporter' to {RESOURCE_PATH}"
            )
        return self.config["url"]

    def submit(self, url: str, data: Mapping) -> str:
        try:
            r = no_auth_post(url, json=data, timeout=self.timeout())
            r.raise_for_status()
            return "Successfully submitted report"
        except Exception:
            logging.exception(f"error posting to {url}")
            return "Failed to post report"

    def timeout(self) -> float:
        return self.config.get("timeout", DEFAULT_TIMEOUT_SECONDS)

    def dump(self, findings: FindingsMap) -> Collection[str]:
        blob = self.inner().serialize(self.context.config, findings)
        url = self.url()
        return IterColl(
            2,
            (s for s in [f"Publishing results to {url}..."]),
            (self.submit(url, d) for d in [blob]),
        )
