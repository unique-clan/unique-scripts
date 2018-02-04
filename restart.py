#!/usr/bin/python3
import os
import sys
import subprocess

import tw


servers = tw.select_items(tw.servers.keys(), sys.argv[1:])
subprocess.run([os.path.join(tw.basedir, 'stop.py')] + list(servers))
for server in servers:
    p = subprocess.Popen([os.path.join(tw.basedir, 'run_tw.py'), server],
                         preexec_fn=os.setpgrp)
    with open(os.path.join(tw.basedir, server, 'server.pid'), 'w') as pidfile:
        pidfile.write(str(p.pid))
