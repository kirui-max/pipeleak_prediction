import psycopg2
import csv

try:
	conn = psycopg2.connect(database='gw34', user='postgres', password='postgres', host='localhost')

except:
	raise

cursor = conn.cursor()


file = csv.reader(open("D:/Development/Datasets/canonades/nodes.csv"), delimiter=';')
next(file)

# cursor.execute("DELETE FROM ws.t_ndvi")
# cursor.execute("DELETE FROM ws.t_elevation")
cursor.execute("DELETE FROM ws.node")

for row in file:
	
	print(row)
	
	# true_id = row[1].split('_')[0]
	#
	# if 'VN' in true_id:
	# 	continue
	#
	# sql = f"INSERT INTO ws.t_elevation VALUES({row[0]}, '{row[1]}', {row[2]}, {true_id})"
	
	# if row[4] == '':
	# 	row[4] = 0

	# sql = f"INSERT INTO ws.t_ndvi VALUES('{row[0]}', {row[1]}, '{row[2]}', {row[3]}, {row[4]})"
	
	sql = f"INSERT INTO ws.node VALUES('{row[0]}', '{row[1]}')"
	
	cursor.execute(sql)

conn.commit()