import abc
import logging
from typing import List

from musiquitax.event import Event

logger = logging.getLogger(__name__)


class EventSource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_event_ids(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_events(self, event_id: str) -> List[Event]:
        pass
