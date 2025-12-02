import numpy as np

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