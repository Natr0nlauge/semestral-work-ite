import numpy as np
import re
import json
import numbers

class IoMatrix:
    def __init__(self, nparray):
        if not isinstance(nparray, np.ndarray):
            raise TypeError("IoMatrix expects a NumPy array.")
        self.nparray = nparray

    def to_latex(self, fmt="{:.3g}", env="matrix"): #, arr, ):
        """
        Convert a NumPy array to a LaTeX matrix/vector string.

        Parameters:
            fmt (str): Format string for each element (default: 3 significant digits).
            env (str): LaTeX environment: matrix, pmatrix, bmatrix, vmatrix, Vmatrix.

        Returns:
            str: LaTeX code.
        """

        allowed_envs = {"matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix"}
        if env not in allowed_envs:
            raise ValueError(f"Invalid LaTeX environment '{env}'. Must be one of {allowed_envs}.")

        arr = self.nparray

        def fmt_value(x):
            if not isinstance(x, numbers.Number):
                raise ValueError(f"Invalid type of array element '{x}'")
            if np.isinf(x):
                return r"\infty" if x > 0 else r"-\infty"
            if np.isnan(x):
                return r"\mathrm{NaN}"
            return fmt.format(x)

        if arr.ndim == 1:
            # Convert 1D vector to a row vector
            body = " & ".join(fmt_value(x) for x in arr)
        elif arr.ndim == 2:
            # Convert 2D array to matrix
            rows = []
            for row in arr:
                rows.append(" & ".join(fmt_value(x) for x in row))
            body = " \\\\\n".join(rows)
        else:
            raise ValueError("Only 1D or 2D arrays are supported.")

        return f"\\begin{{{env}}}\n{body}\n\\end{{{env}}}"
    
    def to_json(self, fmt="{:.3g}", indent=2):
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
            data = [[maybe_number(x) for x in data]]
        else:
            data = [[maybe_number(x) for x in row] for row in data]

        return json.dumps(data, indent=indent)

    def to_csv(self, filename, fmt="{:.3g}"):
        """
        Save a NumPy 2D array to a CSV file using a specified significant-digit format.
        Example fmt: "{:.3g}", "{:.5g}", "{:.2f}", etc.
        """
        # Convert Python's format-string style "{:.3g}" to NumPy's format "%.3g"
        numpy_fmt = fmt.replace("{:", "%").replace("}", "")
        
        np.savetxt(filename, self.nparray, delimiter=",", fmt=numpy_fmt)

    





def extract_arrays_from_latex_text(latex_content):
    """
    Extracts all LaTeX matrices from a string and converts them to NumPy arrays.

    Args:
        latex_content (str): LaTeX document content.

    Returns:
        list of IoMatrix: List of found matrices/vectors.
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
        matrices.append(IoMatrix(array))
    
    return matrices



def extract_arrays_from_latex_file(file_path):
    """
    Reads a LaTeX file and extracts all matrices as NumPy arrays.

    Args:
        file_path (str): Path to the LaTeX file.

    Returns:
        list of IoMatrix: List of found matrices/vectors.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        latex_content = f.read()
    
    # Use the text-based function
    return extract_arrays_from_latex_text(latex_content)


def extract_arrays_from_json_text(json_content):
    """
    Expected format:
      Vector: [[1, 2, 3]]
      Matrix: [[1, 2], [3, 4]]
      Multiple arrays: [ [[...]], [[...]] ]
      
    Parameters:
        json_content (str): JSON text.

    Returns:
        list of np.array: Each extracted NumPy array.
    """

    # Parse JSON
    data = json.loads(json_content)

    # Normalize:
    # If the root is a single nested array representing one array,
    # wrap it into a list so everything is processed uniformly.
    if not (isinstance(data, list) and all(isinstance(x, list) for x in data) and
            all(isinstance(el, list) for el in data[0])):
        # Means root is a single array (vector or matrix)
        data = [data]

    arrays = []

    for entry in data:

        # Helper: convert numeric strings ("1.23", "inf") cleanly
        def parse_item(x):
            if isinstance(x, (int, float)):
                return float(x)
            if isinstance(x, str):
                lx = x.strip().lower()
                if lx in ("inf", "+inf", "infinity"):
                    return float("inf")
                if lx in ("-inf", "-infinity"):
                    return -float("inf")
                if lx == "nan":
                    return float("nan")
                try:
                    return float(x)
                except ValueError:
                    raise ValueError(f"Invalid numeric value: {x}")
            raise ValueError(f"Unsupported JSON type: {type(x)}")
        
        rows = []
        for row in entry:
            if not isinstance(row, list):
                raise ValueError(f"Invalid format - array expected: {row}")
            else:
                parsed_row = np.array([parse_item(x) for x in row], dtype = float)
                rows.append(parsed_row)

        arr = np.array(rows, dtype=float)

        # if arr.ndim == 2 and arr.shape[0] == 1:
        #     arr = arr.flatten()
        arrays.append(IoMatrix(arr))

    return arrays



def extract_arrays_from_json_file(file_path):
    """
    Reads a JSON file and extracts arrays as NumPy arrays.

    Parameters:
        file_path (str): Path to a JSON file.

    Returns:
        list of IoMatrix: List of found matrices/vectors
    """

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return extract_arrays_from_json_text(content)

def extract_matrix_from_csv(file_path):
    """
    Load a CSV file into a NumPy 2D array.
    
    - Single line CSV → row vector [[1, 2, 3]]
    - Single column CSV → column vector [[1], [2], [3]]
    - Multiple rows/columns → 2D array
    """
    array = np.loadtxt(file_path, delimiter=",")
    
    if array.size == 0:
        raise ValueError("Empty CSV file")
    
    # If 1D, decide row or column vector
    if array.ndim == 1:
        # Check if file has a single line (row)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if len(lines) == 1:
            array = array.reshape(1, -1)  # row vector
        else:
            array = array.reshape(-1, 1)  # column vector
    
    return IoMatrix(array)