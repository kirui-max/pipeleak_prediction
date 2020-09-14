"""
This script analizes the database and
"""

import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Connect to postgres dataset
try:
	conn = psycopg2.connect(database='gw34', user='postgres', password='postgres', host='localhost')
except:
	raise

cursor = conn.cursor()


# Plots all the data from @table and plots its distribution
def plot_dist(var, table, condition='true', distinct=''):
	
	# Get the data
	sql = f'SELECT {distinct} {var} FROM {table} WHERE {condition}'
	cursor.execute(sql)
	data = cursor.fetchall()
	
	# Get it as an array of values
	data = list(zip(*data))[0]
	
	# Turn it into float
	data = list(map(float, data))
	
	print(f"size: {len(data)}")
	print(f"max: {max(data)}")
	print(f"min: {min(data)}")
	print(f"mean: {sum(data) / len(data)}")
	
	# Plot the data and return de axis
	return sns.distplot(data, kde=False)


plot_dist(
	'frequency',
	'ws.v_ai_leak_minsector',
)

plt.tight_layout()
plt.show()

'''
cursor.execute('SELECT total_length, leaks FROM ws.v_ai_leak_minsector')
data = cursor.fetchall()

# Get it as an array of values
length = list(zip(*data))[0]
leaks = list(zip(*data))[1]

# Turn it into float
length = list(map(float, length))
leaks = list(map(float, leaks))

plt.scatter(length, leaks)
plt.tight_layout()
plt.show()
'''