"""
This script creates an interactive application in which you can set all model variables througth sliders
"""

import os
import sys
sys.path.append("..")

from utils import *

from functools import partial
from tensorflow.keras.models import load_model
import tensorflow as tf
from random import randint
import psycopg2
from typing import List

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QLabel, QSlider, QHBoxLayout, QWidget, QGridLayout, QPushButton, QDialog, QSpacerItem, QSizePolicy


# Contains the data of one input to the neural network
class Param:
	def __init__(self, var, min_val, max_val, default, func=None):
		self.var = var
		self.min = min_val
		self.max = max_val
		self.default = default
		self.func = func


# Contains all inputs variables
class Data:
	# @variables is a list of Param objects
	def __init__(self, variables: List[Param]):
		
		# Stores the variables as a dictionary
		self.data = {}
		
		# Stores how to transform (if at all) the raw data from the slider
		self.funcs = {}
		
		# Initialize the data
		for i in variables:
			self.funcs[i.var] = i.func
			self.set_var(i.var, i.min)

	# Returns a list with all the variables values
	def as_list(self):
		return list(map(lambda x: [[x]], [x for x in self.data.values()]))
	
	# Set variable @var to value @value and transform it if necessary
	def set_var(self, var, value):
		if self.funcs[var] is None:
			self.data[var] = value
		else:
			self.data[var] = self.funcs[var](value)


# # Connect to postgres
# conn = psycopg2.connect(database='giswater3', user='postgres', password='postgres', host='localhost')
# cursor = conn.cursor()

# Window class
# Stucture: QWidget formed by two other widgets side by side. The left one has a grid layout to store all the buttons
# and the rigth one only has a label with the network prediction
class Window(QDialog):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.resize(700, 400)
		
		# Load the model with its custom metrics (else it would give an error)
		self.model = load_model('D:/Development/Python/pipeleak-prediction/models/ndvi_7.h5', custom_objects={'diff95': diff95})
		
		self.setAutoFillBackground(True)
		
		pnoms = [6, 10, 16, 25]
		materials = ['PE', 'FIB', 'FO', 'PVC', 'Fe', 'other']
		
		# Store all the sliders you want
		self.params = [
			Param('expl_id',	0,  	23, 	0),
			Param('age', 		0,  	100,	30),
			Param('material',	0,  	5,		4,		lambda x: materials[x]),
			Param('pnom', 		0,  	3,		1,		lambda x: pnoms[x]),
			Param('dnom', 		20, 	900,	200),
			Param('slope', 		0,  	15,		4),
			Param('n_connec',	0,  	30,		2),
			Param('consum',		0,  	40000,	1000),
			Param('length',		1,  	1000,	130),
			Param('ndvi', 		0, 		100,	50, 	lambda x: x / 100)
		]
		
		# Create the data acording to the parametern previously defined
		self.data = Data(self.params)
		
		# Create all the sliders into @input_widget
		input_widget = QWidget()
		input_layout = QGridLayout()
		for i, par in enumerate(self.params):
			
			# Label which displays the name of the variable which is modified by the slider
			name = QLabel(f'{par.var}:')
			name.setFont(QtGui.QFont('consolas', 15))
			
			# Create a slider
			slider = QSlider(Qt.Horizontal)
			slider.setObjectName(f's_{par.var}')
			slider.setRange(par.min, par.max)
			slider.setValue(par.min)
			slider.valueChanged.connect(partial(self.set_data, par.var))
			
			# Create a label which will display the current value of the slider
			value = QLabel(f'{self.data.data[par.var]}')
			value.setFont(QtGui.QFont('consolas', 15))
			value.setObjectName(f'v_{par.var}')
			
			# Add them into the widget
			input_layout.addWidget(name, i, 0)
			input_layout.addWidget(slider, i, 1)
			input_layout.addWidget(value, i, 2)
		
		# Add a push button to randomize the data
		buttons_layout = QHBoxLayout()
		
		rand = QPushButton()
		rand.setObjectName('rand_button')
		rand.setText('Randomize')
		rand.clicked.connect(self.randomize_data)
		
		mean = QPushButton()
		mean.setObjectName('mean_button')
		mean.setText('Default')
		mean.clicked.connect(self.set_default)
		
		buttons_layout.addWidget(rand)
		buttons_layout.addWidget(mean)

		buttons = QWidget()
		buttons.setLayout(buttons_layout)

		input_layout.addWidget(buttons, len(self.params), 1)
		
		input_widget.setLayout(input_layout)
		
		# Labal which will display the prediction of the network
		result = QLabel()
		result.setFont(QtGui.QFont('consolas', 20))
		result.setObjectName('result')
		
		# Set all the widgets
		layout = QHBoxLayout()
		layout.addWidget(input_widget)
		layout.addItem(QSpacerItem(40, 40, QSizePolicy.Preferred))
		layout.addWidget(result)
		
		self.setLayout(layout)
		
		# Claculate the output for the fist time
		self.update()
		
		
	# Set default values
	def set_default(self):
	
		for par in self.params:
			
			slider = self.findChild(QSlider, f's_{par.var}')
			slider.setValue(par.default)
	
	
	# Set every slider to a random value
	def randomize_data(self):
		
		for par in self.params:
			
			slider = self.findChild(QSlider, f's_{par.var}')
			slider.setValue(randint(par.min, par.max))

	# Change @data variable value and updates the label
	def set_data(self, var, value):
		
		self.data.set_var(var, value)
		label = self.findChild(QLabel, f'v_{var}')
		label.setText(str(self.data.data[var]))
		
		self.update()
	
	# Recalculate neural network output, optional: update variable value
	def update(self):
		
		# # The station code for each exploitation_id (ex: expl_id = 0 -> station_code = CL)
		# stations = ['CL', 'U4', 'U4', 'WW', 'U4', 'U4', 'CL', 'VU', 'CL', 'WW', 'WW', 'U4', 'VP', 'VV', 'CL', 'CL', 'U4', 'VP', 'WE', 'CI', 'CI', 'V3', 'CG', 'V5']
		#
		# # Get the temperature table from the database
		# cursor.execute(f"select period, val from api_ws_sample.ext_timeseries")
		# temperature = cursor.fetchall()
		#
		# # Get all variables as a list
		# data = self.data.as_list()
		#
		# # Extract the year and the month to calculate the index of the temperature series
		# year = data[0][0][0]
		# month = data[1][0][0]
		#
		# data.pop(1)
		# data.pop(0)
		#
		# index = (year - 2007) * 12 + month
		#
		# # Get the station code for the current exploitation_id
		# s = stations[self.data.data['expl_id']]
		#
		# # Extract six months of data
		# tmax = [t[1][index - 6: index] for t in temperature if t[0]['id'] == s + 'max']
		# tmin = [t[1][index - 6: index] for t in temperature if t[0]['id'] == s + 'min']
		#
		# # Append the temperature to the static data (pipe propieties)
		# data.append(tmax)
		# data.append(tmin)
		
		# Calculate the output of the network
		output = self.model.predict(norm_input_arr(self.data.as_list()))[0][0]
		
		pal = self.palette()
		
		# r = (output < 0 ? 1: 1 - output) * 255;
		# g = (color > 0 ? 1: 1 + color) * 255;
		# b = (1 - abs(color)) * 255;
		
		r = (1 if output < 0 else output) * 255
		g = (1 if output < 0 else 1 - output) * 255
		b = 0
		
		pal.setColor(self.backgroundRole(), QtGui.QColor(r, g, b))
		
		self.setPalette(pal)
		
		# Set the result label text
		t_result = self.findChild(QLabel, 'result')
		t_result.setText(f"{output:.4f}")


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec_())

while True: pass
