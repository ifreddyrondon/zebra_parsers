#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob
import json
import os
import sqlite3 as lite

from datetime import datetime

"""
Get all sqlite databases files that are in the directory where is this script,
from the wireless.ictp.it/tvws/ and transform them to the format accepted
by the zebra application
"""

__author__ = "Freddy Rondón"
__version__ = "1"

FOLDER_NAME = 'parsed'
FILE_NAME = 'zebra_parsed'
EXTENSION = 'json'


def make_sure_path_exists_and_delete_content(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_place(place):
    with open(FOLDER_NAME + '/' + FILE_NAME + '.' + EXTENSION, 'wb') as fp:
        json.dump(place, fp)
    return True


def parser_sqlite_in_current_folder():
    make_sure_path_exists_and_delete_content('./' + FOLDER_NAME)

    # list of files sorted by name
    file_list = glob.glob("*.db")
    file_list.extend(glob.glob('*.DB'))
    file_list = sorted(file_list)

    place = {
        "frequencies": {
            "values": []
        },
        "coordinates": []
    }

    for filename in file_list:
        con = lite.connect(filename)

        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            # get the number of captures for scan
            cur.execute("SELECT nsteps FROM dbmdata")
            captures_4_scan = cur.fetchone()[0]
            # build the list of key for captures values and frequencies values
            captures_keys = []
            frequencies_keys = []
            for value in range(0, captures_4_scan):
                db_capture_key, db_frequency_key = None, None
                if len(str(value)) == 1:
                    db_capture_key = "v00{}".format(value)
                    db_frequency_key = "f00{}".format(value)
                elif len(str(value)) == 2:
                    db_capture_key = "v0{}".format(value)
                    db_frequency_key = "f0{}".format(value)
                elif len(str(value)) == 3:
                    db_capture_key = "v{}".format(value)
                    db_frequency_key = "f{}".format(value)
                captures_keys.append(db_capture_key)
                frequencies_keys.append(db_frequency_key)

            # get the frequencies values
            for fq_key in frequencies_keys:
                query = "SELECT {} FROM config".format(fq_key)
                cur.execute(query)
                place["frequencies"]["values"].append(cur.fetchone()[0])

            # get the captures for scans
            query = "SELECT * FROM dbmdata"
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                row = list(row)
                captures = row[4:captures_4_scan]
                # get the location for loctime, latitude, longitude
                location_id = row[2]
                q2 = "SELECT id, loctime, latitude, longitude FROM location WHERE id = {}".format(location_id)
                cur.execute(q2)
                location = cur.fetchone()
                scan = {
                    "lat": location[2],
                    "lng": location[3],
                    "date": str(datetime.fromtimestamp(location[1]/1000.0)),
                    "cap": captures
                }
                place["coordinates"].append(scan)

    save_place(place)


if __name__ == '__main__':
    parser_sqlite_in_current_folder()
