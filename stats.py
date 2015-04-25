__author__ = 'mike'

import argparse
import tempfile
import signal
import requests
from os import listdir, makedirs, unlink
from os.path import isdir, join, dirname, exists
import sys
from m3u8 import *
import shutil
import time
import datetime
import random
from subprocess import check_output
from multiprocessing import Process, Lock
import psutil

stop_flag = False


def signal_handler(signal, frame):
    global stop_flag
    stop_flag = True


def DEBUG(*args):
    debug = False
    if debug:
        print(args)


def get_istream_info():
    for proc in psutil.process_iter():
        if proc.name().find("istream") != -1:
            return proc
    return None


def get_ffmpeg_info(grep_string):
    procs = []
    for proc in psutil.process_iter():
        if proc.name().find("ffmpeg") != -1 and proc.cmdline().find(grep_string) != -1:
            procs.append(proc)
    return procs


def check(l, port_playlist, port_chunks, ffmpegs, channels):
    sys_time = datetime.datetime.now()
    sys_cpu = psutil.cpu_percent(interval=1)
    sys_mem = psutil.virtual_memory().used / (1024*1024.0)
    istream = get_istream_info()
    istream_cpu = istream.get_cpu_percent(interval=1)
    istream_mem = istream.get_memory_info()[0] / (1024*1024.0)
    istream_con_playlist = len([conn for conn in istream.get_connections()
                                if conn.laddr[1] == port_playlist and conn.status == psutil.CONN_ESTABLISHED])
    istream_con_chunks =   len([conn for conn in istream.get_connections()
                                if conn.laddr[1] == port_chunks and conn.status == psutil.CONN_ESTABLISHED])

    output = "{0}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5}\t{6}".format(sys_time,
                                           sys_cpu,
                                           sys_mem,
                                           istream_cpu,
                                           istream_mem,
                                           istream_con_playlist,
                                           istream_con_chunks)

    if ffmpegs:
        for str in ffmpegs:
            ffmpeg_list = get_ffmpeg_info(str)
            pids = [proc.pid for proc in ffmpeg_list]
            output += "\t{0}".format(pids)

    l.acquire()
    print(output)
    l.release()


def check_loop(interval, port_playlist, port_chunks, ffmpegs, channels):
    lock = Lock()

    head_str = "TIME\tSCPU\tSMEM\tISCPU\tISMEM\tPLCON\tCHCON"
    if ffmpegs:
        for i in range(0, len(ffmpegs)):
            head_str += "\tFFMPG{0}".format(i)

    print head_str

    while True:
        if stop_flag:
            break
        Process(target=check, args=(lock, port_playlist, port_chunks, ffmpegs, channels)).start()
        time.sleep(interval)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='iStream monitoring tool.')
    parser.add_argument('-f', '--ffmpegs', metavar='FFMPEG_SOURCE_URL', nargs='+', help='ffmpeg source urls')
    parser.add_argument('-c', '--channels', metavar='CHECK_CHANNEL_URL', nargs='+', help='channel for checking')
    parser.add_argument('-pl', '--playlist_port', type=int, default=443, help='istream plyalist port')
    parser.add_argument('-pc', '--chunks_port', type=int, default=544, help='istream chunks port')
    parser.add_argument('-i', '--interval', type=int, default=5, help='check interval in seconds')

    args = parser.parse_args()

    print "FFmpegs: ", args.ffmpegs
    print "Channels: ", args.channels

    check_loop(args.interval, args.playlist_port, args.chunks_port, args.ffmpegs, args.channels)
