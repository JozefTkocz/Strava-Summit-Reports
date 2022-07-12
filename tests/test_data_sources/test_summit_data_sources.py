import pandas as pd

from data_sources.summits import LocalFileSummitReference
from unittest.mock import MagicMock


def test_local_file_summit_reference_returns_full_dataset_when_no_filter():
    data_source = LocalFileSummitReference('mock_filename.pkl')
    mock_dataset = pd.DataFrame({'Latitude': [1, 2, 3, 4, 5],
                                 'Longitude': [6, 7, 8, 9, 10]})
    data_source._load_from_file = MagicMock(return_value=mock_dataset)

    expected_result = mock_dataset.copy()
    actual_result = data_source.load()

    pd.testing.assert_frame_equal(expected_result, actual_result)


def test_local_file_summit_reference_filters_dataset():
    data_source = LocalFileSummitReference('mock_filename.pkl')
    mock_dataset = pd.DataFrame({'Latitude': [1, 2, 3, 4, 5],
                                 'Longitude': [6, 7, 8, 9, 10]})
    data_source._load_from_file = MagicMock(return_value=mock_dataset)

    expected_result = pd.DataFrame({'Latitude': [2, 3, 4],
                                    'Longitude': [7, 8, 9]})
    actual_result = data_source.load(latitude_window=(2, 4))

    pd.testing.assert_frame_equal(expected_result, actual_result)
