"""
This script analizes the database and
"""

import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

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


# condition = "mean is not null"
# condition = "consum < 30000 and consum > 50"

# table = "ws.v_ai_pipeleak_main_leak a join ai_ndvi b on (a.id = b.arc_id)"
main_leak = "ws.v_ai_pipeleak_main_leak"
main_noleak = "ws.v_ai_pipeleak_main_noleak"
condition = "length < 1000 and length > 0"

# plot_dist('age', table, distinct='distinct on (age)')

plot_dist('age', main_leak, condition=condition, distinct='distinct on (id, data)')

plot_dist('age', main_noleak, condition=condition, distinct='distinct on (id, data)')

# table = "api_ws_sample.v_ai_pipeleak_main_noleak a join ai_ndvi b on (a.id = b.arc_id)"
# plot_dist('mean', table, condition)

plt.tight_layout()
plt.show()