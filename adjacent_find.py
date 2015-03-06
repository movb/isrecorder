__author__ = 'mike'

import argparse
import os.path
import sys
from db import *
from models import *
from datetime import datetime, timedelta, date


def find_time(max_time_delta, playlist_name):
    session = DataBase.get_session()()
    prev_elem = None
    for x in session.query(SimplePlaylist).filter(SimplePlaylist.name == playlist_name).all():
        if prev_elem:
            if x.date - prev_elem.date > timedelta(0, max_time_delta):
                print("Found time difference {0}".format(x.date - prev_elem.date))
                print("{0} - {1}\n{2}".format(prev_elem.id, prev_elem.date, prev_elem.body))
                print("-------------------------------------------------------------------")
                print("{0} - {1}\n{2}\n".format(x.id, x.date, x.body))

            if prev_elem.body.splitlines()[-1] != x.body.splitlines()[-1]:
                prev_elem = x
        else:
            prev_elem = x


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Istream HLS Session Replayer.')
    parser.add_argument('session', help='recorded session name')
    parser.add_argument('-f', '--folder', help='session folder')
    parser.add_argument('-t', '--time', help='max time delta between consecutive rows (seconds)')
    parser.add_argument('-p', '--playlist', help='playlist name')

    args = parser.parse_args()

    folder = './sessions'

    if args.folder:
        folder = args.folder

    session_folder = os.path.join(folder, args.session)

    if not os.path.exists(session_folder):
        print "Cannot open folder %s" % session_folder
        sys.exit(0)

    DataBase = DB('sqlite:///{0}/session.db'.format(session_folder))

    if args.time and args.playlist:
        find_time(int(args.time), args.playlist)
