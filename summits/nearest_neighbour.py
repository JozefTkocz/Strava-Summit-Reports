import numpy as np
import pandas as pd
from typing import Union, List, Tuple

from models.coordinates import CoordinateSet

EARTH_RADIUS = 6371.


def haversine_distance(lon1: Union[np.array, float],
                       lat1: Union[np.array, float],
                       lon2: Union[np.array, float],
                       lat2: Union[np.array, float]) -> Union[np.array, float]:
    """
    Calculate the great circle distance between two points on the earth (coordinates specified in radians). See
    here for further details: https://en.wikipedia.org/wiki/Haversine_formula

    :param lon1: longitude coordinate of point 1
    :param lat1: latitude coordinate of point 1
    :param lon2: longitude coordinate of point 2
    :param lat2: latitude coordinate of point 2
    :return: great circle distance between point 1 and point 2 in metres.
    """
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.square(np.sin(0.5 * dlat)) + np.cos(lat1) * np.cos(lat2) * np.square(np.sin(0.5 * dlon))
    c = 2 * np.arcsin(np.sqrt(a))
    return c * EARTH_RADIUS * 1000.


def nearest_neighbour_search(coordinates: CoordinateSet, reference_points: CoordinateSet) -> Tuple[np.array, np.array]:
    """
    For each coordinate in coordinates, find the closest coordinate from reference points.

    :param coordinates: CoordinateSet of input coordinates
    :param reference_points: CoordinateSet defining the search space for nearest neighbours to the coordinates argument
    :return: tuple containing the distances to the nearest neighbours, and the indices of the nearest neighbours
    """
    coords_rad = CoordinateSet(latitude=np.radians(coordinates.latitude),
                               longitude=np.radians(coordinates.longitude))

    refs_rad = CoordinateSet(latitude=np.radians(reference_points.latitude),
                             longitude=np.radians(reference_points.longitude))

    coord_latitude, ref_latitude = np.meshgrid(coords_rad.latitude, refs_rad.latitude, sparse=True)
    coord_longitude, ref_longitude = np.meshgrid(coords_rad.longitude, refs_rad.longitude, sparse=True)

    distance_matrix = haversine_distance(ref_longitude, ref_latitude, coord_longitude, coord_latitude)

    minimum_indices = np.argmin(distance_matrix, axis=0)
    distances = distance_matrix[minimum_indices, range(coordinates.length)]

    return distances, minimum_indices


def filter_visited_summits(db, peaks, distance_proximity=20):
    candidate_hills = get_hills_within_altitude_profile(db, peaks)
    candidate_hills = get_hills_within_latlng_grid(peaks=peaks, candidate_hills=candidate_hills, threshold_deg=0.1)
    nearest_hill_distance, nearest_hill_index = find_nearest_summits(peaks, candidate_hills)
    peaks.loc[:, 'named_hill_closest_distance'] = nearest_hill_distance
    peaks.loc[:, 'named_hill_index'] = nearest_hill_index
    hills_to_report = filter_visited_summits_by_proximity(peaks, distance_proximity)
    hill_report_data = candidate_hills.iloc[hills_to_report]
    return hill_report_data


def filter_visited_summits_by_proximity(peaks, threshold_distance=10):
    closest_points = pd.DataFrame(peaks.groupby('named_hill_index')['named_hill_closest_distance'].min())
    closest_points['is_within_threshold'] = closest_points['named_hill_closest_distance'] < threshold_distance
    # Pull out data for those visited hills
    hills_to_report = closest_points.loc[closest_points['is_within_threshold']].index
    return hills_to_report
