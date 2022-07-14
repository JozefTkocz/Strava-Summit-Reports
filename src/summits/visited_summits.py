import numpy as np
import pandas as pd
from typing import Union
from summits.nearest_neighbour import nearest_neighbour_search
from data_sources.summits import SummitReference
from models.coordinates import CoordinateSet


def find_visited_summits(summit_reference_data: SummitReference,
                         gpx_trail: CoordinateSet,
                         distance_proximity: float = 20,
                         search_window_width: Union[float, None] = 0.1) -> pd.DataFrame:
    """
    Given a GPX trail, extract from the reference data source all entries corresponding to summits that were visited,
    where a visit is an approach within distance_proximity of the summit location.

    :param summit_reference_data: Reference data source defining the summit information
    :param gpx_trail: CoordinateSet corresponding to a GPX trail
    :param distance_proximity: maximum approach distance in metres required to qualify a visit to a summit
    :param search_window_width: A margin in decimal degrees applied around the extent of the gpx_trail coordinates, used
    to reduce the summit search area. If None, the whole of the reference dataset is searched for visited summits.
    :return: pd.DataFrame loaded from summit reference, corresponding to the visited summits only.
    """

    candidate_summits = trim_search_area(summit_reference_data=summit_reference_data,
                                         gpx_trail=gpx_trail,
                                         search_window_width=search_window_width)
    if not len(candidate_summits):
        return candidate_summits

    candidate_summit_coords = CoordinateSet(longitude=candidate_summits[summit_reference_data.longitude_column],
                                            latitude=candidate_summits[summit_reference_data.latitude_column])

    nearest_hill_distance, nearest_hill_index = nearest_neighbour_search(coordinates=gpx_trail,
                                                                         reference_points=candidate_summit_coords)
    gpx_data = pd.DataFrame({'Latitude': gpx_trail.latitude,
                             'Longitude': gpx_trail.longitude})

    gpx_data['nearest_hill_index'] = nearest_hill_index
    gpx_data['nearest_hill_distance'] = nearest_hill_distance
    gpx_data = gpx_data.loc[gpx_data['nearest_hill_distance'] < distance_proximity]
    return candidate_summits.iloc[gpx_data['nearest_hill_index']].drop_duplicates()


def trim_search_area(summit_reference_data: SummitReference,
                     gpx_trail: CoordinateSet,
                     search_window_width: Union[float, None]) -> pd.DataFrame:
    """
    Reduce the search space by filtering the summit reference dataset to a region of interest only.

    :param gpx_trail: GPX coordinates used to define the region of interest
    :param summit_reference_data: SummitReference datasource to be filtered
    :param search_window_width: value in decimal degrees defining the margin to be applied around the GPX trail to
    filter out summits that could not have been visited. If None, all summits are retained as candidates.
    :return: pd.DataFrame loaded from the summit reference source, filtered to the search area of interest only.
    """
    lat_max, lat_min = np.amax(gpx_trail.latitude), np.amin(gpx_trail.latitude)
    lng_max, lng_min = np.amax(gpx_trail.longitude), np.amin(gpx_trail.longitude)
    lng_window = lng_min - search_window_width, lng_max + search_window_width
    lat_window = lat_min - search_window_width, lat_max + search_window_width
    candidate_summits = summit_reference_data.load(latitude_window=lat_window,
                                                   longitude_window=lng_window)
    return candidate_summits
