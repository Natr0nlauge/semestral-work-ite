import numpy as np
import re
import json

class IoMatrix:
    def __init__(self, nparray):
        self.nparray = nparray

    def numpy_to_latex(self, fmt="{:.3g}", env="matrix"): #, arr, ):
        """
        Convert a NumPy array to a LaTeX matrix/vector string.

        Parameters:
            fmt (str): Format string for each element (default: 3 significant digits).
            env (str): LaTeX environment: matrix, pmatrix, bmatrix, vmatrix, Vmatrix.

        Returns:
            str: LaTeX code.
        """
        # TODO inf should be displayed in latex with the fitting symbol

        allowed_envs = {"matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix"}
        if env not in allowed_envs:
            raise ValueError(f"Invalid LaTeX environment '{env}'. Must be one of {allowed_envs}.")

        arr = self.nparray

        if arr.ndim == 1:
            # Convert 1D vector to a column vector
            body = " \\\\\n".join(fmt.format(x) for x in arr)
        elif arr.ndim == 2:
            # Convert 2D array to matrix
            rows = []
            for row in arr:
                rows.append(" & ".join(fmt.format(x) for x in row))
            body = " \\\\\n".join(rows)
        else:
            raise ValueError("Only 1D or 2D arrays are supported.")

        return f"\\begin{{{env}}}\n{body}\n\\end{{{env}}}"
    
    def numpy_to_json(self, fmt="{:.3g}", indent=2):
        """
        Convert a NumPy array to a JSON string.

        Parameters:
            fmt (str): Format string for each element (default: 3 significant digits).
            indent (int): JSON indentation level for pretty-printing.

        Returns:
            str: JSON representation of the array.
        """

        arr = self.nparray

        if arr.ndim == 1:
            # 1D -> list
            data = [fmt.format(x) for x in arr]
        elif arr.ndim == 2:
            # 2D -> list of lists
            data = [[fmt.format(x) for x in row] for row in arr]
        else:
            raise ValueError("Only 1D or 2D arrays are supported.")

        # Convert formatted strings back to numeric if possible
        def maybe_number(val):
            try:
                return float(val)
            except ValueError:
                return val

        if arr.ndim == 1:
            data = [maybe_number(x) for x in data]
        else:
            data = [[maybe_number(x) for x in row] for row in data]

        return json.dumps(data, indent=indent)
    





def extract_matrices_from_latex_text(latex_content):
    """
    Extracts all LaTeX matrices from a string and converts them to NumPy arrays.

    Args:
        latex_content (str): LaTeX document content.

    Returns:
        list of np.array: List of matrices found as NumPy arrays.
    """
    # TODO what about reading inf or nan?

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
        matrices.append(IoMatrix(array))
    
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