# Testing Approach and Rationale

This project includes automated tests designed to validate both the writing and reading features of the `IoMatrix` module. The tests cover a full range of scenarios, from basic functionality to edge cases and error conditions.

## Goals of the Test Suite

1. Verify correctness of output from NumPy arrays under various configurations.
2. Ensure robustness against invalid inputs, malformed formatting, and unexpected array shapes.
3. Validate LaTeX parsing for extracting matrices from text or files.
4. Test edge cases, including empty matrices, special values (NaN, ±∞), inconsistent formatting, and comment stripping.
5. Provide clear examples of expected behavior to aid future maintenance.

---

# Summary of Test Categories

## 1. Basic Writing Functionality Tests

Ensure that:

* Standard vectors and matrices are converted correctly to LaTeX, JSON and CSV.
* Formatting rules (row breaks, separators, environment names) are applied consistently.

**Example for LaTeX:**

```
Input:
array([[1, 2], [3, 4]])

Output:
"\\begin{matrix}\n1 & 2 \\\\n3 & 4\n\\end{matrix}"
```

---

## 2. Edge Case Tests

Validates handling of:

* Empty arrays (`[]` and `[[]]`)
* Single‑element arrays
* Negative values and custom formatting
* Very large and very small floating‑point values
* Special numeric values: `NaN`, `inf`, `-inf`

**Example for LaTeX:**

```
Input:
array([[np.nan], [np.inf], [-np.inf]])
Output:
"\\begin{matrix}\n\\mathrm{NaN} \\\\n\\infty \\\\n-\\infty\n\\end{matrix}"
```

---

## 3. Format and Environment Tests

Ensures users can:

* Provide custom numeric format strings
* Select alternate LaTeX environments (e.g., `pmatrix`, `bmatrix`)

**Example:**

```
Input:
array([[1.2345, 9.8765]]), fmt="{:.2f}"
Output:
"1.23 & 9.88"
```

---

## 4. Error Condition Tests

Ensures correct exceptions are thrown when:

* Attempting to convert 3‑D arrays
* Non‑numeric data is present
* Input is not a NumPy array
* Rows have inconsistent lengths

The test cases are designed to verify that the correct exceptions are thrown.

---

## 5. Matrix Extraction Tests

Validates the behavior of functions extracting arrays from text or files.

The tests verify that:

* Multiple matrices can be extracted from a single LaTeX or JSON input
* LaTeX comments are ignored
* Whitespace and irregular spacing are handled robustly
* Matrices with inconsistent rows or invalid numeric values raise errors

**Example (Valid):**

```
Input:
"\\begin{bmatrix} 1 & 2 \\ 3 & 4 \\ end{bmatrix}"
Output:
array([[1,2],[3,4]])
```

**Example (Invalid):**

```
Input contains:
1 & x
Raises:
ValueError
```

## 6. Integration Tests

These tests verify that a matrix or vector can be serialized and deserialized consistently through the full pipeline:

**LaTeX → JSON → CSV → LaTeX**


---

# Sample Input/Output Pairs

## LaTeX

| Description          | Input                           | Output                          |
| -------------------- | ------------------------------- | ------------------------------- |
| Basic 2×2 matrix     | `[[1,2],[3,4]]`                 | `\\begin{matrix} ...`           |
| Single column vector | `[[1],[2],[3]]`                 | Matrix with line breaks         |
| NaN/inf handling     | `[[nan],[inf],[-inf]]`          | Uses `\\mathrm{NaN}`, `\\infty` |
| Extract bmatrix      | LaTeX text containing `bmatrix` | Returns NumPy array             |
| Invalid entry        | Matrix with `x`                 | Raises `ValueError`             |

## JSON

| Description         | Input                                  | Output                                    |
| ------------------- | -------------------------------------- | ----------------------------------------- |
| Basic 2×2 matrix    | `[[1.2345, 2.3456], [3.4567, 4.5678]]` | Nested JSON list: `[[1.23, 2.35], [3.46, 4.57]]`            |
| NaN/inf             | `[nan, inf, -inf]`                     | JSON list containing `NaN`, `inf`, `-inf` |
| Custom formatting   | `[1.2345]` with `fmt="{:.2f}"`         | `[[1.23]]`                                |
| Parse JSON vector   | `"[[1,2,3]]"`                          | NumPy array `[[1.,2.,3.]]`                |
| Parse nested arrays | `[[[1,2,3]], [[4,5],[6,7]]]`           | Two matrices returned                     |                 |

## CSV

| Description         | Input                                   | Output                             |
| ------------------- | --------------------------------------- | ---------------------------------- |
| Basic matrix to CSV | `[[1.23456, 7.89]]` with `fmt="{:.3g}"` | `1.23,7.89`                        |
| Multi-row CSV       | `[[1.1, 2.2], [3.3, 4.4]]`              | `1.1,2.2 \n 3.3,4.4`               |
| Read CSV matrix     | `1.0,2.0 \n 3.0,4.0`                    | `[[1.,2.],[3.,4.]]`                |
| Read value          | `42`                                    | `42`                               |
| Invalid numeric     | `1.0,abc,3.0`                           | error                              |
| Wrong delimiter     | `1;2;3`                                 | error                              |

---

# How To Run the Tests

Run in the console:
```
pytest -q
```
Or execute the `test_main.py` file.


