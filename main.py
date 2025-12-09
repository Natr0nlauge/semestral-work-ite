import numpy as np
#from src import IoMatrix
import src
import json



text = """
        [1, [1, 2, 3]]
    """
# text = """
#     [
#         [1, 2, 3]
#     ]
#     """
# text = "[1, 2, 3]"
arrays = src.extract_arrays_from_json_text(text)
print(arrays[0].nparray)
#print(arrays[1].nparray)


