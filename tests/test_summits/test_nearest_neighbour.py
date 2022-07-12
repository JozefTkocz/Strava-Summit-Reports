from summits.nearest_neighbour import haversine_distance, EARTH_RADIUS, nearest_neighbour_search
import pytest
import numpy as np

from models.coordinates import CoordinateSet


@pytest.mark.parametrize("coordinate, expected_result", [((0, 0), 0.), ((0.5, 0.5), 0.), ((1.0, 1.0), 0.)])
def test_haversine_distance_between_identical_points_is_zero(coordinate, expected_result):
    lat1, lng1 = coordinate
    lat2, lng2 = coordinate
    calculated_result = haversine_distance(lon1=lng1, lat1=lat1, lon2=lng2, lat2=lat2)
    np.testing.assert_almost_equal(calculated_result, expected_result)


def test_haversine_distance_between_antipodal_points():
    lat1, lng1 = (0.5 * np.pi, 0.)
    lat2, lng2 = (-0.5 * np.pi, 0.)
    expected_result = np.pi * EARTH_RADIUS * 1.0e3  # half the circumference of the cross-section of a sphere
    calculated_result = haversine_distance(lon1=lng1, lat1=lat1, lon2=lng2, lat2=lat2)
    np.testing.assert_almost_equal(calculated_result, expected_result)


def test_nearest_neighbour_search():
    coords = CoordinateSet(latitude=np.array([1., 50., 75.]), longitude=np.array([0., 0., 0.]))
    reference_set = CoordinateSet(latitude=np.array([75., 50., 1.]), longitude=np.array([0., 0., 0.]))

    expected_result_distance, expected_result_index = np.array([0., 0., 0.]), np.array([2, 1, 0])
    actual_result_distance, actual_result_index = nearest_neighbour_search(coordinates=coords,
                                                                           reference_points=reference_set)

    np.testing.assert_almost_equal(expected_result_distance, actual_result_distance)
    np.testing.assert_almost_equal(expected_result_index, actual_result_index)
