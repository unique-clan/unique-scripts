#!/usr/bin/python3
import os
import shutil
import sys
from subprocess import run, CalledProcessError

import tw


def build(mdir, git, ref=None, make=None, cmake=None):
    try:
        os.chdir(tw.srcdir)
        if not os.path.isdir(mdir):
            run(['git', 'clone', git, mdir], check=True)
        os.chdir(mdir)
        if ref:
            run(['git', 'fetch', '--tags'], check=True)
            run(['git', 'checkout', ref], check=True)
        else:
            run(['git', 'pull'], check=True)
        if cmake:
            if not os.path.isdir('build'):
                os.mkdir('build')
            os.chdir('build')
            run(['cmake'] + cmake + ['..'], check=True)

        if not make:
            make = ['../bam/bam', 'server_release']
        if cmake and make[0] != 'make':
            make = ['make'] + make
        if make[0] == 'bam':
            make[0] = '../bam/bam'

        run(make, check=True)
        print('\033[1;92mSuccessfully built {}\033[0m'.format(mdir))
        return True
    except CalledProcessError:
        print('\033[1;91mFailed to build {}\033[0m'.format(mdir))
        return False


success = build('bam', 'git@github.com:matricks/bam.git', ref='v0.4.0', make='./make_unix.sh')
if not success:
    sys.exit()

mods = tw.select_items(tw.srcmods.keys(), sys.argv[1:])
for mod in mods:
    build(mod, **tw.srcmods[mod])
