#!/usr/bin/python3
import os
import re
import subprocess

import tw


ADDMAP_RE = re.compile('^[^#]*?(raceaddmap.*)$')

crontabpath = os.path.join(tw.basedir, 'crontab')
valid = True
with open(crontabpath) as crontab:
    for line in crontab:
        m = ADDMAP_RE.match(line)
        if m:
            cmd = m.group(1) + ' --dry-run'
            p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.stdout or p.stderr:
                print(cmd)
                print(p.stdout.decode(), end='')
                print(p.stderr.decode(), end='')
                valid = False

if valid:
    print("No errors, applying crontab")
    subprocess.run(['crontab', crontabpath])
