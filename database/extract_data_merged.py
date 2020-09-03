"""
This file will extract the max and min temperature of each station into a .csv file
"""


import csv

stations = ['CL', 'WW', 'U4', 'WE', 'VU', 'CI', 'VP', 'V5', 'VV', 'V3', 'CG']
years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
modes = ['max', 'min']
data = {}

# Read all
for year in years:
	for mode in modes:

		# Open file
		file_name = mode + str(year)
		print(file_name)
		
		reader = csv.reader(open(f'C:/Users/user/Desktop/Data/{file_name}.csv'), delimiter=';')
		
		# For each row check if the station is one of the stations we want to extract
		for row in reader:

			station = row[1]

			if station in stations:

				key = station + mode
				
				# Remove unwanted charcters and replace comma for dot to separate the decimal part
				temp = list(map(lambda x: x.replace('*', '').replace(',', '.').replace('\n', ''), row[3:15]))
				
				# For each unknown value, set it to a value in between the previows and the next one
				for i in range(len(temp)):
					if temp[i] == 'd.i.':
						temp[i] = (float(temp[i - 1]) + float(temp[i + 1])) / 2.0

				temp = list(map(float, temp))
				
				print(f'{key}: {len(temp)}')
				
				# Store the temperature in the @data varaible
				if key in data:
					data[key] += temp
				else:
					data[key] = temp

# Write the @data variable into a file
writer = csv.DictWriter(
	f=open(f'C:/Users/user/Desktop/Data/new/merged.csv', 'w', newline=''),
	fieldnames=data.keys(),
	delimiter=';'
)

writer.writeheader()
writer.writerow(data)

for key, val in data.items():
	print(f'{key}: {len(val)}') 	# This should print a length of 144 (12 months per year with 12 years of data)