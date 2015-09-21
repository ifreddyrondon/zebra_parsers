#!/usr/bin/python

import glob
import os
import json
from datetime import datetime

"""
Get the JSON file from Android Hunter app inside the current directory and
transform them to the format accepted by the zebra application, the script will
generate 2 files "zebra+power.json" and "zebra+ap.json", the zebra+power file
includes within its arrays of captures the power of the ap, on the other hand
the zebra+ap file include inside within its arrays of captures the number of ap
that was found in the scan.
"""

__author__ = "Freddy Rondon"
__version__ = "3"


FOLDER_NAME = 'parsed'
FILE_NAME = ['zebra+power', 'zebra+ap']
EXTENSION = 'json'
LOWER_POWER_VALUE = -120
# default value in case that the input file does not provide it
SCAN_TYPE = "outdoor"


class Info:
    def __init__(self, *args, **kwargs):
        self.parsed = 0
        self.samples = 0
        self.status = ""

    def print_info(self):
        print "Number of samples: " + str(self.samples + 1)
        print "Number of files parsed: " + str(self.parsed)
        print self.status


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def make_sure_path_exists_and_delete_content(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_place(place, file_name):
    with open(FOLDER_NAME + '/' + file_name + '.' + EXTENSION, 'wb') as fp:
        json.dump(place, fp)
    return True


def parser_files_in_current_folder():
    make_sure_path_exists_and_delete_content('./' + FOLDER_NAME)
    info = Info()
    info.status = "parsing"

    # list of files sorted by name
    file_list = glob.glob("*.json")
    file_list.extend(glob.glob('*.JSON'))
    file_list = sorted(file_list)

    # central channels band 2.4 GHz
    frequencies_2_4 = [
        2412, 2417, 2422, 2427, 2432, 2437, 2442,
        2447, 2452, 2457, 2462, 2467, 2472, 2484
    ]

    # central channels band 5 GHz
    frequencies_5 = [
        5170, 5180, 5190, 5200, 5210, 5220, 5230, 5240, 5260, 5280,
        5300, 5320, 5500, 5520, 5540, 5560, 5580, 5600, 5620, 5640,
        5660, 5680, 5700, 5745, 5765, 5785, 5805, 5825
    ]

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

    # set default SCAN_TYPE
    scan_type = SCAN_TYPE

    for filename in file_list:
        fr = open(filename, 'r')
        data = json.load(fr)

        try:
            scan_type = data["scan_type"]
        except Exception:
            pass

        for leg in data["legs"]:
            for map in leg["map"]:
                if "coordinates" not in map or \
                    "date" not in map or \
                    "freq" not in map or \
                        "power" not in map:
                    continue

                lat = num(map["coordinates"]["lat"])
                lng = num(map["coordinates"]["lng"])
                if scan_type == "outdoor" and (lat == 0 or lng == 0):
                    continue

                date = datetime.fromtimestamp(
                    int(map["date"]) / 1e3
                ).strftime('%Y-%m-%d %H:%M:%S')

                # get sames frequencies in the scan
                fq_dict = {}
                for fq in frequencies:
                    fq = str(fq)
                    fq_dict[fq] = [
                        i for i, x in enumerate(map["freq"]) if x == fq]

                # get and save captures for ap
                cap = []
                for value in fq_dict.itervalues():
                    cap.append(len(value))
                ap_place['coordinates'].append({
                    "lat": lat,
                    "lng": lng,
                    "date": date,
                    "cap": cap
                })

                # get and save captures for power
                for value in fq_dict.itervalues():
                    if len(value) > 0:
                        for index in value:
                            cap = [-120] * len(frequencies)
                            index_fq_ordered = frequencies.index(
                                num(map["freq"][index])
                            )
                            cap[index_fq_ordered] = num(map["power"][index])

                            power_place['coordinates'].append({
                                "lat": lat,
                                "lng": lng,
                                "date": date,
                                "cap": cap
                            })

        info.parsed += 1
        fr.close()

    save_place(power_place, FILE_NAME[0])
    save_place(ap_place, FILE_NAME[1])
    info.status = "DONE"
    info.print_info()


if __name__ == '__main__':
    parser_files_in_current_folder()
