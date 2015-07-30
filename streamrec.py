__author__ = 'mike'


# /usr/bin/env python

import requests
import argparse
from timer_decorator import setInterval
from models import *
from db import DB
from m3u8 import *
from static_vars import *
import shutil
from os import listdir, makedirs
from os.path import isdir, join, dirname, exists
import signal
from datetime import datetime

DataBase = None
stop_flag = False


def signal_handler(signal, frame):
    global stop_flag
    stop_flag = True
    print('Stopped by Ctrl+C!')


def DEBUG(*args):
    debug = False
    if debug:
        print(args)


def save_keys(body, session):
    keys = playlist_get_keys(body)
    for path, data in keys:
        if session.query(Key).filter(Key.path == path).first():
            continue
        else:
            key = Key(path, data)
            session.add(key)


def save_segments(segments, base_url, session, out_path):
    DEBUG('save segments: segments = {0}, out_path = {1}'.format(segments, out_path))
    out_path = join(out_path, 'chunks')
    for segment in segments:
        segment_name = get_path_from_url(segment)
        DEBUG('segment_name {0}'.format(segment_name))
        if session.query(Segment).filter(Segment.name == segment_name).first():
            continue
        try:
            r = requests.get(make_full_url(segment, base_url), stream=True)
            if r.status_code == 200:
                dir = join(out_path, dirname(get_path_from_url(segment)))
                filename = join(out_path, get_path_from_url(segment))
                if not exists(dir):
                    makedirs(dir)
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                segment_file = Segment(segment_name, get_path_from_url(segment), r.reason, r.status_code)
                session.add(segment_file)
            else:
                DEBUG('STATUS CODE: ', r.status_code)
        except:
            return



def save_streams(streams, base_url, session, out_path):
    DEBUG('save streams: streams = {0}, outpath = {1}'.format(streams, out_path))
    for stream in streams:
        try:
            r = requests.get(make_full_url(stream, base_url))
            playlist_name = get_path_from_url(stream)
            body = r.text
            save_keys(body, session)
            body = remove_sessions(body)

            segments = get_streams(body)
            save_segments(segments, base_url, session, out_path)
        except:
            return


@setInterval(.5)
def dump(url, output_folder):
    DEBUG('dump: url = {0}'.format(url))
    try:
        r = requests.get(url)
        body = r.text

        if is_playlist(body):
            if is_variant(body):
                streams = get_streams(body)
                save_streams(streams[-1:], url, output_folder)
            else:
                save_streams([url], url, output_folder)
    except:
        return


def record_stream(url, output_folder, session_name):
    DEBUG('record stream: url = {0}, output folder = {1}'.format(url, output_folder))

    time_start = datetime.utcnow()
    stop = dump(url, output_folder)

    while True:
        if stop_flag:
            stop.set()
            break

    time_stop = datetime.utcnow()
    print("Record length {0}".format(time_stop - time_start))


def main():
    parser = argparse.ArgumentParser(description='HLS stream recorder.')
    parser.add_argument('url', help='hls input stream')
    parser.add_argument('-o', '--output', help='output folder name')
    parser.add_argument('-s', '--session', help='output session name')

    args = parser.parse_args()

    output_folder = './stream-sessions'

    if args.output:
        output_folder = args.output

    if not args.session:
        if not exists(output_folder):
            makedirs(output_folder)
        folders = [f for f in listdir(output_folder) if isdir(join(output_folder, f))]
        i = 1
        while "session{0}".format(i) in folders:
            i += 1
        session_name = "session{0}".format(i)
    else:
        session_name = args.session

    output = "{0}/{1}".format(output_folder, session_name)
    if not exists(output):
        makedirs(output)

    print('Start recording stream {0} to {1}'.format(session_name, output_folder))
    record_stream(args.url, output, session_name)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
