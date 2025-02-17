#!/usr/bin/env python

"""
setup.py file for SNAP (Stanford Network Analysis Platform) Python
    Linux version, generated on CentOS, tested on Ubuntu as well
"""

import re
import inspect
import os
import platform
import sys

#from distutils.core import setup, Extension
from setuptools import setup, Extension

#added pip flag
pip=False

#
#   Snap.py version
#
snappy_version = "4.1.0"
def getdynpath():
    '''
    get the path for the Python dynamic library
    '''
 
    s = inspect.getfile(inspect)

    newpath = None
    if "conda" in s:
        pattern = re.compile('[\w\d]+conda[\s\S]+\/lib\/')
        found = pattern.search(s)
        if found:
            newpath = s[:found.end()] + "libpython2.7.dylib"
    elif "Cellar" in s:
        start = s.find("Python.framework")
        if start > 0:
            newpath = s[:start] + "Python.framework/Python"

    return newpath
    
# is this a dry run
dryrun = False
if len(sys.argv) > 1  and  sys.argv[1] == "-n":
    dryrun = True

# is this a distribution build
sdist = False
if len(sys.argv) > 1  and  sys.argv[1] == "sdist":
    sdist = True
    
# added OS specific wheeling
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
except ImportError:
    bdist_wheel = None

#
#   determine package parameters:
#       package version, python version, os version, architecture
#

# snap version
snap_version = "dev"
try:
    f = open("Version","r")
    content = f.read()
    f.close()
    w = content.split("-")
    snap_version = w[1].strip()
except:
    pass

# python version
python_version = "py" + str(sys.version_info[0]) + "." + str(sys.version_info[1])

# os version
uname = platform.uname()
os_version = "unknown-x.x"

swubuntu = False
if uname[0] == "Linux":
    try:
        f = open("/etc/centos-release","r")
        versionpos = 2
    except:
        try:
            f = open("/etc/redhat-release","r")
            versionpos = 2
        except:
            try:
                f = open("/etc/issue","r")
                versionpos = 1
            except:
                pass

    try:
        content = f.read()
        f.close()
        w = content.split(" ")
        os_version = (w[0] + w[versionpos]).lower()
        if w[0] == "Ubuntu":
            swubuntu = True
    except:
        pass
    useros="POSIX :: Linux"

    obj_name = "_snap.so"

elif uname[0] == "Darwin":
    os.system("sw_vers -productVersion > OSX-Release")
    try:
        f = open("OSX-Release","r")
        content = f.read()
        f.close()
        os_version = "macosx" + content.strip()
    except:
        pass
    useros="MacOS"
    obj_name = "_snap.so"

elif uname[0].find("CYGWIN") == 0:
    w = uname[0].rsplit("-",1)
    os_version = w[0].lower()
    obj_name = "_snap.so"
    useros="Microsoft :: Windows"

elif uname[0].find("Windows") == 0:
    os_version = "Win"
    obj_name = "_snap.pyd"
    useros="Microsoft :: Windows"

# architecture
arch = "i386"
# x86_64 on Linux, Mac OS X, i686 on Cygwin
if uname[4] == "x86_64"  or  uname[4] == "i686"  or  uname[4] == "AMD64":
    arch = "x64"

pkg_version = "-".join([snappy_version, snap_version,
                        os_version, arch, python_version])


#
#   get the installation directory
#

# get the system Python directory
sys_install = os.path.join(
            os.path.dirname(inspect.getfile(inspect)),
            "site-packages")

instdir = "site-packages"
if swubuntu:
    instdir = "dist-packages"

#pip path relative to usr/local/ for mac and linux
if uname[0]=="Darwin":
    pip_install='lib/python'+'/'+instdir+'/'
elif uname[0]=="Linux":
    pip_install='lib/python'+str(sys.version_info[0])+'.'+str(sys.version_info[1])+'/'+instdir+'/'
else:
    pip_install='lib/python'+'/'+instdir+'/'


# check for an alternative Python user directory
user_install = sys_install
for p in sys.path:
    n = p.find(instdir)
    if n > 0:
        user_install = os.path.join(p[:n],instdir)
        break

# if Mac OS X, get a path for the Python dynamic library
dynlib_path = None
if uname[0] == "Darwin":
    dynlib_path = getdynpath()

if dryrun:
    print("swubuntu", swubuntu)
    print("pkg_version", pkg_version)
    print("obj_name", obj_name)
    print("user_install", user_install)
    print("pip_install", pip_install)
    if dynlib_path:
        print("dynlib_path", dynlib_path)
    sys.exit(0)
    
#switch to pip directory
if pip:
    user_install=pip_install

# specify additional files for Mac OS X
files = []
if uname[0] == "Darwin"  and  sdist:
    files = ["install_name_tool", "update_dynlib.sh"]

#
#   update the dynamic library path
#
if dynlib_path:
    cmd = "./update_dynlib.sh " + dynlib_path
    os.system(cmd)
    
with open("README.txt", "r") as fh:
    long_description = fh.read()

#
#   setup configuration
#
setup (name = 'snap',
    py_modules  = ["snap"],
    #ext_modules = [snap_module],
    data_files  = [(user_install, [obj_name])], #user_install
    scripts     = files,
    version     = snappy_version,
    author      = "snap.stanford.edu",
    description = """SNAP (Stanford Network Analysis Platform) Python""",
    long_description=long_description,
    long_description_content_type="text/plain",
    #url="https://github.com/snap-stanford/snap-python",
    cmdclass={'bdist_wheel': bdist_wheel},
    classifiers=[
        "Programming Language :: Python :: "+str(sys.version_info[0]),
        "Operating System :: " + useros,
    ],
    )

