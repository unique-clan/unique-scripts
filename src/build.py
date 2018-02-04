#!/usr/bin/python3
import os
import sys
import subprocess

import tw


mods = tw.select_items(tw.srcmods.keys(), sys.argv[1:])
for mod in mods:
    os.chdir(os.path.join(tw.srcdir, mod))
    tool = tw.srcmods[mod]
    status = None

    if tool == 'bam':
        status = subprocess.run(['bam', 'server_release']).returncode
    elif tool == 'cmake':
        os.chdir('build')
        status = subprocess.run(['make', 'DDNet-Server']).returncode

    if status == 0:
        print('\033[1;92mSuccessfully built {}\033[0m'.format(mod))
    elif status is not None:
        print('\033[1;91mFailed to build {}\033[0m'.format(mod))
