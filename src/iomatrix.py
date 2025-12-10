import numpy as np
import re
import json
import os
import numbers

class IoMatrix:
    """
    A wrapper class for a NumPy array with convenient methods to export
    to LaTeX, JSON, and CSV formats.
    """
    def __init__(self, nparray):
        """
        Initialize IoMatrix with a NumPy array.

        Parameters:
            nparray (np.ndarray): A 1D or 2D NumPy array.

        Raises:
            TypeError: If the input is not a NumPy array.
        """
        if not isinstance(nparray, np.ndarray):
            raise TypeError("IoMatrix expects a NumPy array.")
        self.nparray = nparray

    def to_latex(self, fmt="{:.3g}", env="matrix"): #, arr, ):
        """
        Convert the stored NumPy array to a LaTeX matrix or vector.

        Parameters:
            fmt (str): Format string for each element (default: 3 significant digits).
            env (str): LaTeX environment. Options: "matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix".

        Returns:
            str: LaTeX code representing the array.

        Raises:
            ValueError: If the array has more than 2 dimensions or the environment is invalid.
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
        Convert the stored NumPy array to a JSON string.

        Parameters:
            fmt (str): Format string for each element (default: 3 significant digits).
            indent (int): Indentation level for pretty-printing JSON.

        Returns:
            str: JSON representation of the array.

        Raises:
            ValueError: If the array has more than 2 dimensions.
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
        Save the stored NumPy array to a CSV file.

        Parameters:
            filename (str): Path to the CSV file.
            fmt (str): Format string for elements, e.g., "{:.3g}", "{:.2f}".

        Raises:
            ValueError: If the array cannot be saved to CSV.
        """
        # Convert Python's format-string style "{:.3g}" to NumPy's format "%.3g"
        numpy_fmt = fmt.replace("{:", "%").replace("}", "")
        
        np.savetxt(filename, self.nparray, delimiter=",", fmt=numpy_fmt)

    





def extract_arrays_from_latex_text(latex_content):
    """
    Extract all LaTeX matrices from a string and convert them to IoMatrix objects.

    Parameters:
        latex_content (str): LaTeX document content.

    Returns:
        list of IoMatrix: List of matrices/vectors found in the LaTeX content.
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
    Extract all matrices from a LaTeX file.

    Parameters:
        file_path (str): Path to a LaTeX file.

    Returns:
        list of IoMatrix: List of matrices/vectors found in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        latex_content = f.read()
    
    # Use the text-based function
    return extract_arrays_from_latex_text(latex_content)


def extract_arrays_from_json_text(json_content):
    """
    Extract arrays from a JSON string into IoMatrix objects.

    Parameters:
        json_content (str): JSON-formatted text.

    Returns:
        list of IoMatrix: Each extracted array wrapped in an IoMatrix.
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
    Read a JSON file and extract all arrays as IoMatrix objects.

    Parameters:
        file_path (str): Path to a JSON file.

    Returns:
        list of IoMatrix: List of matrices/vectors found in the JSON file.
    """

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return extract_arrays_from_json_text(content)

def extract_matrix_from_csv(file_path):
    """
    Load a CSV file into an IoMatrix object.

    Single-line CSV → row vector
    Single-column CSV → column vector
    Multiple rows/columns → 2D array

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        IoMatrix: Array read from the CSV file.

    Raises:
        ValueError: If the CSV file is empty.
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


def extract_matrix_from_file(file_path):
    """
    Determine the file type from its extension and extract matrices accordingly.

    Supported formats:
        - .json  → extract_arrays_from_json_file
        - .tex   → extract_arrays_from_latex_file
        - .csv   → extract_matrix_from_csv

    Parameters:
        file_path (str): Path to the file.

    Returns:
        list[IoMatrix] or IoMatrix:
            - JSON/TEX files may contain multiple arrays → returns a list of IoMatrix objects.
            - CSV files represent a single array → returns a single IoMatrix.

    Raises:
        ValueError: If unsupported extension or file not found.
    """

    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".json":
        return extract_arrays_from_json_file(file_path)

    elif ext in {".tex", ".latex"}:
        return extract_arrays_from_latex_file(file_path)

    elif ext == ".csv":
        return extract_matrix_from_csv(file_path)

    else:
        raise ValueError(
            f"Unsupported file extension '{ext}'. "
            "Supported types are: .json, .tex, .csv"
        )
    
def run_from_command_line():
    """
    Command-line interface:
        1. Ask user for a file path.
        2. Parse the file into IoMatrix object(s).
        3. Ask user for an output format: latex, json, csv.
        4. Print converted matrices in that format.
    """

    file_path = input("Enter the path to the file (.json, .tex, .csv): ").strip()

    try:
        result = extract_matrix_from_file(file_path)

        # Normalize result -> always a list of IoMatrix
        matrices = result if isinstance(result, list) else [result]
        print(f"Found matrices: {len(result)}")

        if not matrices:
            print("No matrices found.")
            return

        # Ask for output format
        output_format = input("Enter output format (latex / json / csv): ").strip().lower()

        if output_format not in {"latex", "json", "csv"}:
            print(f"Invalid format '{output_format}'. Must be latex, json, or csv.")
            return

        print(f"\nConverted {len(matrices)} matrix/matrices:\n")

        for i, M in enumerate(matrices, start=1):
            print(f"--- Matrix {i} ---")

            if output_format == "latex":
                print(M.to_latex())

            elif output_format == "json":
                print(M.to_json())

            elif output_format == "csv":
                # Print CSV as a string instead of writing to file
                import io
                buffer = io.StringIO()
                # Use same formatting style as np.savetxt
                fmt = "%.3g"
                np.savetxt(buffer, M.nparray, delimiter=",", fmt=fmt)
                print(buffer.getvalue())

            print()  # blank line for separation

    except Exception as e:
        print(f"\nError: {e}")

