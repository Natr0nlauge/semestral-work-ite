import numpy as np
import pytest
import tempfile
import os
from unittest.mock import patch

from src import (
    IoMatrix, 
    extract_matrix_from_csv
)

def test_numpy_to_csv_calls_savetxt_with_correct_params():
    arr = np.array([[1.23456, 7.89]])
    io = IoMatrix(arr)

    with patch("numpy.savetxt") as mock_save:
        io.to_csv("file.csv", fmt="{:.3g}")

    mock_save.assert_called_once_with(
        "file.csv",
        arr,
        delimiter=",",
        fmt="%.3g",
    )


@pytest.mark.parametrize(
    "fmt, expected",
    [
        ("{:.3g}", "%.3g"),
        ("{:.5g}", "%.5g"),
        ("{:.2f}", "%.2f"),
    ],
)
def test_numpy_to_csv_format_conversion(fmt, expected):
    arr = np.array([[1.23456]])
    io = IoMatrix(arr)

    with patch("numpy.savetxt") as mock_save:
        io.to_csv("out.csv", fmt=fmt)

    mock_save.assert_called_once_with(
        "out.csv",
        arr,
        delimiter=",",
        fmt=expected,
    )

def test_numpy_to_csv_writes_correct_csv_content():
    arr = np.array([
        [1.23456, 7.89],
        [0.0012345, 12345]
    ])

    io = IoMatrix(arr)

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "matrix.csv")
        io.to_csv(path, fmt="{:.3g}")

        with open(path, "r") as f:
            content = f.read().strip()

    expected = "1.23,7.89\n0.00123,1.23e+04"
    assert content == expected

def test_numpy_to_csv_empty_array():
    arr = np.array([]).reshape(0, 0)
    io = IoMatrix(arr)

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "empty.csv")
        io.to_csv(path)

        # File should exist but be empty
        with open(path) as f:
            content = f.read().strip()

    assert content == ""

def test_numpy_to_csv_invalid_format_string():
    arr = np.array([[1.23]])
    io = IoMatrix(arr)

    # This becomes '%BADFORMAT'
    with pytest.raises(ValueError):
        io.to_csv("tests\\x.csv", fmt="{:BADFORMAT}")

def test_numpy_to_csv_non_string_format():
    arr = np.array([[1]])
    io = IoMatrix(arr)

    with pytest.raises(AttributeError):
        # calling .replace on non-string will cause an AttributeError
        io.to_csv("tests\\x.csv", fmt=123)

def test_numpy_to_csv_permission_error(tmp_path):
    arr = np.array([[1.2]])
    io = IoMatrix(arr)

    # Create a directory path instead of a file
    invalid_path = tmp_path / "not_a_file.csv"
    invalid_path.mkdir()

    # Windows -> PermissionError
    # Unix    -> IsADirectoryError (subclass of OSError)
    with pytest.raises((PermissionError, IsADirectoryError)):
        io.to_csv(str(invalid_path))

def test_numpy_to_csv_nan_inf():
    arr = np.array([[np.nan, np.inf, -np.inf]])
    io = IoMatrix(arr)

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "vals.csv")
        io.to_csv(path)

        with open(path) as f:
            content = f.read().strip()

    assert content == "nan,inf,-inf"

def test_numpy_to_csv_large_array(tmp_path):
    arr = np.random.rand(1000, 1000)
    io = IoMatrix(arr)

    path = tmp_path / "large.csv"
    io.to_csv(str(path))

    assert path.exists()
    assert path.stat().st_size > 0


# Test reading

def test_extract_matrix_from_csv_basic():
    csv = "1.0,2.0\n3.0,4.0\n"
    
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "m.csv")
        with open(path, "w") as f:
            f.write(csv)

        io = extract_matrix_from_csv(path)

    assert isinstance(io, IoMatrix)
    np.testing.assert_array_equal(io.nparray, np.array([[1.0, 2.0],
                                                        [3.0, 4.0]]))
    
def test_extract_matrix_from_csv_single_row():
    csv = "5,6,7\n"

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "row.csv")
        with open(path, "w") as f:
            f.write(csv)

        io = extract_matrix_from_csv(path)

    expected = np.array([[5, 6, 7]])
    np.testing.assert_array_equal(io.nparray, expected)

def test_extract_matrix_from_csv_single_value():
    csv = "42\n"

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "one.csv")
        with open(path, "w") as f:
            f.write(csv)

        io = extract_matrix_from_csv(path)

    assert io.nparray == 42

def test_extract_matrix_from_csv_empty_file():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "empty.csv")
        open(path, "w").close()  # create but leave empty

        with pytest.raises(ValueError):
            extract_matrix_from_csv(path)

def test_extract_matrix_from_csv_invalid_numbers():
    csv = "1.0,abc,3.0\n"

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "bad.csv")
        with open(path, "w") as f:
            f.write(csv)

        with pytest.raises(ValueError):
            extract_matrix_from_csv(path)

def test_extract_matrix_from_csv_file_not_found():
    with pytest.raises(OSError):
        extract_matrix_from_csv("definitely_missing.csv")

def test_extract_matrix_from_csv_delimiter_comma():
    csv = "1;2;3\n"

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "wrongdelim.csv")
        with open(path, "w") as f:
            f.write(csv)

        # loadtxt should fail because delimiter is ",", not ";"
        with pytest.raises(ValueError):
            extract_matrix_from_csv(path)