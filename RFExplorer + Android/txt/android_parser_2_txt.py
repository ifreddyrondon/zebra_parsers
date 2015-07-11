import glob
import os
import datetime

"""
Get all the csv files that are in the directory where is this script, 
from the android application and transform them to the format accepted 
by the zebra application
"""

__author__ = "Freddy Rondon"
__version__ = "1"

FOLDER_NAME = 'parsed'
EXTENSION = 'txt'


def make_sure_path_exists(path):
	if not os.path.exists(path):
		os.makedirs(path)


def parser_files_in_current_folder():
	make_sure_path_exists('./' + FOLDER_NAME)

	numberOfFile = 0
	# list of files sorted by name
	file_list = glob.glob("*.csv")
	file_list.extend(glob.glob('*.CSV'))
	file_list = sorted(file_list)

	for filename in file_list:
		fr = open(filename, 'r')
		for i, line in enumerate(fr):
			splitLine = line.split(';')

			data = []
			power = []
			for value in splitLine:
				# replace , by .
				value = value.replace(',', '.')
				# delete white spaces
				value = value.strip()
				data.append(value)

			# frequencies
			if i == 0:
				frequencies = []
				frequenciesAux = data[4:len(data)]
				for frequency in frequenciesAux:
					frequencies.append(frequency.replace('.', ''))

			# check if lat and lng are 0
			elif float(data[1]) != 0 and float(data[2]) != 0:
				power = data[4:len(data)]
				fw = open(FOLDER_NAME + '/' + str(numberOfFile) + '.' + EXTENSION, "w")

				for i, frequency in enumerate(frequencies):
					fw.write(str(frequency) + '\t' + str(power[i]) + '\n')

				# we write the latitude and longitude
				fw.write(str(data[1]) + '\n')
				fw.write(str(data[2]) + '\n')

				# we write a fake date
				fw.write(str(datetime.datetime.now()))

				# close the sample file
				fw.close()

				numberOfFile += 1

		fr.close()

if __name__ == '__main__':
	parser_files_in_current_folder()
