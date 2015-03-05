__author__ = 'mike'

import cherrypy
import argparse
import os.path
import sys
from cherrypy.lib.static import serve_file
from db import *
from models import *
from m3u8 import *
from datetime import datetime, timedelta

DataBase = None
session_folder = None
start_time = datetime.utcnow()


class Keys(object):
    def _cp_dispatch(self, vpath):
        cherrypy.request.params['name'] = '/'+'/'.join(vpath) + '?' + cherrypy.request.query_string
        del vpath[:]
        return self

    @cherrypy.expose
    def index(self, name=None, **params):
        return get_key(name)


class Chunks(object):
    def __init__(self, static_dir):
        self.static_dir = static_dir

    def _cp_dispatch(self, vpath):
        cherrypy.request.params['name'] = os.path.join(self.static_dir, '/'.join(vpath))
        del vpath[:]
        return self

    @cherrypy.expose
    def index(self, name):
        print ('RETURN', name)
        return serve_file(name)


@cherrypy.popargs('name')
class Playlist(object):
    @cherrypy.expose
    def index(self, name=None, **params):
        vpath = name.split('/')
        if len(vpath) > 1 and vpath[0] == 'key':
            return get_key('/'.join(vpath[1:]))
        else:
            cherrypy.response.headers['Content-Type'] = 'audio/mpegurl'
            if name == 'stream.m3u8':
                return get_main_playlist()
            else:
                return get_internal_playlist(name)

    @cherrypy.expose
    def key(self, name=None, **args):
        print "requested key", name
        return get_key(name)



def get_session_start_time():
    session = DataBase.get_session()()
    meta = session.query(Meta).first()
    return meta.start


def get_main_playlist():
    related_time = (datetime.utcnow() - start_time) + get_session_start_time()
    session = DataBase.get_session()()
    pl = session.query(MainPlaylist).filter(MainPlaylist.date < related_time).order_by(MainPlaylist.date.desc()).first()
    return playlist_remove_absolute_paths(pl.body)+'\n'


def get_internal_playlist(name):
    related_time = (datetime.utcnow() - start_time) + get_session_start_time()
    session = DataBase.get_session()()
    pl = session.query(SimplePlaylist).filter(SimplePlaylist.name == name).filter(SimplePlaylist.date < related_time)\
        .order_by(SimplePlaylist.date.desc()).first()
    if pl:
        host = cherrypy.request.headers['Host']
        return playlist_prepend_path(playlist_remove_absolute_paths(
            playlist_replace_keys(pl.body, host)), '/chunks')+'\n'
    else:
        raise cherrypy.NotFound


def get_key(path):
    session = DataBase.get_session()()
    key = session.query(Key).filter(Key.path == path).first()
    if key:
        return key.data
    else:
        raise cherrypy.NotFound()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Istream HLS Session Replayer.')
    parser.add_argument('session', help='recorded session name')
    parser.add_argument('-f', '--folder', help='session folder')
    parser.add_argument('-p', '--port', help='listening port (default 9090)')
    parser.add_argument('-o', '--offset', help='start offset in seconds')

    args = parser.parse_args()

    folder = './sessions'

    if args.folder:
        folder = args.folder

    if args.offset:
        start_time -= timedelta(0,int(args.offset))

    session_folder = os.path.join(folder, args.session)

    if not os.path.exists(session_folder):
        print "Cannot open folder %s" % session_folder
        sys.exit(0)

    DataBase = DB('sqlite:///{0}/session.db'.format(session_folder))

    conf = {
        'global': {
            'server.socket_port': 9090,
            'server.socket_host': '0.0.0.0',
            'tools.trailing_slash.on': False,
            'tools.trailing_slash.extra': False,
            'tools.trailing_slash.missing': False
        }
    }
    app_conf = {}
    cherrypy.config.update(conf)
    cherrypy.tree.mount(Playlist(), '/', app_conf)
    cherrypy.tree.mount(Chunks(os.path.join(os.path.abspath(folder), args.session, 'chunks')), '/chunks', app_conf)
    cherrypy.tree.mount(Keys(), '/key', app_conf)
    cherrypy.engine.start()
    cherrypy.engine.block()