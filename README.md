# MATRIX-IO Format Converter

## Purpose of the Program

The MATRIX-IO Format Converter is a Python utility designed to convert matrices and vectors between common formats including **LaTeX**, **CSV**, and **JSON**.  

It simplifies transferring mathematical data between documents, scripts, and structured data files. Typical use cases include:  

- Importing a LaTeX matrix into Python as a NumPy array.
- Exporting a NumPy array to LaTeX for academic papers or reports.
- Saving or loading arrays as CSV or JSON for interoperability with other software.  

The utility wraps NumPy arrays in the `IoMatrix` class, providing convenient methods for reading, formatting, and exporting arrays in multiple formats.

---

## Installation

### Requirements

- Python 3.8 or higher
- NumPy

Optional dependencies (if saving to files in specific formats):

- None, standard library modules (`json`, `re`, `numbers`) are sufficient.

### Installation Steps

1. **Clone the repository**:

```bash
git clone https://github.com/Natr0nlauge/matrix-io.git
cd matrix-io
````

2. **Install dependencies**:

```bash
pip install numpy
```

3. **Verify installation** by running Python and importing the module:

```python
import numpy as np
from iomatrix import IoMatrix
```

---

## Usage Manual

### Creating an `IoMatrix`

```python
import numpy as np
from iomatrix import IoMatrix

array = np.array([[1, 2], [3, 4]])
matrix = IoMatrix(array)
```

### Exporting to LaTeX

```python
latex_code = matrix.to_latex(fmt="{:.2f}", env="bmatrix")
print(latex_code)
```

Output example:

```latex
\begin{bmatrix}
1.00 & 2.00 \\
3.00 & 4.00
\end{bmatrix}
```

### Exporting to JSON

```python
json_text = matrix.to_json(fmt="{:.2f}", indent=2)
print(json_text)
```

Output example:

```json
[
  [1.00, 2.00],
  [3.00, 4.00]
]
```

### Exporting to CSV

```python
matrix.to_csv("matrix.csv", fmt="{:.2f}")
```

### Importing Arrays

#### From LaTeX Text or File

```python
from iomatrix import extract_arrays_from_latex_text, extract_arrays_from_latex_file

matrices = extract_arrays_from_latex_text(latex_string)
matrices_from_file = extract_arrays_from_latex_file("file.tex")
```

#### From JSON Text or File

```python
from iomatrix import extract_arrays_from_json_text, extract_arrays_from_json_file

matrices = extract_arrays_from_json_text(json_string)
matrices_from_file = extract_arrays_from_json_file("file.json")
```

#### From CSV

```python
from iomatrix import extract_matrix_from_csv

matrix = extract_matrix_from_csv("matrix.csv")
```

---

## Limitations or Known Issues

* Only **1D or 2D arrays** are supported; higher-dimensional arrays are not currently handled.
* LaTeX parser assumes a standard matrix environment and numeric entries; it may fail on complex expressions or symbolic entries.
* CSV import assumes numeric data only and may fail with empty or malformed files.
* JSON import expects a consistent list-of-lists structure; non-numeric strings may raise errors.
* LaTeX formatting currently supports environments: `matrix`, `pmatrix`, `bmatrix`, `vmatrix`, `Vmatrix`.
* Some formatting strings (e.g., very large precision) may not round-trip perfectly between JSON/LaTeX/CSV.