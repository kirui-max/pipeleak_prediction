"""
This file will plot how each input modifies the network prediction
"""

import sys
sys.path.append("..")

import warnings
warnings.simplefilter('ignore')

from utils import norm_input_arr, diff95
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from tensorflow.python.keras.api._v2.keras.models import load_model, Model
import psycopg2

# Connect to the database
conn = psycopg2.connect(database='giswater3', user='postgres', password='postgres', host='localhost')
cursor = conn.cursor()

# Get the temperature data from the database
cursor.execute(f"select period, val from api_ws_sample.ext_timeseries")
temperature = cursor.fetchall()

# Load the model with its custom metrics (else it would give an error)
model = tf.keras.models.load_model('C:/Users/elies/Desktop/break_prediction/models/ndvi_7.h5', custom_objects={'diff95': diff95})
# model.summary()

# List to iterate on every type of material
mats = ['Fe', 'FO', 'FIB', 'PE', 'PVC', 'other']

# Set the range of each variable you want to analyze
plots = {
	'expl_id': 	[np.arange(0, 23, 1), "id del municipi"],
	'material':	[mats, "material"],
	'ndvi':		[np.arange(0, 1, 0.1), "index ndvi"],
	'age':  	[np.arange(0, 100, 0.1), "edat [anys]"],
	'dnom': 	[np.arange(20, 900, 0.1), "diàmetre [mm]"],
	'pnom': 	[np.array([6, 10, 16, 25]), "pressió nominal [kg]"],
	'slope': 	[np.arange(0, 15, 0.1), "pendent [%]"],
	'n_connec':	[np.arange(0, 30, 1), "nombre de connexions"],
	'consum':	[np.arange(0, 40000, 20), "consum [m3]"],
	'length': 	[np.arange(0.6, 1000, 1), "longitud [m]"]
}


# For each dictionary key (@var) and value (@ran). Also store the item index
for n, (var, ran) in enumerate(plots.items()):

	plt.figure(figsize=(9, 5), dpi=100)

	rang = list(ran[0])
	
	print(n + 1)

	# Start a subplot in the window
	# plt.subplot(2, 4, n + 1)

	# For each material plot how the the input efects the output
	# for mat in mats:

	# Initialize the values
	data = dict()

	data['expl_id'] =	[0] * len(rang)
	data['age'] =		[30] * len(rang)
	data['material'] =	['Fe'] * len(rang)
	data['pnom'] =		[10] * len(rang)
	data['dnom'] =		[200] * len(rang)
	data['slope'] =		[4] * len(rang)
	data['n_connec'] =	[2] * len(rang)
	data['consum'] =	[1000] * len(rang)
	data['length'] =	[130] * len(rang)
	data['sum'] =		[0.5] * len(rang)

	# Set the dynamic values
	data[var] = rang
	# data['material'] = [mat] * len(ran)

	# inputs = [list(map(list, x)) for x in data.values()]
	inputs = [list(map(lambda i: [i], x)) for x in data.values()]

	# Predict the inputs
	y = model.predict(norm_input_arr(inputs))


	
	dat = sorted(zip(y, rang))
	
	# Plot the data
	for yy, x in dat:
		print(x, yy)
		plt.bar(x, yy)
	# plt.plot(rang, y)#, label=mat)

	# Set the tile of the subplot
	# plt.title(var)
	
	plt.xticks(list(zip(*dat))[1])
	
	plt.xlabel(ran[1], size=15)
	plt.ylabel("probabilitat de trencament", size=15)
	
	# Plot the lengend and reduce its size
	# plt.legend(fontsize='x-small')
	
	plt.tight_layout()
	
	plt.show()

