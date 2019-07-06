import datetime
import json
import logging
import re
from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from musiquitax.event import Event
from musiquitax.event.source import EventSource
from musiquitax.network import UrlFetcher, RequestsFetcher

logger = logging.getLogger(__name__)

_EVENT_RE = r"Entrada:\s*\$\s*(?P<price>[\d.,]+)\s*.*?(?P<time>\d\d:\d\d)\s*hs\s*-\s*(?P<date>\d\d/\d\d/\d\d\d\d)"

_MONTH_NAME_TO_NUMBER = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12,
}


class TicketHoy(EventSource):
    def __init__(self, base_url: str, fetcher: UrlFetcher = RequestsFetcher.instance()):
        self.__base_url = base_url
        self.__events = self._parse_events(fetcher.fetch(base_url))

    def get_event_ids(self) -> List[str]:
        return list(self.__events.keys())

    def get_events(self, event_id: str) -> List[Event]:
        return [self.__events[event_id]]

    def _parse_events(self, contents: str) -> Dict[str, Event]:
        events = json.loads(contents)
        return {e["id"]: Event(
            id=str(e["id"]),
            title=e["nombre"],
            location=e["complejo"],
            datetime=self._get_datetime(e["fecha"]),
            price=float(e["importe"]),
            url=f"""https://bue.tickethoy.com/{e["categoriaSlug"]}/{e["eventoSlug"]}""",
        ) for e in events}

    @staticmethod
    def _get_datetime(pretty_date: str):
        spl = pretty_date.split()
        day = int(spl[1])
        month = _MONTH_NAME_TO_NUMBER[spl[3].lower()]
        time = datetime.datetime.strptime(spl[4], "%H:%M").time()
        return datetime.datetime.combine(datetime.date(2019, month, day), time)

