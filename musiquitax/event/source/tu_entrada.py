import datetime
import json
import re
from typing import List, Dict
from urllib.parse import urlparse, urljoin

from musiquitax.event import Event
from musiquitax.event.source import EventSource
from musiquitax.network import RequestsFetcher, UrlFetcher

_HEADERS_RE = r"searchHeaders : (?P<headers>.*]),"
_DATA_RE = r"searchResults : (?P<data>.*?^\s*]),"

_MONTH_NAME_TO_NUMBER = {
    'ene': 1,
    'feb': 2,
    'mar': 3,
    'abr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'ago': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dic': 12,
}


class TuEntrada(EventSource):
    def __init__(self, base_url: str, fetcher: UrlFetcher = RequestsFetcher.instance()):
        self.__base_url = base_url
        self.__events = self._parse_events(fetcher.fetch(base_url))

    def get_event_ids(self) -> List[str]:
        return list(self.__events.keys())

    def get_events(self, event_id: str) -> List[Event]:
        return [self.__events[event_id]]

    def _parse_events(self, contents: str) -> Dict[str, Event]:
        headers = json.loads(re.search(_HEADERS_RE, contents).group("headers"))
        items = json.loads(re.search(_DATA_RE, contents, flags=re.MULTILINE | re.DOTALL).group("data"))
        events = [self._parse_event(dict(zip(headers, d))) for d in items]
        return {e.id: e for e in events}

    def _parse_event(self, data: dict) -> Event:
        domain = urlparse(self.__base_url).netloc
        return Event(
            id=f"""{domain}:::{data["Id"]}""",
            title=data["Performance Short Description"],
            location=data["Venue Name"],
            datetime=self._get_datetime(data["Fecha"]),
            price=self._format_price(data["Minimum Price"], data["Maximum Price"]),
            url=urljoin(self.__base_url, data["Additional Info"]),
        )

    @staticmethod
    def _get_datetime(pretty_date: str):
        spl = pretty_date.split()
        day = int(spl[1])
        month = _MONTH_NAME_TO_NUMBER[spl[3].lower()]
        year = int(spl[4])
        time = datetime.datetime.strptime(spl[5], "%H:%M").time()
        return datetime.datetime.combine(datetime.date(year, month, day), time)

    def _format_price(self, minimum: str, maximum: str) -> str:
        if minimum == maximum:
            return minimum
        else:
            return f"{minimum} - {maximum}"
