import numpy as np
import pytest
from src import IoMatrix


# -----------------------------
# BASIC FUNCTIONALITY TESTS
# -----------------------------

def test_vector_to_latex_basic():
    arr = np.array([1, 2, 3])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "1 \\\\\n"
        "2 \\\\\n"
        "3\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex() == expected


def test_matrix_to_latex_basic():
    arr = np.array([[1, 2], [3, 4]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "1 & 2 \\\\\n"
        "3 & 4\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex() == expected


# -----------------------------
# EDGE CASES
# -----------------------------

def test_empty_vector():
    arr = np.array([])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex() == expected


def test_empty_matrix():
    arr = np.array([[]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex() == expected


def test_single_element_vector():
    arr = np.array([42])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "42\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex() == expected


def test_single_element_matrix():
    arr = np.array([[7]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "7\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex() == expected


def test_negative_numbers():
    arr = np.array([[-1, -2.5]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "-1 & -2.5\n"
        "\\end{matrix}"
    )
    assert io.numpy_to_latex(fmt="{:.3g}") == expected


def test_large_small_values():
    arr = np.array([[1e10, 5e-12]])
    io = IoMatrix(arr)
    result = io.numpy_to_latex()
    assert "1e+10" in result
    assert "5e-12" in result


# -----------------------------
# FORMAT AND ENVIRONMENT TESTS
# -----------------------------

def test_custom_format():
    arr = np.array([[1.2345, 9.8765]])
    io = IoMatrix(arr)
    result = io.numpy_to_latex(fmt="{:.2f}")
    expected = (
        "\\begin{matrix}\n"
        "1.23 & 9.88\n"
        "\\end{matrix}"
    )
    assert result == expected


def test_different_environment():
    arr = np.array([[1, 2]])
    io = IoMatrix(arr)
    result = io.numpy_to_latex(env="pmatrix")
    assert result.startswith("\\begin{pmatrix}")
    assert result.endswith("\\end{pmatrix}")


# -----------------------------
# ERROR CONDITION TESTS
# -----------------------------

def test_3d_array_raises():
    arr = np.zeros((2, 2, 2))
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        io.numpy_to_latex()

def test_non_numeric_array_raises():
    arr = np.array([["a", "b"]])
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        # formatting should fail inside fmt.format(x)
        io.numpy_to_latex()

def test_invalid_format_array_raises():
    arr = np.array([[1, 2]])
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        # formatting should fail inside fmt.format(x)
        io.numpy_to_latex(env="nonsense")

def test_invalid_input_type():
    with pytest.raises(AttributeError):  # nparray not a numpy array
        IoMatrix("hello").numpy_to_latex()

def test_inconsistent_row_lengths():
    # NumPy normally blocks jagged arrays unless dtype=object
    arr = np.array([[1, 2], [3]], dtype=object)
    io = IoMatrix(arr)
    with pytest.raises(Exception):
        io.numpy_to_latex()
