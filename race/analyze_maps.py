#!/usr/bin/python3
import sys
import os

import tw


folder = os.path.join(tw.racedir, 'maps')
lengths = ['short', 'middle', 'long']

with tw.RecordDB() as db:
    with db.query as c:
        c.execute("SELECT Map, Server, Stars FROM race_maps")
        votes = {}
        for row in c.fetchall():
            mapname = row[0]
            length = row[1].lower()
            difficulty = row[2]
            if mapname in votes:
                print("Error: Mapvote '{}' has duplicates".format(mapname))
            if length in lengths:
                votes[mapname] = length
            else:
                print("Error: Mapvote '{}' has an invalid map length field".format(mapname))
            if (length == 'long' and not 0 <= difficulty <= 2) or (length != 'long' and difficulty != 0):
                print("Error: Mapvote '{}' has an invalid difficulty field".format(mapname))

conforgs = {}
for length in lengths:
    conforgs[os.path.join(tw.racedir, 'reset_'+length+'.cfg')] = length

maps = []
configs = {}
images = []
for filename in os.listdir(folder):
    filepath = os.path.join(folder, filename)
    if filename.endswith('.map'):
        if os.path.isfile(filepath):
            maps.append(filename[:-4])
        else:
            print("Error: Mapfile '{}' is not a regular file".format(filename))
    elif filename.endswith('.map.cfg'):
        conforg = os.path.realpath(filepath)
        if os.path.isfile(filepath) and os.path.islink(filepath) and conforg in conforgs:
            configs[filename[:-8]] = conforgs[conforg]
        else:
            print("Error: Mapconfig '{}' is not a symlink to a length dependent reset file".format(filename))
    elif filename.endswith('.png'):
        if os.path.isfile(filepath):
            images.append(filename[:-4])
        else:
            print("Error: Map image '{}' is not a regular file".format(filename))
    else:
        print("Error: Unknown file '{}'".format(filename))

mapcount = {l: 0 for l in lengths}
for mapname, maplength in votes.items():
    mapcount[maplength] += 1
    if mapname not in maps:
        print("Error: Mapvote '{}' has no corresponding mapfile".format(mapname))
    if mapname not in configs:
        print("Error: Mapvote '{}' has no corresponding mapconfig".format(mapname))
    elif maplength != configs[mapname]:
        print("Error: Map length field of mapvote '{}' does not match the corresponding mapconfigs symlink to the length dependent reset file".format(mapname))
    if mapname not in images:
        print("Error: Mapvote '{}' has no corresponding map image".format(mapname))
for mapname in maps:
    if mapname not in votes:
        print("Error: Mapfile '{}.map' has no corresponding mapvote".format(mapname))
for mapname in configs:
    if mapname not in votes:
        print("Error: Mapconfig '{}.map.cfg' has no corresponding mapvote".format(mapname))
for mapname in images:
    if mapname not in votes:
        print("Error: Map image '{}.png' has no corresponding mapvote".format(mapname))

print("There are {} mapvotes in total ({short} short, {middle} middle, {long} long)".format(sum(mapcount.values()), **mapcount))
