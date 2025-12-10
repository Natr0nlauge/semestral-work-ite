from src import (
    IoMatrix, 
    extract_matrix_from_csv,
    extract_arrays_from_json_file,
    extract_matrix_from_csv,
    extract_arrays_from_json_text,
    extract_arrays_from_latex_file,
    extract_arrays_from_latex_text
)

import numpy as np
import pytest

@pytest.mark.parametrize("arrays", [
    np.array([[1.0, 2.5, -3.0]]),    # Row vector (2D, shape 1xN)
    np.array([[1.0], [2.5], [-3.0]]), # Column vector (2D, shape Nx1)
    np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
])
def test_end_to_end_vector(tmp_path, arrays):
    """
    End-to-end test for vectors (row and column) and matrices through LaTeX → JSON → CSV → back to LaTeX.
    """

    # Step 0: Wrap in IoMatrix
    im = IoMatrix(arrays)

    # Step 1: Convert to LaTeX
    latex_str = im.to_latex(env="pmatrix")
    extracted_from_latex = extract_arrays_from_latex_text(latex_str)
    arr1 = extracted_from_latex[0].nparray
    np.testing.assert_array_almost_equal(arr1, arrays)

    # Step 2: Convert to JSON
    im_from_latex = extracted_from_latex[0]
    json_str = im_from_latex.to_json()
    extracted_from_json = extract_arrays_from_json_text(json_str)
    arr2 = extracted_from_json[0].nparray
    np.testing.assert_array_almost_equal(arr2, arrays)

    # Step 3: Save to CSV
    file_path = "tests\\vector.csv"
    extracted_from_json[0].to_csv(file_path)
    loaded_from_csv = extract_matrix_from_csv(file_path)
    arr3 = loaded_from_csv.nparray
    np.testing.assert_array_almost_equal(arr3, arrays)

    # Step 4: Convert back to LaTeX from CSV-loaded matrix
    latex_from_csv = loaded_from_csv.to_latex(env="pmatrix")
    extracted_final = extract_arrays_from_latex_text(latex_from_csv)
    arr_final = extracted_final[0].nparray
    np.testing.assert_array_almost_equal(arr_final, arrays)
