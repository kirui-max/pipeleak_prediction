"""
This script trains a model with data from the database
"""

import sys
sys.path.append("..")

import warnings
import logging
warnings.simplefilter('ignore')

import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import psycopg2
import datetime

from utils import *

from tensorflow.python.keras.callbacks import TensorBoard, ModelCheckpoint

logging.getLogger('tensorflow').disabled = True

from training.model_creator import MakeModel

# Stores diferent onfiguration variables
class Config:
	def __init__(self, layers, dropout, batch_size, epochs):
		self.layers = layers
		self.dropout = dropout
		self.batch_size = batch_size
		self.epochs = epochs


# Generator of training and validation data
def generator(batch_size, validation=False):
	if validation:
		table = 'valid'
	else:
		table = 'train'
	
	# Connect to the database
	conn = psycopg2.connect(database='gw34', user='postgres', password='postgres', host='localhost')
	cursor = conn.cursor()
	
	# Get the temperature data
	# cursor.execute(f"select period, val from api_ws_sample.ext_timeseries")
	# temperature = cursor.fetchall()
	
	# Forever keep sending new batchs of data
	while True:
		
		# Select half a batch of broken pipes and the other hald of never borken pipes
		cursor.execute(
			f"(SELECT n_expl_id, age, material, pnom, dnom, slope, n_connec, consum, length, ndvi, true as broke "
			f"FROM ws.v_ai_pipeleak_{table}_leak "
			f"ORDER BY random() LIMIT {batch_size // 2}) "
			f"UNION "
			f"(SELECT n_expl_id, age, material, pnom, dnom, slope, n_connec, consum, length, ndvi, false as broke "
			f"FROM ws.v_ai_pipeleak_{table}_noleak "
			f"ORDER BY random() LIMIT {batch_size // 2})")
		rows = cursor.fetchall()
		data = list(zip(*rows))
		
		# Get aditional data
		result = data[-1]  		# Did it break?
		
		# Delete this aditional data from main inputs
		data.pop(-1)
		
		# Extract the temperature data 6 months prior the break
		# tmax = []
		# tmin = []
		#
		# for s, date in zip(station_id, broken_date):
		# 	index = (date.year - 2007) * 12 + date.month
		#
		# 	tmax.append([t[1][index - 6: index] for t in temperature if t[0]['id'] == s + 'max'][0])
		# 	tmin.append([t[1][index - 6: index] for t in temperature if t[0]['id'] == s + 'min'][0])
		#
		# data.append(tmax)
		# data.append(tmin)
		
		# Send the the inputs and the targets
		yield norm_input_arr(data), list(map(float, result))


# To be able to test diferent models: loop througth every convination of dropout and structure of the network
dropouts = [0]
# structures = [[32], [32, 64], [64, 128]]
structures = [[32]]

for dropout in dropouts:
	for structure in structures:
		
		cfg = Config(layers=structure, dropout=dropout, batch_size=1024, epochs=15)
		
		# Create the model
		creator = MakeModel()
		
		creator.add_categorical_input('expl_id', 24)
		creator.add_numeric_input('age')
		creator.add_categorical_input('material', 6)
		creator.add_numeric_input('pnom')
		creator.add_numeric_input('dnom')
		creator.add_numeric_input('slope')
		creator.add_numeric_input('n_connec')
		creator.add_numeric_input('consum')
		creator.add_numeric_input('length')
		creator.add_numeric_input('ndvi')
		# creator.add_numeric_input('tmax', n=6)
		# creator.add_numeric_input('tmin', n=6)
		
		model = creator.make_model(layers=cfg.layers, dropout=cfg.dropout)
		
		model.compile(
			optimizer='adam',
			loss='binary_crossentropy',
			metrics=['acc', 'mae', diff95]
		)
		
		# Create model name
		DATE = datetime.datetime.now().strftime('%d%m%Y_%H%M%S')
		NAME = f"ndvi-layers={cfg.layers}-dropout={cfg.dropout}-time={DATE}"
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
			filepath=os.path.join(save_dir, 'checkp_{epoch:02d}-{val_acc:.3f}.hdf5'),
			monitor='val_acc',
			save_best_only=True,
			verbose=0,
			save_weights_only=True
		)
		
		# Train the model
		model.fit_generator(
			generator=generator(batch_size=cfg.batch_size),
			validation_data=generator(batch_size=200, validation=True),
			validation_steps=5,
			steps_per_epoch=100,
			epochs=cfg.epochs,
			callbacks=[tb, cp]
		)
		
		# Save the model
		model.save(os.path.join(save_dir, 'final.h5'))
