import datetime
from collections import namedtuple

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

Event = namedtuple("Event", ["id", "title", "location", "datetime", "price", "url"])


def event_to_dict(event: Event) -> dict:
    res = dict(zip(event._fields, event))
    res['datetime'] = res['datetime'].strftime(_DATETIME_FORMAT)
    return res


def event_from_dict(values: dict) -> Event:
    values = dict(values)
    values['datetime'] = datetime.datetime.strptime(values['datetime'], _DATETIME_FORMAT)
    return Event(**values)
