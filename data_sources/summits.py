from typing import Protocol, Tuple

import pandas as pd


class SummitReference(Protocol):
    def load(self, latitude_window: Tuple[float, float], longitude_window: Tuple[float, float]) -> pd.DataFrame:
        ...


class LocalFileSummitReference:
    altitude_column = 'Metres'
    latitude_column = 'Latitude'
    longitude_column = 'Longitude'

    def __init__(self, filepath):
        self.filepath = filepath

    def load(self,
             latitude_window: Tuple[float, float] = None,
             longitude_window: Tuple[float, float] = None) -> pd.DataFrame:
        df = self._load_from_file()

        if latitude_window is not None:
            df = df.loc[(df[self.latitude_column] >= latitude_window[0]) &
                        (df[self.latitude_column] <= latitude_window[1])]

        if longitude_window is not None:
            df = df.loc[(df[self.longitude_column] >= longitude_window[0]) &
                        (df[self.longitude_column] <= longitude_window[1])]
        return df.reset_index(drop=True)

    def _load_from_file(self):
        df = pd.read_pickle(self.filepath)
        return df
