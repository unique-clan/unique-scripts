#!/usr/bin/python3
import sys
import os
import subprocess

import tw


def writelines(maps, votefile, length):
    for mapname, mapper in maps:
        votefile.write('@chmap|'+mapname+'|'+mapper+'\n')

print("Generating votes")

with tw.RecordDB() as db:
    for length in ('Short', 'Middle', 'Long', 'Fastcap'):
        with db.query as c:
            c.execute("SELECT Map, Mapper FROM race_maps WHERE Server = %s ORDER BY Map", (length, ))
            maps = c.fetchall()
            c.execute("SELECT Map, Mapper FROM race_maps WHERE Server = %s ORDER BY Timestamp DESC LIMIT 5", (length, ))
            newmaps = c.fetchall()
        with open(os.path.join(tw.racedir, 'maps_'+length.lower()+'.cfg.tmpl'), 'w') as mapsfile:
            writelines(maps, mapsfile, length)
        with open(os.path.join(tw.racedir, 'mapsnew_'+length.lower()+'.cfg.tmpl'), 'w') as newmapsfile:
            writelines(newmaps, newmapsfile, length)

subprocess.run(os.path.join(tw.basedir, 'build_config.py'))
