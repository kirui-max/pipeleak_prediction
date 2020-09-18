"""
This script will calculate the
"""
import sys
sys.path.append("..")

from tensorflow.keras.models import load_model
import psycopg2
from utils import diff95
import pandas
from training.train_minsector_model import norm_inputs
import configparser

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

print('Getting data')

input_names = [
	'expl_id',
	'age',
	'mats',
	'pnom',
	'dnom',
	'uconnec',
	'udemand',
	'slope',
	'elev_delta',
	'press_range',
	'press_mean',
	'press_mean_pnom',
	'press_max_pnom',
	'vel_max',
	'vel_mean',
	'ndvi_mean'
]

cursor.execute(
	f"SELECT "
	f"{', '.join(input_names)}, minsector_id "
	f"FROM ws.v_ai_leak_minsector_raw"
)
rows = cursor.fetchall()
data = list(zip(*rows))

# Get frequency data
minsector_ids = data[-1]
data.pop(-1)

data = dict(zip(input_names, data))
inputs = norm_inputs(data)


print('Creating model')
model = load_model('../models/final.h5', custom_objects={'diff95': diff95})


print('Predicting result')
prediction = model.predict(inputs)


print('Uploading results')
data = []

for minsector_id, pred in zip(minsector_ids, prediction):
	data.append({'minsector_id': minsector_id, 'pred': pred[0]})

pandas.DataFrame(data).to_csv('minsector_output.csv', index=False)

print('Done!')