"""
This script trains a model with data from the database
"""

import sys
sys.path.append("..")

import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import psycopg2
import datetime
import itertools

from utils import map_func, scale

import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.python.keras.callbacks import TensorBoard, ModelCheckpoint

from training.model_creator import MakeModel

import configparser

# Stores diferent onfiguration variables
class Config:
	def __init__(self, optimizer, layers, dropout, activation, batch_size, epochs, loss):
		self.optimizer = optimizer
		self.layers = layers
		self.dropout = dropout
		self.activation = activation
		self.batch_size = batch_size
		self.epochs = epochs
		self.loss = loss

	def as_string(self):
		return f"opt={self.optimizer}-layers={self.layers}-drop={self.dropout}-activ={self.activation}" \
			   f"-bs={self.batch_size}-loss={self.loss}-epochs={self.epochs}"

# Set normalize inputs
def norm_inputs(inputs: dict):
	
	def norm_expl_id(x): 			return x
	def norm_age(x): 				return scale(float(x), 0, 70)
	def norm_mats(x): 				return map_func(float, x)
	def norm_pnom(x): 				return scale(float(x), 0, 16)
	def norm_dnom(x):				return scale(float(x), 0, 300)
	def norm_uconnec(x):			return scale(float(x), 0, 0.05)
	def norm_udemand(x):			return scale(float(x), 0, 20)
	def norm_slope(x):				return scale(float(x), 0, 20)
	def norm_elev_delta(x):			return scale(float(x), -150, 150)
	def norm_press_range(x):		return scale(float(x), 0, 30)
	def norm_press_mean(x):			return scale(float(x), 0, 120)
	def norm_press_mean_pnom(x):	return scale(float(x), 0, 1)
	def norm_press_max_pnom(x):		return scale(float(x), 0, 1)
	# def norm_vel_min(x):			return float(x)
	def norm_vel_max(x):			return scale(float(x), 0, 2.5)
	def norm_vel_mean(x):			return scale(float(x), 0, 2.5)
	def norm_ndvi_mean(x):			return scale(float(x), 0, 0.25)
	
	for key in inputs.keys():
		func = locals()[f'norm_{key}']
		inputs[key] = map_func(func, inputs[key])
	
	return tuple(inputs.values())


# Generator of training and validation data
def generator(batch_size, input_names, validation=False):
	if validation:
		table = 'valid'
	else:
		table = 'train'

	# getting conn parameters
	parser = configparser.ConfigParser()
	parser.read('../config.conf')
	host = parser.get(section='CONNECTION', option='host')
	port = parser.get(section='CONNECTION', option='port')
	db = parser.get(section='CONNECTION', option='db')
	user = parser.get(section='CONNECTION', option='user')
	password = parser.get(section='CONNECTION', option='password')
	schema_name = parser.get(section='OTHER', option='schema_name')

	# Connect to the database
	conn = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)
	cursor = conn.cursor()
	
	# Forever keep sending new batchs of data
	while True:
		
		cursor.execute(
			f"SELECT "
			f"{', '.join(input_names)}, frequency "
			f"FROM {schema_name}.v_ai_leak_minsector_{table} "
			f"ORDER BY random() LIMIT {batch_size}"
		)
		rows = cursor.fetchall()
		data = list(zip(*rows))
		
		# Get frequency data
		frequency = data[-1]
		data.pop(-1)
		
		data = dict(zip(input_names, data))
		inputs = norm_inputs(data)

		target = np.array(list(map(float, frequency)))
		
		# Send the the inputs and the targets
		yield inputs, target


if __name__ == '__main__':

	# Set model parameters: To be able to test diferent models: loop througth every convination of dropout and structure of the network

	# dynamic variables
	optimizers = ['adam']		# Model optimizer
	dropouts = [0]				# Dropout percent
	structures = [[16]]			# Number of neurons per layer
	activations = ['relu']		# Hidden layers activation
	batch_sizes = [128]			# Batch size
	losses = [					# Losses function
		'mse'
	]

	# statics variables (not used on loop)
	epochs = 3 					# Number of epochs
	metrics = [					# Metrics parameters.
		tf.metrics.MeanSquaredError(),
		tf.metrics.RootMeanSquaredError()
	]


	for opt, drop, stru, activ, bs, loss in itertools.product(*[optimizers, dropouts, structures, activations, batch_sizes, losses]):

		cfg = Config(optimizer=opt, layers=stru, dropout=drop, activation=activ, batch_size=bs, epochs=epochs, loss=loss)
		
		# Create the model
		creator = MakeModel()
		
		# Set model inputs
		creator.add_categorical_input('expl_id', 25)
		creator.add_numeric_input('age')
		creator.add_numeric_input('mats', n=6)
		creator.add_numeric_input('pnom')
		creator.add_numeric_input('dnom')
		creator.add_numeric_input('uconnec')
		creator.add_numeric_input('udemand')
		creator.add_numeric_input('slope')
		creator.add_numeric_input('elev_delta')
		creator.add_numeric_input('press_range')
		creator.add_numeric_input('press_mean')
		creator.add_numeric_input('press_mean_pnom')
		creator.add_numeric_input('press_max_pnom')
		# creator.add_numeric_input('vel_min')
		creator.add_numeric_input('vel_max')
		creator.add_numeric_input('vel_mean')
		creator.add_numeric_input('ndvi_mean')
		
		# Get all input names
		input_names = [i.name for i in creator.inputs]
		
		# Construct the model
		model = creator.make_model(layers=cfg.layers, dropout=cfg.dropout, activation=cfg.activation, output_activation='relu')
		
		# Compile the model
		model.compile(
			# Choose optimizer function
			optimizer=cfg.optimizer,
			# Choose losses function
			loss=cfg.loss,
			# Choose parameter(s) to metrics
			metrics=metrics
		)
		
		# Create model name
		DATE = datetime.datetime.now().strftime('%d%m%Y_%H%M%S')
		NAME = f"minsector-{cfg.as_string()}-time={DATE}"
		print(NAME)
		
		# Make logs direcories
		log_dir = os.path.join('logs', NAME)
		save_dir = os.path.join('saves', NAME)
		
		os.makedirs(log_dir)
		os.makedirs(save_dir)
		
		# Callback to be able to see error graphs
		tb = TensorBoard(
			log_dir=log_dir,
			profile_batch=0
		)
		
		# Callback which saves the best model based on the accuracy on the validation data
		cp = ModelCheckpoint(
			filepath=os.path.join(save_dir, 'checkp_{epoch:02d}-{val_loss:.3f}.hdf5'),
			monitor='val_loss',
			save_best_only=True,
			verbose=0,
			save_weights_only=False
		)
		
		# Train the model
		model.fit(
			x=generator(batch_size=cfg.batch_size, input_names=input_names),
			validation_data=generator(batch_size=200, input_names=input_names, validation=True),
			validation_steps=5,
			steps_per_epoch=300,
			epochs=cfg.epochs,
			callbacks=[tb, cp]
		)
		
		# Save the model
		model.save(os.path.join(save_dir, 'final.h5'))