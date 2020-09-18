"""
Functions and classes used by multiple scripts
"""

import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np

# Map function to array and return it as a np.array
def map_func(func, x):
	return np.array(list(map(func, np.array(x))))

# Scale a value to a range
def scale(x, imin, imax, omin=0, omax=1):
	return omin + ((omax - omin) / (imax - imin)) * (x - imin)
