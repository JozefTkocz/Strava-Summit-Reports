from src.models.coordinates import CoordinateSet
import pytest
import numpy as np


def test_coordinate_set_raises_value_error_if_coordinates_not_same_length():
    with pytest.raises(AssertionError):
        coords = CoordinateSet(longitude=np.array([1, 2]), latitude=np.array([1]))


def test_coordinate_set_doesnt_raise_with_inputs_of_same_length():
    coords = CoordinateSet(longitude=np.array([1, 2]), latitude=np.array([1, 2]))


def test_coordinate_set_index():
    coords = CoordinateSet(latitude=np.array([3, 4]), longitude=np.array([1, 2]))
    expected_result = (4, 2)
    calculated_result = coords.index(1)
    assert expected_result == calculated_result


def test_coordinate_set_index_raises_index_error_when_index_exceeds_array_length():
    coords = CoordinateSet(latitude=np.array([3, 4]), longitude=np.array([1, 2]))
    with pytest.raises(IndexError):
        calculated_result = coords.index(2)


def test_coordinate_set_length():
    coords = CoordinateSet(latitude=np.array([3, 4]), longitude=np.array([1, 2]))
    expected_result = 2
    calculated_result = coords.length
    assert calculated_result == expected_result
