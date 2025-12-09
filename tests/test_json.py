import json
import numpy as np
import pytest
from src import (
    IoMatrix,
    extract_arrays_from_json_text, 
    extract_arrays_from_json_file,
)


# -----------------------------
# BASIC FUNCTIONALITY TESTS
# -----------------------------

def test_json_vector_basic():
    arr = np.array([1.2345, 2.3456, 3.4567])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[1.23, 2.35, 3.46]]


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
    assert result == [[]]


def test_json_empty_matrix():
    arr = np.array([[]])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[]]


def test_json_single_element_vector():
    arr = np.array([42])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json())
    assert result == [[42]]


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

    assert np.isnan(result[0][0])
    assert result[0][1] == float("inf")
    assert result[0][2] == float("-inf")


# -----------------------------
# FORMAT TESTS
# -----------------------------

def test_json_custom_format():
    arr = np.array([1.2345])
    io = IoMatrix(arr)
    result = json.loads(io.numpy_to_json(fmt="{:.2f}"))
    assert result == [[1.23]]


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


def test_extract_row_vector():
    text = "[[1, 2, 3]]"
    arrays = extract_arrays_from_json_text(text)
    assert len(arrays) == 1
    assert np.array_equal(arrays[0].nparray, np.array([1.0, 2.0, 3.0]))

def test_extract_column_vector():
    text = "[[1], [2], [3]]"
    arrays = extract_arrays_from_json_text(text)
    assert len(arrays) == 1
    assert np.array_equal(arrays[0].nparray, np.array([[1.0], [2.0], [3.0]]))


def test_extract_2d_array():
    text = "[[1, 2], [3, 4]]"
    arrays = extract_arrays_from_json_text(text)
    assert len(arrays) == 1
    assert np.array_equal(arrays[0].nparray, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_extract_multiple_arrays():
    text = """
    [
        [[1, 2, 3]],
        [[4, 5], [6, 7]]
    ]
    """
    arrays = extract_arrays_from_json_text(text)

    assert len(arrays) == 2
    assert np.array_equal(arrays[0].nparray, np.array([1.0, 2.0, 3.0]))
    assert np.array_equal(arrays[1].nparray, np.array([[4.0, 5.0], [6.0, 7.0]]))


def test_parse_string_numbers():
    text = '[["1.2", "3.4", "5"]]'
    arrays = extract_arrays_from_json_text(text)
    expected = np.array([1.2, 3.4, 5.0])
    assert np.array_equal(arrays[0].nparray, expected)


def test_parse_inf_nan():
    text = '[["inf", "-inf", "nan"]]'
    arrays = extract_arrays_from_json_text(text)
    arr = arrays[0].nparray

    assert np.isinf(arr[0]) and arr[0] > 0
    assert np.isinf(arr[1]) and arr[1] < 0
    assert np.isnan(arr[2])


def test_invalid_numeric_string():
    text = '[["abc", "123"]]'
    with pytest.raises(ValueError):
        extract_arrays_from_json_text(text)


def test_invalid_structure_mixed_dimensionality():
    text = '[1, [2, 3]]'  # Mix of non-list and list → should fail
    with pytest.raises(ValueError):
        extract_arrays_from_json_text(text)


def test_file_loading(tmp_path):
    fp = tmp_path / "test.json"
    fp.write_text("[[1, 2, 3]]")

    arrays = extract_arrays_from_json_file(fp)
    assert len(arrays) == 1
    assert np.array_equal(arrays[0].nparray, np.array([1.0, 2.0, 3.0]))