#!/usr/bin/python3
import sys
import os
import argparse
import subprocess

import tw
from validate_map import validate_map


parser = argparse.ArgumentParser()
parser.add_argument('mapname', help="map file is expected in race/release/")
parser.add_argument('-f', '--force', action='store_true', help="respect only critical validation errors")
args = parser.parse_args()

with tw.RecordDB() as db:
    with db.query as c:
        c.execute("SELECT Map, Server, Stars FROM race_maps WHERE Map = %s", (args.mapname, ))
        if not c.rowcount:
            print("No such map")
            sys.exit()
        row = c.fetchone()
        category = row[1]
        if category == "Long":
            category = "Long Easy"
            if row[2] == 1:
                category = "Long Advanced"
            elif row[2] == 2:
                category = "Long Hard"

mappath = os.path.join(tw.racedir, 'release', args.mapname+'.map')
if not os.path.isfile(mappath):
    print("Expected map file at {}".format(mappath))
    sys.exit()

if not validate_map(mappath, 'fastcap' if category == "Fastcap" else 'race', only_critical=args.force):
    sys.exit()


dest = os.path.join(tw.racedir, 'maps', args.mapname+'.map')
dest07 = os.path.join(tw.racedir, 'maps07', args.mapname+'.map')
ddnet_build_dir = os.path.join(tw.srcdir, 'ddnet', 'build')
os.rename(mappath, dest)
subprocess.run([os.path.join(ddnet_build_dir, 'map_convert_07'), dest, dest07], cwd=ddnet_build_dir, stdout=subprocess.DEVNULL)

subprocess.run(os.path.join(tw.basedir, 'clone.sh'))
