import numpy as np
import pytest
from unittest.mock import mock_open, patch
from src import (
    extract_arrays_from_latex_text,
    extract_arrays_from_latex_file,
    IoMatrix,
)


# -----------------------------
# BASIC FUNCTIONALITY TESTS
# -----------------------------

def test_vector_to_latex_basic():
    arr = np.array([[1], [2], [3]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "1 \\\\\n"
        "2 \\\\\n"
        "3\n"
        "\\end{matrix}"
    )
    assert io.to_latex() == expected


def test_matrix_to_latex_basic():
    arr = np.array([[1, 2], [3, 4]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "1 & 2 \\\\\n"
        "3 & 4\n"
        "\\end{matrix}"
    )
    assert io.to_latex() == expected


# -----------------------------
# EDGE CASES
# -----------------------------

def test_latex_empty_vector():
    arr = np.array([])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "\n"
        "\\end{matrix}"
    )
    assert io.to_latex() == expected


def test_latex_empty_matrix():
    arr = np.array([[]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "\n"
        "\\end{matrix}"
    )
    assert io.to_latex() == expected


def test_latex_single_element_vector():
    arr = np.array([42])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "42\n"
        "\\end{matrix}"
    )
    assert io.to_latex() == expected


def test_latex_single_element_matrix():
    arr = np.array([[7]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "7\n"
        "\\end{matrix}"
    )
    assert io.to_latex() == expected


def test_latex_negative_numbers():
    arr = np.array([[-1, -2.5]])
    io = IoMatrix(arr)
    expected = (
        "\\begin{matrix}\n"
        "-1 & -2.5\n"
        "\\end{matrix}"
    )
    assert io.to_latex(fmt="{:.3g}") == expected


def test_latex_large_small_values():
    arr = np.array([[1e10, 5e-12]])
    io = IoMatrix(arr)
    result = io.to_latex()
    assert "1e+10" in result
    assert "5e-12" in result

def test_latex_nan_inf_values():
    arr = np.array([[np.nan], [np.inf], [-np.inf]])
    io = IoMatrix(arr)
    result = io.to_latex()
    expected = (
        "\\begin{matrix}\n"
        "\mathrm{NaN} \\\\\n"
        "\infty \\\\\n"
        "-\infty\n"
        "\\end{matrix}"
    )
    assert result == expected

# -----------------------------
# FORMAT AND ENVIRONMENT TESTS
# -----------------------------

def test_latex_custom_format():
    arr = np.array([[1.2345, 9.8765]])
    io = IoMatrix(arr)
    result = io.to_latex(fmt="{:.2f}")
    expected = (
        "\\begin{matrix}\n"
        "1.23 & 9.88\n"
        "\\end{matrix}"
    )
    assert result == expected


def test_latex_different_environment():
    arr = np.array([[1, 2]])
    io = IoMatrix(arr)
    result = io.to_latex(env="pmatrix")
    assert result.startswith("\\begin{pmatrix}")
    assert result.endswith("\\end{pmatrix}")


# -----------------------------
# ERROR CONDITION TESTS
# -----------------------------

def test_latex_3d_array_raises():
    arr = np.zeros((2, 2, 2))
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        io.to_latex()

def test_latex_non_numeric_array_raises():
    arr = np.array([["a", "b"]])
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        # formatting should fail inside fmt.format(x)
        io.to_latex()

def test_latex_invalid_format_array_raises():
    arr = np.array([[1, 2]])
    io = IoMatrix(arr)
    with pytest.raises(ValueError):
        # formatting should fail inside fmt.format(x)
        io.to_latex(env="nonsense")

def test_latex_invalid_input_type():
    with pytest.raises(TypeError):  # nparray not a numpy array
        IoMatrix("hello").to_latex()

def test_latex_inconsistent_row_lengths():
    # NumPy normally blocks jagged arrays unless dtype=object
    arr = np.array([[1, 2], [3]], dtype=object)
    io = IoMatrix(arr)
    with pytest.raises(Exception):
        io.to_latex()

# -----------------------------
# Test matrix reading
# -----------------------------   

def test_latex_extract_single_bmatrix():
    latex = r"""
        \begin{bmatrix}
            1 & 2 \\
            3 & 4
        \end{bmatrix}
    """
    matrices = extract_arrays_from_latex_text(latex)
    assert len(matrices) == 1
    expected = np.array([[1, 2], [3, 4]])
    assert np.array_equal(matrices[0].nparray, expected)

def test_latex_extract_multiple_matrices():
    latex = r"""
        \begin{pmatrix}
            1 & 0
        \end{pmatrix}

        \begin{bmatrix}
            2 & 3 \\
            4 & 5
        \end{bmatrix}
    """
    matrices = extract_arrays_from_latex_text(latex)
    assert len(matrices) == 2
    assert np.array_equal(matrices[0].nparray, np.array([[1, 0]]))
    assert np.array_equal(matrices[1].nparray, np.array([[2, 3], [4, 5]]))

def test_latex_strip_comments():
    latex = r"""
        % This is a comment
        \begin{matrix}
            1 & 2 \\ 3 & 4
        \end{matrix}
        % another comment
    """
    matrices = extract_arrays_from_latex_text(latex)
    assert len(matrices) == 1
    assert np.array_equal(matrices[0].nparray, np.array([[1, 2], [3, 4]]))

def test_latex_spaces_and_newlines():
    latex = r"""
        \begin{bmatrix}
            10 &   20     \\    
            30   &    40
        \end{bmatrix}
    """
    matrices = extract_arrays_from_latex_text(latex)
    expected = np.array([[10, 20], [30, 40]])
    assert np.array_equal(matrices[0].nparray, expected)

def test_latex_extract_from_file():
    matrices = extract_arrays_from_latex_file("tests\\example.tex")

    expected = [np.array([[1, 2, 3], [4, 5, 6]]), np.array([[7,8], [9,10]])]
    assert len(matrices) == 2
    assert np.array_equal(matrices[0].nparray, expected[0])
    assert np.array_equal(matrices[1].nparray, expected[1])

def test_latex_invalid_float_raises():
    latex = r"""
        \begin{bmatrix}
            1 & x \\
            2 & 3
        \end{bmatrix}
    """
    with pytest.raises(ValueError):
        extract_arrays_from_latex_text(latex)

def test_latex_invalid_format_raises():
    latex = r"""
        \begin{bmatrix}
            1 \\
            2 & 3
        \end{bmatrix}
    """
    with pytest.raises(ValueError):
        extract_arrays_from_latex_text(latex)

def test_latex_no_matrices_found():
    latex = "No matrix here"
    matrices = extract_arrays_from_latex_text(latex)
    assert matrices == []