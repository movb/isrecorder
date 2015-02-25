import requests
import argparse
from timer_decorator import setInterval
from models import *
from db import DB
from m3u8 import *
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


def save_segments(segments, base_url, session, out_path):
    DEBUG('save segments: segments = {0}, out_path = {1}'.format(segments, out_path))
    out_path = join(out_path, 'chunks')
    for segment in segments:
        segment_name = get_path_from_url(segment)
        DEBUG('segment_name {0}'.format(segment_name))
        if session.query(Segment).filter(Segment.name == segment_name).first():
            continue
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



def save_streams(streams, base_url, session, out_path):
    DEBUG('save streams: streams = {0}, outpath = {1}'.format(streams, out_path))
    for stream in streams:
        r = requests.get(make_full_url(stream, base_url))
        playlist_name = get_path_from_url(stream)
        body = r.text
        body = remove_sessions(body)
        sp = session.query(SimplePlaylist).filter(SimplePlaylist.name == get_path_from_url(stream))\
            .order_by(SimplePlaylist.date.desc()).first()
        if sp and sp.body == body:
            return
        simple_pl = SimplePlaylist(playlist_name, body, r.reason, r.status_code)
        session.add(simple_pl)

        segments = get_streams(body)
        save_segments(segments, base_url, session, out_path)


@setInterval(.5)
def dump(url, output_folder):
    DEBUG('dump: url = {0}'.format(url))
    r = requests.get(url)
    session = DataBase.get_session()()
    body = r.text
    body = remove_sessions(body)
    main_pl = MainPlaylist(body, r.reason, r.status_code)
    session.add(main_pl)

    if is_playlist(body):
        if is_variant(body):
            streams = get_streams(body)
            save_streams(streams, url, session, output_folder)
        else:
            save_streams([url], url, session, output_folder)

    session.commit()


def record_session(url, output_folder, session_name):
    DEBUG('record session: url = {0}, output folder = {1}'.format(url, output_folder))
    global DataBase
    DataBase = DB('sqlite:///{0}/session.db'.format(output_folder))
    session = DataBase.get_session()()
    meta = Meta(session_name, url)
    session.add(meta)
    session.commit()

    stop = dump(url, output_folder)

    while True:
        if stop_flag:
            stop.set()
            break

    session = DataBase.get_session()()
    meta = session.query(Meta).first()
    meta.stop = datetime.utcnow()
    print("Record length {0}".format(meta.stop - meta.start))
    session.commit()


def main():
    parser = argparse.ArgumentParser(description='Istream HLS Session Recorder.')
    parser.add_argument('url', help='hls input stream')
    parser.add_argument('-o', '--output', help='output folder name')
    parser.add_argument('-s', '--session', help='output session name')

    args = parser.parse_args()

    output_folder = './sessions'
    
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

    print('Start recording session {0} to {1}'.format(session_name, output_folder))
    record_session(args.url, output, session_name)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
