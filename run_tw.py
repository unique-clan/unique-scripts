#!/usr/bin/python3
import sys
import os
import subprocess
import signal
import time

import tw


def stop(signum, frame):
    p.terminate()
    sys.exit()


if len(sys.argv) <= 1:
    print("No server specified")
    sys.exit()

server = sys.argv[1]
for srvdata in tw.servers:
    if srvdata['dir'] == server:
        break
else:
    print("No such server")
    sys.exit()

serverdir = os.path.join(tw.basedir, server)
logpath = os.path.join(serverdir, 'server.log')
portpath = os.path.join(serverdir, 'port.cfg')

signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)

while True:
    with open(portpath, 'w') as portfile:
        portfile.write('sv_port {}\n'.format(srvdata['port']))
        portfile.write('ec_port {}\n'.format(srvdata['port']))
    if os.path.isfile(logpath):
        os.rename(logpath, logpath+'.old')
    with open(logpath, 'w') as logfile:
        p = subprocess.Popen('./teeworlds_srv', cwd=serverdir, stdout=logfile, stderr=logfile)
        p.wait()
    time.sleep(1)
