__author__ = 'mike'

import re
import requests
from urlparse import urlparse
from urlparse import urljoin


def remove_sessions(playlist):
    str = re.sub('([?|&]session=)\w+', '', playlist)
    return re.sub('([?|&]token=)\w+', '', str)


def is_playlist(playlist):
    if playlist.find('#EXTM3U') == -1:
        return False
    else:
        return True


def is_variant(playlist):
    if playlist.find('#EXT-X-STREAM-INF') == -1:
        return False
    else:
        return True


def get_streams(playlist):
    urls = []
    for x in playlist.splitlines():
        if x.find('#') != 0:
            urls.append(x)
    return urls


def make_full_url(url, baseurl):
    p_url = urlparse(url)
    if not p_url.hostname:
        return urljoin(baseurl, url)
    else:
        return url


def get_path_from_url(url):
    p_url = urlparse(url)
    if p_url.path.find('/') == 0:
        return p_url.path[1:]
    else:
        return p_url.path


def playlist_remove_absolute_paths(playlist):
    lines = []
    for x in playlist.splitlines():
        if x.find('#') != 0:
            p = urlparse(x)
            lines.append(p.path)
        else:
            lines.append(x)
    return '\n'.join(lines)


def playlist_prepend_path(playlist, path):
    lines = []
    for x in playlist.splitlines():
        if x.find('#') != 0:
            lines.append(path + x)
        else:
            lines.append(x)
    return '\n'.join(lines)


def playlist_get_keys(playlist):
    keys = []
    for x in playlist.splitlines():
        if x.find('#EXT-X-KEY') == 0:
            m = re.search('URI="(.*)"', x)
            url = m.group(1)
            r = requests.get(url)
            if r.status_code == 200:
                p = urlparse(remove_sessions(url))
                keys.append((p.path+'?'+p.query, r.text))
    return keys


def playlist_replace_keys(playlist, base):
    lines = []
    for x in playlist.splitlines():
        if x.find('#EXT-X-KEY') == 0:
            str = re.sub('(URI=")http[s]?://([^/]+)(.*")', r'\g<1>http://'+base+r'/key\g<3>', x)
            lines.append(str)
        else:
            lines.append(x)
    return '\n'.join(lines)

def playlist_get_media_sequence(playlist):
    lines = []

    first = 0
    count = 0
    for x in playlist.splitlines():
        if x.find('#EXT-X-MEDIA-SEQUENCE') == 0:
            first = int(x[22:])
        if x.find('#EXTINF') == 0:
            count += 1

    return first, count