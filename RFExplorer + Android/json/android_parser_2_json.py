#!/usr/bin/python

import glob
import os
import json

"""
Get all the csv files that are in the directory where is this script, 
from the android application and transform them to the format accepted 
by the zebra application
"""

__author__ = "Freddy Rondon"
__version__ = "2"


FOLDER_NAME = 'parsed'
FILE_NAME = 'zebra_parsed'
EXTENSION = 'json'


class Info:
	def __init__(self, *args, **kwargs):
		self.parsed = 0
		self.samples = 0
		self.status = ""

	def cls(self):
		os.system('cls' if os.name == 'nt' else 'clear')

	def print_info(self, places):
		self.cls()
		print "Number of files parsed: " + str(self.parsed)
		print "Total number of samples: " + str(self.samples) + "\n"

		for i, place in enumerate(places):
			resume = "Place " + str(i + 1) + \
				" range: " + get_frequency_range(place["frequencies"]["values"])

			if i == len(places) - 1:
				resume += " ....." + self.status
			else:
				resume += " .....DONE"

			print resume


def get_frequency_range(l):
	return "[" + str(l[0]) + "-" + str(l[-1]) + "]"


def make_sure_path_exists_and_delete_content(path):
	if not os.path.exists(path):
		os.makedirs(path)


def save_place(places):
	place = places[-1]

	if len(place["coordinates"]) == 0:
		return False

	else:
		num = len(places)

		path = "./" + FOLDER_NAME + "/" + \
			"place_" + str(num) + "_" + \
			get_frequency_range(place["frequencies"]["values"])

		make_sure_path_exists_and_delete_content(path)
		with open(path + '/' + FILE_NAME + '.' + EXTENSION, 'wb') as fp:
			json.dump(place, fp)
		return True


def num(s):
	try:
		return int(s)
	except ValueError:
		return float(s)


def parser_files_in_current_folder():
	make_sure_path_exists_and_delete_content('./' + FOLDER_NAME)

	info = Info()
	info.status = "parsing"

	# list of files sorted by name
	file_list = glob.glob("*.csv")
	file_list.extend(glob.glob('*.CSV'))
	file_list = sorted(file_list)

	places_list = []
	places_list.append({
		"frequencies": {
			"values": []
		},
		"coordinates": []
	})

	# set of frequencies
	cur_frequencies = set()

	for filename in file_list:
		fr = open(filename, 'r')
		for i, line in enumerate(fr):
			data = []
			# values between lines are separeted by ;
			for value in line.split(';'):
				# replace , by .
				value = value.replace(',', '.')
				# delete white spaces
				value = value.strip()
				data.append(value)

			# frequencies
			if len(cur_frequencies) == 0 and i == 0:
				for frequency in data[4:len(data)]:
					fq = num(frequency.replace('.', ''))
					places_list[-1]["frequencies"]["values"].append(fq)

				cur_frequencies = set(places_list[-1]["frequencies"]["values"])

			# cheking frequencies
			elif len(cur_frequencies) > 0 and i == 0:
				frequencies = []
				for frequency in data[4:len(data)]:
					fq = num(frequency.replace('.', ''))
					frequencies.append(fq)

				new_set_frequencies = set(frequencies)
				if cur_frequencies != new_set_frequencies:

					info.status = "saving"
					info.print_info(places_list)
					if save_place(places_list):
						places_list.append({
							"frequencies": {
								"values": frequencies
							},
							"coordinates": []
						})
						cur_frequencies = new_set_frequencies

				else:
					info.status = "parsing"
					info.print_info(places_list)
			# power
			else:
				# check if lat and lng are different from 0
				if float(data[1]) != 0 and float(data[2]) != 0:
					places_list[-1]["coordinates"].append({
						"lat": num(data[1]),
						"lng": num(data[2]),
						"date": str(filename[:-4]),
						"cap": [float(x) for x in data[4:len(data)]]
					})
					info.samples += 1

		fr.close()
		info.parsed += 1
		info.print_info(places_list)

	info.status = "saving"
	info.print_info(places_list)
	save_place(places_list)
	info.status = "DONE"
	info.print_info(places_list)

if __name__ == '__main__':
	parser_files_in_current_folder()
