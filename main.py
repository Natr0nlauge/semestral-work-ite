import numpy as np
from src import IoMatrix
import re


def extract_matrices_from_latex_text(latex_content):
    """
    Extracts all LaTeX matrices from a string and converts them to NumPy arrays.

    Args:
        latex_content (str): LaTeX document content.

    Returns:
        list of np.array: List of matrices found as NumPy arrays.
    """
    # Remove comments to avoid parsing issues
    latex_content = re.sub(r'%.*', '', latex_content)

    # Regex to match LaTeX matrix environments
    pattern = r"\\begin\{(bmatrix|pmatrix|matrix|vmatrix|Vmatrix)\}(.*?)\\end\{\1\}"
    matches = re.findall(pattern, latex_content, re.DOTALL)
    
    matrices = []
    
    for env, matrix_content in matches:
        matrix_content = matrix_content.strip()
        # Split rows by "\\" and then columns by "&"
        rows = [row.strip().split("&") for row in matrix_content.split("\\\\")]
        # Convert to float
        array = np.array([[float(entry.strip()) for entry in row] for row in rows])
        matrices.append(array)
    
    return matrices


def extract_matrices_from_latex_file(file_path):
    """
    Reads a LaTeX file and extracts all matrices as NumPy arrays.

    Args:
        file_path (str): Path to the LaTeX file.

    Returns:
        list of np.array: List of matrices found.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        latex_content = f.read()
    
    # Use the text-based function
    return extract_matrices_from_latex_text(latex_content)


# Example usage:
latex_text = r"""
Here is a matrix:
\[
\begin{bmatrix}
1 & 2 & 3 \\
4 & 5 & 6
\end{bmatrix}
\]
"""

# Option 1: From text
matrices_from_text = extract_matrices_from_latex_text(latex_text)
print("From file:")
for matrix in matrices_from_text:
    print(matrix)

# Option 2: From file
matrices_from_file = extract_matrices_from_latex_file("example.tex")
print("From file:")
for matrix in matrices_from_file:
    print(matrix)