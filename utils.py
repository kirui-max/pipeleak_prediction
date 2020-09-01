"""
Functions and classes used by multiple scripts
"""

import warnings
warnings.simplefilter('ignore')

import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np
from random import randint, uniform, shuffle
import matplotlib.pyplot as plt
import seaborn as sns

# 95 percentil
def diff95(y_true, y_pred):
	return tfp.stats.percentile(tf.math.abs(tf.math.subtract(y_true, y_pred)), 95, interpolation='linear')

# Map function to array and return it as a np.array
def map_func(func, x):
	return np.array(list(map(func, np.array(x))))

# Scale a value to a range
def scale(x, imin, imax, omin, omax):
	return omin + ((omax - omin) / (imax - imin)) * (x - imin)

# Normalize all inputs
def norm_input(expl_n_id, age, material, pnom, dnom, slope, n_connec, consum, length, ndvi):
	
	def norm_expl_n_id(x):	return x
	def norm_age(x):		return scale(float(x),   0,    100, -1, 1)
	def norm_material(x):
		if   x == 'PE':		return 0
		elif x == 'FIB':	return 1
		elif x == 'FO':		return 2
		elif x == 'PVC':	return 3
		elif x == 'Fe':		return 4
		elif x == 'other':	return 5
		else:
			print(f'------Material {material} is not handled------')
			return None
	def norm_pnom(x):		return scale(float(x),   0,     25, -1, 1)
	def norm_dnom(x):		return scale(float(x),  20,    900, -1, 1)
	def norm_slope(x):		return scale(float(x),   0,     40, -1, 1)
	def norm_n_connec(x):	return scale(float(x),   0,     30, -1, 1)
	def norm_consum(x):		return scale(float(x),   0, 100000, -1, 1)
	def norm_length(x):		return scale(float(x),   0,   2000, -1, 1)
	def norm_ndvi(x):		return scale(float(x),	 0,    1, -1, 1)
	
	n_expl_n_id = 	map_func(norm_expl_n_id, expl_n_id)	# expl_n_id
	n_age =			map_func(norm_age, age)				# age
	n_material =	map_func(norm_material, material)	# material
	n_pnom =		map_func(norm_pnom, pnom)			# pnom
	n_dnom =		map_func(norm_dnom, dnom)			# dnom
	n_slope =		map_func(norm_slope, slope)			# slope
	n_n_connec = 	map_func(norm_n_connec, n_connec)	# n_connec
	n_consum = 		map_func(norm_consum, consum)		# consum
	n_length = 		map_func(norm_length, length)		# length
	n_ndvi = 		map_func(norm_ndvi, ndvi)			# ndvi
	
	return n_expl_n_id, n_age, n_material, n_pnom, n_dnom, n_slope, n_n_connec, n_consum, n_length, n_ndvi

# Normalize the inputs when they are an array
def norm_input_arr(inputs):
	
	return norm_input(inputs[0], inputs[1], inputs[2], inputs[3],
					  inputs[4], inputs[5], inputs[6], inputs[7],
					  inputs[8], inputs[9])
