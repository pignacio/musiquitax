import datetime
import logging
import re
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from musiquitax.event import Event
from musiquitax.event.source import EventSource
from musiquitax.network import UrlFetcher, RequestsFetcher

logger = logging.getLogger(__name__)

_EVENT_RE = r"Entrada:\s*\$\s*(?P<price>[\d.,]+)\s*.*?(?P<time>\d\d:\d\d)\s*hs\s*-\s*(?P<date>\d\d/\d\d/\d\d\d\d)"


class AlternativaTeatral(EventSource):
    def __init__(self, base_url: str, fetcher: UrlFetcher = RequestsFetcher.instance()):
        self.__base_url = base_url
        self.__fetcher = fetcher

    def get_event_ids(self) -> List[str]:
        soup = BeautifulSoup(self.__fetcher.fetch(self.__base_url), features="html.parser")
        events = soup.find_all("td", {"class": "celdatitulo"})
        return [self.__extract_event_id(e) for e in events]

    def get_events(self, event_id: str) -> List[Event]:
        url = urljoin(self.__base_url, event_id)
        data = self.__fetcher.fetch(url)
        soup = BeautifulSoup(data, features="html.parser")
        venue_tag = soup.find("div", {"class": "teatro"})
        venue_name = venue_tag.find("span", {"itemprop": "location"}).find("span", {"itemprop": "name"}).text
        title = soup.find(id="izquierda").h1.text
        matches = re.finditer(_EVENT_RE, venue_tag.text)

        return [Event(
            id=f"{event_id}.{index}",
            title=title,
            location=venue_name,
            datetime=self._get_datetime(match),
            price=float(match.group("price").replace(",", ".")),
            url=url,
        ) for index, match in enumerate(matches)]

    @staticmethod
    def __extract_event_id(event_tag: Tag) -> str:
        event_id = event_tag.a['href']
        logger.debug(f"Found event in page: {event_id}: {event_tag.text}")
        return event_id

    @staticmethod
    def _get_datetime(match):
        # TODO: ugly
        as_str = match.group("date") + " " + match.group("time")
        return datetime.datetime.strptime(as_str, "%d/%m/%Y %H:%M")
