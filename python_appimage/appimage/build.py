import os
import subprocess
import sys

from ..utils.compat import decode
from ..utils.deps import APPIMAGETOOL, ensure_appimagetool
from ..utils.docker import docker_run
from ..utils.fs import copy_tree
from ..utils.log import debug, log
from ..utils.tmp import TemporaryDirectory


__all__ = ['build_appimage']


def build_appimage(appdir=None, destination=None):
    '''Build an AppImage from an AppDir
    '''
    if appdir is None:
        appdir = 'AppDir'

    log('BUILD', appdir)
    ensure_appimagetool()

    cmd = [APPIMAGETOOL, appdir]
    if destination is not None:
        cmd.append(destination)
    cmd = ' '.join(cmd)

    debug('SYSTEM', cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
    stdout = []
    while True:
        out = decode(p.stdout.readline())
        stdout.append(out)
        if out == '' and p.poll() is not None:
            break
        elif out:
            out = out.replace('%', '%%')[:-1]
            for line in out.split(os.linesep):
                if line.startswith('WARNING'):
                    log('WARNING', line[9:])
                elif line.startswith('Error'):
                    raise RuntimeError(line)
                else:
                    debug('APPIMAGE', line)
    rc = p.poll()
    if rc != 0:
        print(''.join(stdout))
        sys.stdout.flush()
        raise RuntimeError('Could not build AppImage')
