import abc
import logging
import time

import requests

logger = logging.getLogger(__name__)


class UrlFetcher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fetch(self, url: str) -> str:
        pass


class RequestsFetcher(UrlFetcher):
    __INSTANCE = None

    def fetch(self, url: str) -> str:
        logger.info(f"Fetching url: '{url}'")
        time.sleep(5)
        return requests.get(url).text

    @classmethod
    def instance(cls):
        if cls.__INSTANCE is None:
            cls.__INSTANCE = RequestsFetcher()
        return cls.__INSTANCE
