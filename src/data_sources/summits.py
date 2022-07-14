import os.path
from typing import Protocol, Tuple

import pandas as pd


class SummitReference(Protocol):
    altitude_column: str
    latitude_column: str
    longitude_column: str

    def load(self,
             latitude_window: Tuple[float, float] = None,
             longitude_window: Tuple[float, float] = None) -> pd.DataFrame:
        pass


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


if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))
    data = LocalFileSummitReference(os.path.join(current_path, 'database.pkl'))
    df = data.load()
    df.to_csv('hills.csv')
