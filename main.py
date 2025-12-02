import numpy as np
from src import IoMatrix





v = np.array([[1, 2, 3]])

example_vector = IoMatrix(v)

print(example_vector.numpy_to_latex(env="matrix"))