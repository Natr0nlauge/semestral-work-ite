import numpy as np
#from src import IoMatrix
import src



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
matrices_from_text = src.extract_matrices_from_latex_text(latex_text)
print("From text:")
for matrix in matrices_from_text:
    print(matrix.numpy_to_latex())

# Option 2: From file
matrices_from_file = src.extract_matrices_from_latex_file("example.tex")
print("From file:")
for matrix in matrices_from_file:
    print(matrix.numpy_to_latex())