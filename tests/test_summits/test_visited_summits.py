import pandas as pd
import numpy as np

from data_sources.summits import LocalFileSummitReference
from summits.visited_summits import find_visited_summits
from models.coordinates import CoordinateSet

from unittest.mock import MagicMock


def test_visited_summits_with_one_visited_summit():
    mock_summit_database = pd.DataFrame({'Latitude': [0., 10., 20.],
                                         'Longitude': [0., 0., 0.],
                                         'Name': ['A', 'B', 'C']})

    mock_summit_reference = LocalFileSummitReference('mock_filepath.pkl')
    mock_summit_reference._load_from_file = MagicMock(return_value=mock_summit_database)

    # each step of 1e-5 is approx. 1.11 m of distance
    gpx_coords = CoordinateSet(latitude=np.array([0., 1e-5, 2e-5]), longitude=np.array([0., 0., 0.]))

    expected_result = pd.DataFrame({'Latitude': [0.],
                                    'Longitude': [0.],
                                    'Name': ['A']})
    calculated_result = find_visited_summits(gpx_trail=gpx_coords,
                                             summit_reference_data=mock_summit_reference,
                                             distance_proximity=10)

    pd.testing.assert_frame_equal(expected_result, calculated_result)


def test_visited_summits_with_multiple_visited_summits():
    mock_summit_database = pd.DataFrame({'Latitude': [0., 10., 20.],
                                         'Longitude': [0., 0., 0.],
                                         'Name': ['A', 'B', 'C']})

    mock_summit_reference = LocalFileSummitReference('mock_filepath.pkl')
    mock_summit_reference._load_from_file = MagicMock(return_value=mock_summit_database)

    # each step of 1e-5 is approx. 1.11 m of distance
    gpx_coords = CoordinateSet(latitude=np.array([0., 10.00001, 20.00001]), longitude=np.array([0., 0., 0.]))

    expected_result = pd.DataFrame({'Latitude': [0., 10., 20.],
                                    'Longitude': [0., 0., 0.],
                                    'Name': ['A', 'B', 'C']})
    calculated_result = find_visited_summits(gpx_trail=gpx_coords,
                                             summit_reference_data=mock_summit_reference,
                                             distance_proximity=10)

    pd.testing.assert_frame_equal(expected_result, calculated_result)


def test_visited_summits_with_no_visited_summits():
    mock_summit_database = pd.DataFrame({'Latitude': [0., 10., 20.],
                                         'Longitude': [0., 0., 0.],
                                         'Name': ['A', 'B', 'C']})

    mock_summit_reference = LocalFileSummitReference('mock_filepath.pkl')
    mock_summit_reference._load_from_file = MagicMock(return_value=mock_summit_database)

    # each step of 1e-5 is approx. 1.11 m of distance
    gpx_coords = CoordinateSet(latitude=np.array([30., 30., 30.]), longitude=np.array([0., 0., 0.]))

    expected_result = pd.DataFrame({'Latitude': [],
                                    'Longitude': [],
                                    'Name': []})
    calculated_result = find_visited_summits(gpx_trail=gpx_coords,
                                             summit_reference_data=mock_summit_reference,
                                             distance_proximity=10)

    pd.testing.assert_frame_equal(expected_result, calculated_result, check_dtype=False)
