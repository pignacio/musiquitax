import datetime
import json
import logging
from typing import List, Dict
from urllib.parse import urlparse

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
        events = [self._parse_event(d) for d in json.loads(contents)]
        return {e.id: e for e in events}

    def _parse_event(self, data: dict) -> Event:
        domain = urlparse(self.__base_url).netloc
        return Event(
            id=f"""{domain}:::{data["id"]}""",
            title=data["nombre"],
            location=data["complejo"],
            datetime=self._get_datetime(data["fecha"]),
            price=float(data["importe"]),
            url=f"""https://{domain}/{data["categoriaSlug"]}/{data["eventoSlug"]}""",
        )

    @staticmethod
    def _get_datetime(pretty_date: str):
        spl = pretty_date.split()
        day = int(spl[1])
        month = _MONTH_NAME_TO_NUMBER[spl[3].lower()]
        time = datetime.datetime.strptime(spl[4], "%H:%M").time()
        return datetime.datetime.combine(datetime.date(2019, month, day), time)

