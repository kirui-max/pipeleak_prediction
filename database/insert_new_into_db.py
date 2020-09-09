import psycopg2
import numpy as np
import time
import csv

# Connect to postgres
try:
	conn = psycopg2.connect(database='gw34', user='postgres', password='postgres', host='localhost')
	cursor = conn.cursor()

except:
	raise


'''
class Pipe:
	def __init__(self):
		self.segments = []
		self.node1 = None
		self.node2 = None


print("Getting raw data...")
cursor.execute("select * from ws.t_links_raw")
data = cursor.fetchall()



print("Organizing segments...")
result = dict()
for pipe in data:
	
	id = pipe[1].split('P')[0]
	
	if '_' in id:
		continue
	
	if id not in result:
		result[id] = Pipe()

	result[id].segments.append(pipe[1])



print("Getting arc nodes...")
list_to_remove = []
for id, info in result.items():
	
	cursor.execute(f"select node_1, node_2 from ws.arc where arc_id = '{id}'")
	try:
		nodes = cursor.fetchall()[0]
		info.node1 = nodes[0]
		info.node2 = nodes[1]
	except:
		list_to_remove.append(id)

for id in list_to_remove:
	result.pop(id)


# Function to retrieve pressure data from node
def get_node_data(node_id: str):
	
	cursor.execute(f"SELECT * FROM ws.t_nodes_raw WHERE node_id = '{node_id}'")
	node = cursor.fetchall()
	try:
		node = np.array(node)[:,7:-2]
		node = np.array([list(map(float, x)) for x in node])
		if node.shape[0] > 1:
			node = np.max(node, axis=0)
		else:
			node = node[0]
	except:
		print(id, info.node1, node)
		list_to_remove.append(id)
		return None
	
	return node


print("Retrieving organized data...")
list_to_remove = []
for i, (id, info) in enumerate(result.items()):
	
	if i % 1000 == 0:
		print(i)
	
	cursor.execute(f"SELECT * FROM ws.t_links_raw WHERE c_link_nom_ = ANY(ARRAY{info.segments})")
	segs_data = cursor.fetchall()
	
	vel_data = []
	for seg in segs_data:
		vel_data += seg[7:]
	
	vel_data = list(map(float, vel_data))
	vel_data = np.array(vel_data)
	
	
	node1 = get_node_data(info.node1)
	node2 = get_node_data(info.node2)

	if node1 is None or node2 is None:
		continue

	press_data = np.mean(np.array([node1, node2]), axis=0)

	press_min = np.min(press_data)
	press_max = np.max(press_data)
	press_mean = np.mean(press_data)
	
	vel_min = np.min(vel_data)
	vel_max = np.max(vel_data)
	vel_mean = np.mean(vel_data)
	
	sql = f"INSERT INTO ws.ai_hydraulics VALUES('{id}', " \
		  f"NULL, NULL, NULL, " \
		  f"{press_min}, {press_max}, {press_mean}, " \
		  f"{vel_min}, {vel_max}, {vel_mean})"
	cursor.execute(sql)

conn.commit()

	# print(speed_mean, speed_delta)
	# print(press_mean, press_delta)
	
	# sql = f"INSERT INTO ws.t_link_info VALUES('{id}', ARRAY{data.segments}, '{data.node1}', '{data.node2}');"
	#
	# cursor.execute(sql)
#
# conn.commit()

# print(result['153497'])
# print(result['127345'])



'''


file = csv.reader(open("D:/Development/Datasets/canonades/presszone.csv"), delimiter=';')
next(file)

cursor.execute("DELETE FROM ws.t_presszone")

for i, row in enumerate(file):
	
	if (i % 100 == 0):
		print(i)

	if (row[2] == ''):
		continue
		

	sql = f"INSERT INTO ws.t_presszone VALUES({row[0]}, '{row[1]}', {row[2]}, '{row[3]}')"
	# sql = f"UPDATE ws.t_ai_pipeleak_raw_all SET minsector_id = {row[2]} WHERE arc_id = '{row[1]}'"
	
	# print(sql)
	
	cursor.execute(sql)

conn.commit()

'''
file = csv.reader(open("D:/Development/Datasets/canonades/XARXA_NODE.txt"), delimiter=',')
for row in file:

	sql = "INSERT INTO ws.t_nodes_raw VALUES(\n'"
	sql += "', '".join(row)
	sql += "');"
	
	# print(sql)
	
	cursor.execute(sql)

conn.commit()


file = csv.reader(open("D:/Development/Datasets/canonades/XARXA_LINK.txt"), delimiter=',')
for row in file:
	
	print(row)
	
	sql = f"CREATE TABLE t_nodes_raw (\n"
	for val in row:
		if val == '':
			val = 'id'
		sql += f"{val} text, \n"
		
	sql += ")"
	
	sql = sql.replace('.', '_')
	
	print(sql)
	
	exit()
	


cursor.execute("select * from ws.t_nodes_raw")
data = cursor.fetchall()
for row in data:
	
	id = row[1].split('_')[0]
	# print(id)
	
	cursor.execute(f"update ws.t_nodes_raw set node_id = '{id}' where c_node_nom_ = '{row[1]}'")

conn.commit()

'''