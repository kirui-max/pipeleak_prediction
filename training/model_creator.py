"""
This script abstracts the creation of a tf.keras model
"""

from tensorflow.python.keras.api._v2.keras.models import Model
from tensorflow.python.keras.api._v2.keras.layers import Input, Dense, Dropout, Embedding, Concatenate, Flatten

# Stores the input and output of each input
class ModelInput:
	def __init__(self, input, output):
		self.input = input
		self.output = output

# Abstraction to create a model
class MakeModel:
	
	def __init__(self):
		self.inputs = []
	
	# Add @n float inputs
	def add_numeric_input(self, name, n=1):
		
		x = Input((n,), name=name)
		self.inputs.append(ModelInput(x, x))
	
	# Add @n categorical inputs with @categories_count categories
	def add_categorical_input(self, name, categories_count, n=1):
		
		x = Input((n,), dtype='int32', name=name)
		h_x = Embedding(categories_count, 1, name=f'emb_{name}')(x)
		h_x = Flatten(name=f'float_{name}')(h_x)
		
		self.inputs.append(ModelInput(x, h_x))
	
	# Concatenate the inputs and make the hidden layers. It return an uncompiled model
	def make_model(self, layers, dropout) -> Model:
		
		concatenated = Concatenate(name='concatenated')([i.output for i in self.inputs])
		
		pre_layer = concatenated
		for i, units in enumerate(layers):
			
			pre_layer = Dense(units, activation='relu', name=f'dense_{i}')(pre_layer)
				
			if dropout != 0:
				pre_layer = Dropout(dropout)(pre_layer)
		
		output = Dense(1, activation='sigmoid', name='output')(pre_layer)
		
		return Model([i.input for i in self.inputs], output)