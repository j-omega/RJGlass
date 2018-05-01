#!/usr/bin/env python
#python setup.py py2exe is command to run py2exe

#from distutils.core import setup
#import py2exe

#setup(console=['RJGlass.py'])
#data=[('.', ['config.py'])]

from distutils.core import setup
import py2exe

myVersion='0.3.0'

setup(options={'py2exe': {
#'dist_dir':'gne_wol_'+myVersion,
'excludes':'config',
'bundle_files': 1,
'dll_excludes':'w9xpopen.exe'}},
#zipfile=None,
name='RJGlass',
version=myVersion,
author='Michael LaBrie',
author_email='monkey256@verizon.net',
description='RJ Glass Cockpit',
console=['RJGlass.py'],
data_files=[('.', ['config.py'])]
)
