"""
Functions and classes used by multiple scripts
"""

import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np

# 95 percentil
def diff95(y_true, y_pred):
	return tfp.stats.percentile(tf.math.abs(tf.math.subtract(y_true, y_pred)), 95, interpolation='linear')

# Map function to array and return it as a np.array
def map_func(func, x):
	return np.array(list(map(func, np.array(x))))

# Scale a value to a range
def scale(x, imin, imax, omin=0, omax=1):
	return omin + ((omax - omin) / (imax - imin)) * (x - imin)
