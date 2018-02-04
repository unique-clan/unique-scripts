#!/usr/bin/python3
import sys
import os
import subprocess
import signal

import tw


def stop(signum, frame):
    p.terminate()
    sys.exit()


if len(sys.argv) <= 1:
    print("No server specified")
    sys.exit()

server = sys.argv[1]
if server not in tw.servers:
    print("No such server")
    sys.exit()

serverdir = os.path.join(tw.basedir, server)
logpath = os.path.join(serverdir, 'server.log')

signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)

while True:
    if os.path.isfile(logpath):
        os.rename(logpath, logpath+'.old')
    with open(logpath, 'w') as logfile:
        p = subprocess.Popen('./teeworlds_srv', cwd=serverdir, stdout=logfile, stderr=logfile)
        p.wait()
