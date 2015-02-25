__author__ = 'mike'

import re
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