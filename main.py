import numpy as np
#from src import IoMatrix
import src
import json



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
#print("From text:")
# for matrix in matrices_from_text:
#     print(matrix.numpy_to_latex())

# Option 2: From file
matrices_from_file = src.extract_matrices_from_latex_file("example.tex")
#print("From file:")
# for matrix in matrices_from_file:
#     print(matrix.numpy_to_latex())

#print(matrices_from_file[0].numpy_to_json())

arr = np.array([np.nan, np.inf, -np.inf])
io = src.IoMatrix(arr)

#result = json.loads(io.numpy_to_json())

print(io.numpy_to_latex())