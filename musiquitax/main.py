import json
import logging
import sys

from musiquitax.event import event_to_dict, event_from_dict
from musiquitax.event.source.alternativa_teatral import AlternativaTeatral
from musiquitax.event.source.ticket_hoy import TicketHoy
from musiquitax.network import RequestsFetcher
from musiquitax.network.cache import CachedFetcher

logger = logging.getLogger(__name__)

_VINILO_URL = "http://www.alternativateatral.com/espacio2531-cafe-vinilo"
_DATABASE_FILE = "data.json"


def load_data():
    try:
        with open(_DATABASE_FILE) as fin:
            return json.load(fin)
    except FileNotFoundError:
        return {}


def save_data(data):
    with open(_DATABASE_FILE, "w") as fout:
        json.dump(data, fout, indent=1, sort_keys=True)


def main():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    data = load_data()

    source = AlternativaTeatral("http://www.alternativateatral.com/espacio2531-cafe-vinilo",
                                fetcher=CachedFetcher(RequestsFetcher.instance()))
    source = TicketHoy("https://bue.tickethoy.com/search-home?categoria=&lugar=559&dia=&fechar_orden=true",
                       fetcher=CachedFetcher(RequestsFetcher.instance()))
    try:
        for event_id in source.get_event_ids():
            if event_id in data:
                logger.info(f"Event '{event_id}' is present in the data. Not re-fetching")
            else:
                logger.info(f"Updating data for '{event_id}'")
                events = source.get_events(event_id)
                logger.info(f"Found {len(events)} events for '{event_id}'")
                data[event_id] = [event_to_dict(e) for e in events]
    finally:
        save_data(data)
        events = [event_from_dict(x) for y in data.values() for x in y]
        for event in sorted(events, key=lambda e: e.datetime):
            print(f"{event.title}\t{event.datetime}\t{event.location}\t{event.price}\t{event.url}")


if __name__ == "__main__":
    main()
