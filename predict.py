"""
This script will calculate the
"""

import warnings
warnings.simplefilter('ignore')

import tensorflow as tf

from tensorflow.python.keras.api._v2.keras.models import load_model, Model
import datetime
import psycopg2
from utils import norm_input_arr, diff95
import json
import csv
import pandas

import logging
logging.getLogger('tensorflow').disabled = True

# Connect to the database
conn = psycopg2.connect(database='giswater3', user='postgres', password='postgres', host='localhost')
cursor = conn.cursor()

print('Getting data')
date = datetime.date(2019, 8, 19)
cursor.execute(
	f"SELECT id, builtdate, expl_n_id, material, pnom, dnom, slope, n_connec, consum, length, mean "
	f"FROM "
	f"(select * from api_ws_sample.v_ai_pipeleak_main_leak "
	f"UNION "
	f"select * from api_ws_sample.v_ai_pipeleak_main_noleak) a "
	f"JOIN ai_ndvi b ON (a.id = b.arc_id) WHERE mean is not null "
	f"order by random()"
)

data = cursor.fetchall()

data = list(zip(*data))
ages = [(datetime.datetime.now().date() - x) / datetime.timedelta(days=365) for x in data[1]]
ids = data[0]

data.pop(1)
data.pop(0)

data.insert(1, ages)

inputs = [list(map(lambda i: [i], x)) for x in data]

print('Creating model')
model = tf.keras.models.load_model('models/ndvi_5.h5', custom_objects={'diff95': diff95})

print('Predicting result')
prediction = model.predict(norm_input_arr(inputs))

# print('Calculating tolerance')
# cursor.execute(
# 	"(SELECT expl_n_id, age, material, pnom, dnom, slope, n_connec, consum, length, true as broke "
# 	"FROM api_ws_sample.v_ai_pipeleak_valid_leak "
# 	"ORDER BY random()) "
# 	"UNION "
# 	"(SELECT expl_n_id, age, material, pnom, dnom, slope, n_connec, consum, length, false as broke "
# 	"FROM api_ws_sample.v_ai_pipeleak_valid_noleak "
# 	"ORDER BY random()) limit 5"
# )
#
# rows = cursor.fetchall()
# valid = list(zip(*rows))
# optimal = list(map(lambda i: [float(i)], valid[-1]))
# valid.pop(-1)
#
# valid = [list(map(lambda i: [i], x)) for x in valid]
#
# print(valid)
# print(optimal)
#
# metrics = model.metrics_names
#
# accuracy = model.evaluate(norm_input_arr(valid), optimal, verbose=0)[metrics.index('acc')]
# tolerance = 1 - accuracy
tolerance = 0.3

print('Uploading results')
cursor.execute('DELETE FROM api_ws_sample.audit_log_data WHERE fprocesscat_id = 48 and user_name = current_user')

data = []

for arc_id, pred in zip(ids, prediction):
	data.append({'arc_id': arc_id, 'pred': pred[0]})

pandas.DataFrame(data).to_csv('testtt.csv', index=False)

# file = csv.DictWriter(open("test.csv", 'w'), fieldnames=["arc_id", "pred"])
# for x in data:
# 	file.writerow(x)

# for arc_id, pred in zip(ids, prediction):
# 	log_message = dict()
# 	log_message['value'] = float(pred[0])
# 	log_message['period'] = '1-0'
# 	log_message['start'] = date.strftime('%m-%Y')
# 	log_message['end'] = date.strftime('%m-%Y')
# 	log_message['tolerance'] = tolerance
#
# 	cursor.execute(
# 		f"INSERT INTO api_ws_sample.audit_log_data"
# 		f"(fprocesscat_id, feature_type, feature_id, log_message) "
# 		f"VALUES "
# 		f"(48, 'arc', {arc_id}, '{json.dumps(log_message)}')"
# 	)
#
# conn.commit()
#
# print('Finished')


"""
where fprocesscat_id = 48 and user_name = current_user()

table = audit_log_data
fprocesscat_id = 48
feature_type = 'arc'
feature_id = arc_id

log:
value
period
start
end
tolerance
"""