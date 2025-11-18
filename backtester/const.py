from enum import Enum
from collections import namedtuple

class OrderSide(Enum):
    LONG = 'long'
    SHORT = 'short'


class LevelHit(Enum):
    TARGET = 'target'
    STOP = 'stop'
    NOHIT = 'nohit'

bardata = namedtuple('bardata', ['open', 'high', 'low', 'close', 'timestamp', 'day_index'])