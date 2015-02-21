from __future__ import print_function
"""
:copyright: 2010-2015 by Ronny Pfannschmidt
:license: MIT
"""
import os
import sys
from pkg_resources import iter_entry_points


from .utils import do, trace
from .version import format_version


def version_from_cachefile(root, cache_file=None):
    # XXX: for now we ignore root
    if not cache_file or not os.path.exists(cache_file):
        return
    # replaces 'with open()' from py2.6
    fd = open(cache_file)
    fd.readline()  # remove the comment
    version = None
    try:
        line = fd.readline()
        version_string = line.split(' = ')[1].strip()
        version = version_string[1:-1]
    except:  # any error means invalid cachefile
        trace('invalid cachefile')
    fd.close()
    return version


def write_cache_file(path, version):
    fd = open(path, 'w')
    try:
        fd.write('# this file is autogenerated by setuptools_scm + setup.py\n')
        fd.write('version = "%s"\n' % version)
    finally:
        fd.close()


def version_from_scm(root):
    ep = find_matching_entrypoint(root, 'setuptools_scm.parse_scm')
    if ep:
        return ep.load()(root)


def get_version(cache_file=None, root='.',
                version_scheme='guess-next-dev',
                local_scheme='node-and-date',
                ):
    root = os.path.abspath(root)
    trace('root', repr(root))
    if cache_file is not None:
        cache_file = os.path.join(root, cache_file)
        trace('cache_file', repr(cache_file))

    version = version_from_scm(root)

    if version:
        if isinstance(version, str):
            return version
        version = format_version(
            version, version_scheme=version_scheme, local_scheme=local_scheme)
        assert version, version
        if cache_file:
            write_cache_file(cache_file, version)
        return version
    elif cache_file:
        return version_from_cachefile(root, cache_file)


def _ovalue(obj, name, default):
    if isinstance(obj, dict):
        return obj.get(name, default)
    else:
        return default


def setuptools_version_keyword(dist, keyword, value):
    if not value:
        return
    if value is True:
        value = {}
    try:
        dist.metadata.version = get_version(**value)
    except Exception as e:
        trace('error', e)


def find_matching_entrypoint(path, entrypoint):
    trace('looking for ep', entrypoint, path)
    for ep in iter_entry_points(entrypoint):
        if os.path.exists(os.path.join(path, ep.name)):
            if os.path.isabs(ep.name):
                trace('ignoring bad ep', ep)
            trace('found ep', ep)
            return ep


def find_files(path='.'):
    if not path:
        path = '.'
    abs = os.path.abspath(path)
    ep = find_matching_entrypoint(abs, 'setuptools_scm.files_command')
    if ep:
        command = ep.load()
        if isinstance(command, str):
            return do(ep.load(), path).splitlines()
        else:
            return command(path)
    else:
        return []

if __name__ == '__main__':
    print('Guessed Version', get_version())
    if 'ls' in sys.argv:
        for fname in find_files('.'):
            print(fname)