""" this module provides command line acces to unittesting with
maya's python interpreter
CREDIT GOES TO CHAD VERNONE
http://www.chadvernon.com/blog/unit-testing-in-maya/ """

import argparse
import errno
import os
import platform
import shutil
import stat
import subprocess
import tempfile
import uuid

SPORE_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_maya_location(maya_version):
    """Get the location where Maya is installed.
    @param maya_version The maya version number.
    @return The path to where Maya is installed.
    """
    if 'MAYA_LOCATION' in os.environ.keys():
        return os.environ['MAYA_LOCATION']
    if platform.system() == 'Windows':
        return 'C:/Program Files/Autodesk/Maya{0}'.format(maya_version)
    elif platform.system() == 'Darwin':
        return '/Applications/Autodesk/maya{0}/Maya.app/Contents'.format(maya_version)
    else:
        location = '/usr/autodesk/maya{0}'.format(maya_version)
        if maya_version < 2016:
            # Starting Maya 2016, the default install directory name changed.
            location += '-x64'
        return location


def mayapy(maya_version):
    """Get the mayapy executable path.
    @param maya_version The maya version number.
    @return: The mayapy executable path.
    """
    python_exe = '{0}/bin/mayapy'.format(get_maya_location(maya_version))
    if platform.system() == 'Windows':
        python_exe += '.exe'
    return python_exe


def create_clean_maya_app_dir(dst):
    """Creates a copy of the clean Maya preferences so we can create predictable results.
    @return: The path to the clean MAYA_APP_DIR folder.
    """
    app_dir = os.path.join(SPORE_ROOT_DIR, 'tests', 'clean_maya_prefs')
    if os.path.exists(dst):
        shutil.rmtree(dst, ignore_errors=False, onerror=remove_read_only)
    shutil.copytree(app_dir, dst)
    return dst


def remove_read_only(func, path, exc):
    """ Called by shutil.rmtree when it encounters a readonly file. """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise RuntimeError('Could not remove {0}'.format(path))


def main():
    parser = argparse.ArgumentParser(description='Runs unit tests for a Maya module')
    parser.add_argument('-m', '--maya',
                        help='Maya version',
                        type=int,
                        default=2018)
    #  parser.add_argument('-mad', '--maya-app-dir',
    #                      help='Just create a clean MAYA_APP_DIR and exit')
    pargs = parser.parse_args()

    mayaunittest = os.path.join(SPORE_ROOT_DIR, 'scripts', 'utils', 'test_util.py')
    cmd = [mayapy(pargs.maya), mayaunittest]

    if not os.path.exists(cmd[0]):
        raise RuntimeError('Could not find mayapy: {}'.format(cmd[0]))

    app_dir = os.path.join(SPORE_ROOT_DIR, 'tests', 'clean_maya_prefs', str(pargs.maya))
    pref_dir = create_clean_maya_app_dir(app_dir)

    os.environ['SPORE_ROOT_DIR'] = SPORE_ROOT_DIR
    os.environ['PYTHONPATH'] = ''
    os.environ['MAYA_APP_DIR'] = pref_dir
    os.environ['MAYA_SCRIPT_PATH'] = ''
    os.environ['MAYA_PLUG_IN_PATH'] = os.path.join(SPORE_ROOT_DIR, 'plug-ins')
    os.environ['MAYA_MODULE_PATH'] = SPORE_ROOT_DIR

    print cmd

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        print 'subprocess returned zero'
    finally:
        shutil.rmtree(pref_dir)

if __name__ == '__main__':
    main()
