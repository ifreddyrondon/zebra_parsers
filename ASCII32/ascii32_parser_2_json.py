#!/usr/bin/python

import glob
import os
import json

"""
Get all the txt files that are in the directory where is this script, 
from the ASCII32 and transform them to the format accepted 
by the zebra application
"""

__author__ = "Freddy Rondon"
__version__ = "1"

FOLDER_NAME = 'parsed'
FILE_NAME = 'zebra_parsed'
EXTENSION = 'json'


class Info:
    def __init__(self, *args, **kwargs):
        self.parsed = 0
        self.samples = 0
        self.status = ""

    def print_info(self):
        print "Number of samples: " + str(self.samples + 1)
        print "Number of files parsed: " + str(self.parsed)
        print self.status


def make_sure_path_exists_and_delete_content(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_place(place):
    with open(FOLDER_NAME + '/' + FILE_NAME + '.' + EXTENSION, 'wb') as fp:
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
    file_list = glob.glob("*.txt")
    file_list.extend(glob.glob('*.TXT'))
    file_list = sorted(file_list)

    place = {
        "frequencies": {
            "values": []
        },
        "coordinates": []
    }

    # set of frequencies to compare
    frequencies_cmp = set()

    for filename in file_list:
        frequencies = []
        captures = []

        fr = open(filename, 'r')
        for line in fr:
            data = []
            # values between lines are separeted by ,
            for value in line.split(','):
                # delete white spaces
                value = value.strip()
                data.append(value)

            # capture
            if len(data) == 2:
                frequencies.append(num(data[0]))
                captures.append(num(data[1]))

            # coordinate
            elif len(data) == 5:
                # save the frequencies just once for compare and save just once in json
                if len(frequencies_cmp) == 0:
                    frequencies_cmp = set(frequencies)
                    # save the frequencies values for the first time
                    place["frequencies"]["values"] = frequencies

                # check if frequencies are equals
                if frequencies_cmp == set(frequencies):
                    # calculate lat
                    minutelat = num(data[3].split('.')[0]) / 100.0
                    declat = num("0." + data[3].split('.')[1])
                    lat = int(minutelat) + (100 * (minutelat - int(minutelat)) + declat) / 60.0

                    # calculate lng
                    minutelon = num(data[4].split('.')[0]) / 100.0
                    declon = num("0." + data[4].split('.')[1])
                    lng = int(minutelon) + (100 * (minutelon - int(minutelon)) + declon) / 60.0
                    lng *= -1

                    # capture date
                    date = data[1][:2] + "/" + data[1][2:4] + "/" + data[1][4:6] + \
                           " " + data[2][:2] + ":" + data[2][2:4] + ":" + data[1][4:]

                    # save the coord whit caps
                    place["coordinates"].append({
                        "lat": lat,
                        "lng": lng,
                        "date": date,
                        "cap": captures
                    })
                    info.samples += 1

                # reset frequencies and captures
                frequencies = []
                captures = []

        fr.close()
        info.parsed += 1
        info.print_info()

    info.status = "saving"
    info.print_info()
    save_place(place)
    info.status = "DONE"
    info.print_info()


if __name__ == '__main__':
    parser_files_in_current_folder()
