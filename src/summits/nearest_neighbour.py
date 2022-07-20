import numpy as np
from typing import Union, Tuple

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



