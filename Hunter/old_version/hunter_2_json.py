#!/usr/bin/python

import glob
import os
import json

"""
Get all the txt files that are in the directory where is this script, from
the android hunter application and transform them to the format accepted by
the zebra application, the script will generate 2 files "zebra+power.json" and
"zebra+ap.json", the zebra+power file includes within its arrays of captures
the power of the ap, on the other hand the zebra+ap file include inside within
its arrays of captures the number of ap that was found in the scan.
"""

__author__ = "Freddy Rondon"
__version__ = "2"


FOLDER_NAME = 'parsed'
FILE_NAME = ['zebra+power', 'zebra+ap']
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


def save_place(place, file_name):
    with open(FOLDER_NAME + '/' + file_name + '.' + EXTENSION, 'wb') as fp:
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

    # central channels band 2.4 GHz
    frequencies_2_4 = [
        2412, 2417, 2422, 2427, 2432, 2437, 2442,
        2447, 2452, 2457, 2462, 2467, 2472, 2484]

    # central channels band 5 GHz
    frequencies_5 = [
        5170, 5180, 5190, 5200, 5210, 5220, 5230, 5240, 5260, 5280,
        5300, 5320, 5500, 5520, 5540, 5560, 5580, 5600, 5620, 5640,
        5660, 5680, 5700, 5745, 5765, 5785, 5805, 5825]

    frequencies = frequencies_2_4 + frequencies_5

    # place for save the number of ap
    power_place = {}
    power_place['frequencies'] = {}
    power_place['frequencies']['values'] = frequencies
    power_place['coordinates'] = []

    # place for save the power of ap
    ap_place = {}
    ap_place['frequencies'] = {}
    ap_place['frequencies']['values'] = frequencies
    ap_place['coordinates'] = []

    # util
    flen = len(power_place['frequencies']['values'])

    for filename in file_list:
        fr = open(filename, 'r')
        for i, line in enumerate(fr):
            data = []
            # values between lines are separeted by tab
            for value in line.split('\t'):
                # delete white spaces
                value = value.strip()
                data.append(value)

            try:
                num(data[0])

            except ValueError:
                date = data[-1][6:]
                # check if there are any AP for the scan, if no remove last
                if len(ap_place['coordinates']) > 0 and len(
                    ap_place['coordinates'][-1]) < 4:
                    ap_place['coordinates'].pop(-1)

                # save new coordinate for place with number of ap
                ap_place['coordinates'].append({
                    "date": date,
                    "cap": [0] * flen
                    })

            else:
                lat = num(data[0])
                lng = num(data[1])

                if lat == 0 or lng == 0:
                    continue

                # save new coordinate for place with power ap
                power_place['coordinates'].append({
                    "lat": lat,
                    "lng": lng,
                    "date": date,
                    "cap": [-120] * flen
                    })

                # get the frequency and the index of the frequency for save the capture
                frequency = num(data[3])
                index = power_place['frequencies']['values'].index(frequency)

                # # save power in capture
                power = num(data[2])
                power_place['coordinates'][-1]["cap"][index] = power
                info.samples += 1

                # check if lat and lng was already saved for place with number of ap
                if "lat" is not ap_place['coordinates'][-1]:
                    ap_place['coordinates'][-1]["lat"] = lat

                if "lng" is not ap_place['coordinates'][-1]:
                    ap_place['coordinates'][-1]["lng"] = lng

                # save number of ap (capture)
                ap_place['coordinates'][-1]["cap"][index] += 1

        info.parsed += 1
        fr.close()

    save_place(power_place, FILE_NAME[0])
    save_place(ap_place, FILE_NAME[1])
    info.status = "DONE"
    info.print_info()

if __name__ == '__main__':
    parser_files_in_current_folder()
