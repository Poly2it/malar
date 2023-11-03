from enum import Enum, auto


class Sector(Enum):
    SE1 = 1
    SE2 = 2
    SE3 = 3
    SE4 = 4


class Service(Enum):
    WATER = auto()
    DISTRICT_HEATING = auto()
    ELECTRICITY = auto()


class Status(Enum):
    NOMINAL = auto()
    UNDER_INVESTIGATION = auto()
    UNDER_SERVICE = auto()

