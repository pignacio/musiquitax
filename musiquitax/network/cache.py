import collections
import logging
import sqlite3
import time
from typing import Optional

from ..network import UrlFetcher

logger = logging.getLogger(__name__)

_ONE_WEEK_IN_MS = 7 * 24 * 60 * 60 * 1000

DatedContents = collections.namedtuple("DatedContent", ["contents", "date"])


class CachedFetcher(UrlFetcher):
    def __init__(self, delegate: UrlFetcher, db_file: str = ".fetcher_cache"):
        self.__delegate = delegate
        self.__conn = sqlite3.connect(db_file)
        self._sync_table()

    def fetch(self, url: str) -> str:
        cached = self._get_page_and_date(url)
        if cached is None or self._should_reload(cached):
            contents = self.__delegate.fetch(url)
            self._save_page(url, contents)
            return contents
        else:
            return cached.contents

    def _get_page_and_date(self, url: str) -> Optional[DatedContents]:
        with self.__conn:
            res = self.__conn.execute("SELECT contents, date FROM fetcher_cache WHERE url = ?", (url,)).fetchone()
            if res is not None:
                return DatedContents(res[0], res[1])
        return None

    def _save_page(self, url: str, contents: str):
        with self.__conn:
            self.__conn.execute("DELETE FROM fetcher_cache WHERE url = ?", (url,))
            self.__conn.execute("INSERT INTO fetcher_cache VALUES (?, ?, ?)", (url, contents, self._current_time()))

    def _sync_table(self):
        logger.info("Syncing CachedFetcher table")
        with self.__conn:
            self.__conn.execute(
                "CREATE TABLE IF NOT EXISTS fetcher_cache ("
                "  url VARCHAR(512) PRIMARY KEY, "
                "  contents TEXT NOT NULL, "
                "  date BIGINT NOT NULL"
                ")"
            )

    def _should_reload(self, cached: DatedContents) -> bool:
        return self._current_time() - cached.date > _ONE_WEEK_IN_MS

    @staticmethod
    def _current_time() -> int:
        return int(time.time() * 1000)
