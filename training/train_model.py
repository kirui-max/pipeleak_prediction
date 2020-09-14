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

from utils import map_func, scale, diff95

import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.python.keras.callbacks import TensorBoard, ModelCheckpoint

from training.model_creator import MakeModel

# Stores diferent onfiguration variables
class Config:
	def __init__(self, optimizer, layers, dropout, activation, batch_size, epochs):
		self.optimizer = optimizer
		self.layers = layers
		self.dropout = dropout
		self.activation = activation
		self.batch_size = batch_size
		self.epochs = epochs
		
	def as_string(self):
		return f"opt={self.optimizer}-layers={self.layers}-drop={self.dropout}-activ={self.activation}-bs={self.batch_size}-epochs={self.epochs}"


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
	
	# Connect to the database
	conn = psycopg2.connect(database='gw34', user='postgres', password='postgres', host='localhost')
	cursor = conn.cursor()
	
	# Forever keep sending new batchs of data
	while True:
		
		cursor.execute(
			f"SELECT "
			f"{', '.join(input_names)}, frequency "
			f"FROM ws.v_ai_leak_minsector_{table} "
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


# To be able to test diferent models: loop througth every convination of dropout and structure of the network
optimizers = ['adam']
dropouts = [0]
structures = [[16]]
activations = ['relu']
batch_sizes = [128]
	
for opt, drop, stru, activ, bs in itertools.product(*[optimizers, dropouts, structures, activations, batch_sizes]):
		
	cfg = Config(optimizer=opt, layers=stru, dropout=drop, activation=activ, batch_size=bs, epochs=20)
	
	# Create the model
	creator = MakeModel()
	
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
	
	input_names = [i.name for i in creator.inputs]
	
	model = creator.make_model(layers=cfg.layers, dropout=cfg.dropout, activation=cfg.activation)
	
	model.compile(
		optimizer=cfg.optimizer,
		loss='mse',
		metrics=[tf.metrics.MeanAbsoluteError(), tf.metrics.RootMeanSquaredError()]
	)
	
	# Create model name
	DATE = datetime.datetime.now().strftime('%d%m%Y_%H%M%S')
	NAME = f"{cfg.as_string()}-time={DATE}"
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