__author__ = 'mike'

import argparse
import tempfile
import signal
import requests
from os import listdir, makedirs, unlink
from os.path import isdir, join, dirname, exists
import sys
from multiprocessing import Process
from m3u8 import *
import shutil
import time
import random

stop_flag = False


def signal_handler(signal, frame):
    global stop_flag
    stop_flag = True


def DEBUG(*args):
    debug = False
    if debug:
        print(args)


def ECHO(*args):
    print(args)


def save_segments(segments, base_url, saved_segments):
    for segment in segments:
        if segment not in saved_segments:
            DEBUG('save segment: segment = {0}'.format(segment))
            saved_segments.append(segment)
            segment_name = get_path_from_url(segment)
            DEBUG('segment_name {0}'.format(segment_name))
            r = requests.get(make_full_url(segment, base_url), stream=True)
            if r.status_code == 200:
                f = tempfile.NamedTemporaryFile(delete=False)
                with open(f.name, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                f.close()
                unlink(f.name)
            else:
                DEBUG('STATUS CODE: ', r.status_code)


def load_streams(streams, base_url, saved_segments):
    DEBUG('save streams: streams = {0}'.format(streams))
    for stream in streams:
        r = requests.get(make_full_url(stream, base_url))
        body = r.text
        #save_keys(body, session)
        #body = remove_sessions(body)

        segments = get_streams(body)
        save_segments(segments, base_url, saved_segments)


def load_channel(server, channel, pause, number):
    token = "TOKEN" + str(number)
    url = server + '/' + channel + '.m3u8' + '?token=' + token
    saved_segments = []

    time.sleep(random.randrange(100)/10)

    while True:
        try:
            r = requests.get(url, timeout = 10)
            body = r.text

            if is_playlist(body):
                if is_variant(body):
                    streams = get_streams(body)
                    #save only best quality
                    load_streams([streams[-1]], url, saved_segments)
                else:
                    load_streams([url], url, saved_segments)
        except requests.exceptions.Timeout:
            ECHO("Request timeout after 10 seconds, url={0}".format(url))
        except (KeyboardInterrupt, SystemExit):
            raise
        except (RuntimeError, TypeError, NameError) as ex:
            ECHO("Exception in thread #{0}".format(number), ex)
        except:
            ECHO("Unknown exception in #{0}".format(number))

        if stop_flag:
            break
        time.sleep(pause)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='iStream stress testing tool.')
    parser.add_argument('address', help='iStream server address')
    parser.add_argument('channels', metavar='Channel', nargs='+',
                   help='an integer for the accumulator')
    parser.add_argument('-t', '--threads', type=int, default=10, help='number of threads')
    parser.add_argument('-p', '--pause', type=int, default=7, help='pause between playlist reloads')

    args = parser.parse_args()
    num_threads = args.threads
    pause = args.pause

    if not args.address or len(args.channels) == 0:
        sys.exit(0)

    print "Num threads", num_threads

    for n in range(num_threads):
        Process(target=load_channel, args=(args.address, args.channels[num_threads % len(args.channels)],
                                           pause, n)).start()