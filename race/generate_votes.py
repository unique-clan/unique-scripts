#!/usr/bin/python3
import sys
import os
import subprocess

import tw


MAP_CATEGORIES = [
    ('Short', 'short', 0, 0),
    ('Middle', 'middle', 0, 0),
    ('Long', 'long', 0, 2),
    ('Fastcap', 'fastcap', 0, 0),
    ('Fastcap', 'fastcap_no_wpns', 1, 1)
]


def writelines(maps, votefile):
    for mapname, mapper in maps:
        votefile.write('@chmap|'+mapname+'|'+mapper+'\n')

print("Generating votes")

with tw.RecordDB() as db:
    for length, mapsfilename, min_stars, max_stars in MAP_CATEGORIES:
        with db.query as c:
            c.execute("SELECT Map, Mapper FROM race_maps WHERE Server = %s AND Stars >= %s AND Stars <= %s ORDER BY Map", (length, min_stars, max_stars))
            maps = c.fetchall()
            c.execute("SELECT Map, Mapper FROM race_maps WHERE Server = %s AND Stars >= %s AND Stars <= %s ORDER BY Timestamp DESC LIMIT 5", (length, min_stars, max_stars))
            newmaps = c.fetchall()
        with open(os.path.join(tw.racedir, 'maps_'+mapsfilename+'.cfg.tmpl'), 'w') as mapsfile:
            writelines(maps, mapsfile)
        with open(os.path.join(tw.racedir, 'mapsnew_'+mapsfilename+'.cfg.tmpl'), 'w') as newmapsfile:
            writelines(newmaps, newmapsfile)

subprocess.run(os.path.join(tw.basedir, 'build_config.py'))
