#!/usr/bin/python3
import os
import sys
import signal

import tw


servers = tw.select_items(tw.servers.keys(), sys.argv[1:])
for server in servers:
    pidpath = os.path.join(tw.basedir, server, 'server.pid')
    if os.path.isfile(pidpath):
        with open(pidpath) as pidfile:
            pid = int(pidfile.read())
        os.remove(pidpath)
        os.kill(pid, signal.SIGTERM)
