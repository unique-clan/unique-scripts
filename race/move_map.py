#!/usr/bin/python3
import sys
import os
import argparse
import subprocess

import tw


parser = argparse.ArgumentParser()
parser.add_argument('mapname')
parser.add_argument('category', choices=["Short", "Middle", "Long Easy", "Long Advanced", "Long Hard"])
args = parser.parse_args()

length = args.category.split()[0]
difficulty = 0
if args.category == "Long Advanced":
    difficulty = 1
elif args.category == "Long Hard":
    difficulty = 2

with tw.RecordDB() as db:
    with db.commit as c:
        c.execute("UPDATE race_maps SET Server = %s, Stars = %s WHERE Map = %s", (length, difficulty, args.mapname))
        if not c.rowcount:
            print("Map '{}' does not exist or is already on {}".format(args.mapname, args.category))
            sys.exit()
        print("Updated vote")

confdest = os.path.join(tw.racedir, 'maps', args.mapname+'.map.cfg')
conforg = os.path.join(tw.racedir, 'reset_'+length.lower()+'.cfg')
print("Updating symlink at {}".format(confdest))
os.remove(confdest)
os.symlink(conforg, confdest)

subprocess.run(os.path.join(tw.racedir, 'generate_votes.py'))
subprocess.run(os.path.join(tw.racedir, 'clean_worse_ranks.py'))
