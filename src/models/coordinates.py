from dataclasses import dataclass
import numpy as np
from typing import Tuple


@dataclass
class CoordinateSet:
    latitude: np.array
    longitude: np.array

    def __post_init__(self):
        self._validate_coordinates()

    def _validate_coordinates(self):
        assert len(self.latitude) == len(self.longitude)

    def index(self, index: int) -> Tuple:
        """
        Return the latitude and longitude coordinates for a specified index

        :param index: desired coordinate index
        :return: tuple containing the latitude and longitude values at the given index
        """
        return self.latitude[index], self.longitude[index]

    @property
    def length(self):
        return len(self.latitude)
