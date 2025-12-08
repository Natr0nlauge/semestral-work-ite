import json
import numpy as np
import pytest
from src import IoMatrix


# -----------------------------
# BASIC FUNCTIONALITY TESTS
# -----------------------------

def test_json_vector_basic():
    arr = np.array([1.2345, 2.3456, 3.4567])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [1.23, 2.35, 3.46]


def test_json_matrix_basic():
    arr = np.array([[1.2345, 2.3456], [3.4567, 4.5678]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[1.23, 2.35], [3.46, 4.57]]


# -----------------------------
# EDGE CASES
# -----------------------------

def test_json_empty_vector():
    arr = np.array([])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == []


def test_json_empty_matrix():
    arr = np.array([[]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[]]


def test_json_single_element_vector():
    arr = np.array([42])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [42]


def test_json_single_element_matrix():
    arr = np.array([[7]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[7]]


def test_json_negative_numbers():
    arr = np.array([[-1, -2.5]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[-1.0, -2.5]]


def test_json_large_and_small_values():
    arr = np.array([[1e10, 5e-12]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[1e10, 5e-12]]


def test_json_integer_array():
    arr = np.array([[1, 2], [3, 4]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[1, 2], [3, 4]]


def test_json_nan_inf_values():
    arr = np.array([np.nan, np.inf, -np.inf])
    io = IoMatrix(arr)

    result = json.loads(io.numpy_to_json())

    assert np.isnan(result[0])
    assert result[1] == float("inf")
    assert result[2] == float("-inf")


# -----------------------------
# FORMAT TESTS
# -----------------------------

def test_json_custom_format():
    arr = np.array([1.2345])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json(fmt="{:.2f}"))
    assert result == [1.23]


def test_json_indent_applied():
    arr = np.array([1])
    io = IoMatrix(arr)
    out = io.numpy_to_json(indent=4)
    assert "\n    " in out  # JSON pretty-print indentation


def test_json_invalid_format_raises():
    arr = np.array([1.23])
    io = IoMatrix(arr)
    with pytest.raises(Exception):
        io.numpy_to_json(fmt="{:.2Z}")  # invalid format specifier


# -----------------------------
# ERROR CONDITION TESTS
# -----------------------------

def test_json_3d_array_raises():
    arr = np.zeros((2, 2, 2))
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        io.numpy_to_json()


def test_json_non_numeric_array_raises():
    arr = np.array([["a", "b"]])
    io = IoMatrix(arr)
    # string formatting is fine, but conversion to float fails → ValueError
    with pytest.raises(ValueError):
        json.loads(io.numpy_to_json())


def test_json_invalid_input_type():
    with pytest.raises(AttributeError):
        IoMatrix("hello").numpy_to_json()


def test_json_inconsistent_row_lengths():
    arr = np.array([[1, 2], [3]], dtype=object)  # jagged array
    io = IoMatrix(arr)
    with pytest.raises(Exception):
        io.numpy_to_json()
