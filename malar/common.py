from enum import Enum


class Sector(Enum):
    SE1 = 1
    SE2 = 2
    SE3 = 3
    SE4 = 4

    def __str__(self) -> str:
        return self.name
