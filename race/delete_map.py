#!/usr/bin/python3
import sys
import os
import subprocess

import tw


mapname = input("Mapname: ")
if not mapname:
    print("Mapname may not be empty")
    sys.exit()


dest = os.path.join(tw.racedir, 'maps', mapname+'.map')
if os.path.isfile(dest):
    print("Deleting map at {}".format(dest.replace(' ', '\\ ')))
    os.remove(dest)
else:
    print("Map was not deleted, it couldn't be found at {}".format(dest.replace(' ', '\\ ')))

dest07 = os.path.join(tw.racedir, 'maps07', mapname+'.map')
if os.path.isfile(dest07):
    print("Deleting map at {}".format(dest07.replace(' ', '\\ ')))
    os.remove(dest07)
else:
    print("Map was not deleted, it couldn't be found at {}".format(dest07.replace(' ', '\\ ')))

confdest = os.path.join(tw.racedir, 'maps', mapname+'.map.cfg')
if os.path.isfile(confdest):
    print("Deleting config at {}".format(confdest))
    os.remove(confdest)
else:
    print("Config was not deleted, it couldn't be found at {}".format(confdest.replace(' ', '\\ ')))

deleted_votes = False
with tw.RecordDB() as db:
    with db.commit as c:
        c.execute("DELETE FROM race_maps WHERE Map = %s", (mapname, ))
        if c.rowcount:
            print("Deleted vote")
            deleted_votes = True
        else:
            print("Vote with mapname doesn't exists, no vote was deleted")

if deleted_votes:
    subprocess.run(os.path.join(tw.racedir, 'generate_votes.py'))
