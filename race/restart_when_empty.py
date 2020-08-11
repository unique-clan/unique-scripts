#!/usr/bin/python3
import os
import subprocess

import tw


subprocess.run(os.path.join(tw.basedir, 'build_config.py'))

servers = tw.select_items([s['dir'] for s in tw.servers], ['race'])
for server in servers:
    fifopath = os.path.join(tw.basedir, server, 'server.fifo')
    if os.path.exists(fifopath):
        with open(fifopath, 'w') as fifofile:
            fifofile.write('sv_shutdown_when_empty 1')
