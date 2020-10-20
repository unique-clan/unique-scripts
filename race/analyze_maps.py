#!/usr/bin/python3
import sys
import os
import argparse

import tw
from validate_map import validate_map


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--validate-maps', action='store_true', help="validate map files")
parser.add_argument('-p', '--pedantic', action='store_true', help="show non-critical errors")
args = parser.parse_args()


folder = os.path.join(tw.racedir, 'maps')
folder07 = os.path.join(tw.racedir, 'maps07')
lengths = ['short', 'middle', 'long', 'fastcap']

with tw.RecordDB() as db:
    with db.query as c:
        c.execute("SELECT Map, Server, Stars FROM race_maps")
        votes = {}
        for row in c.fetchall():
            mapname = row[0]
            length = row[1].lower()
            stars = row[2]
            if mapname in votes:
                print("Error: Mapvote '{}' has duplicates".format(mapname))
            if length in lengths:
                votes[mapname] = (length, stars)
            else:
                print("Error: Mapvote '{}' has an invalid map length field".format(mapname))
            if ((length == 'long' and not 0 <= stars <= 2) or (length == 'fastcap' and not 0 <= stars <= 1)
                    or (length != 'long' and length != 'fastcap' and stars != 0)):
                print("Error: Mapvote '{}' has an invalid stars field".format(mapname))

conforgs = {os.path.join(tw.racedir, 'reset_fastcap_no_wpns.cfg'): 'fastcap'}
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
        print("Error: Unknown file '{}' in maps folder".format(filename))

maps07 = []
for filename in os.listdir(folder07):
    filepath = os.path.join(folder07, filename)
    if filename.endswith('.map'):
        if os.path.isfile(filepath):
            maps07.append(filename[:-4])
        else:
            print("Error: 0.7 mapfile '{}' is not a regular file".format(filename))
    else:
        print("Error: Unknown file '{}' in 0.7 maps folder".format(filename))

mapcount = {l: 0 for l in lengths}
for mapname, (maplength, mapstars) in votes.items():
    mapcount[maplength] += 1
    if mapname not in maps:
        print("Error: Mapvote '{}' has no corresponding mapfile".format(mapname))
    if mapname not in maps07:
        print("Error: Mapvote '{}' has no corresponding 0.7 mapfile".format(mapname))
    if mapname not in configs:
        print("Error: Mapvote '{}' has no corresponding mapconfig".format(mapname))
    elif maplength != configs[mapname]:
        print("Error: Map length field of mapvote '{}' does not match the corresponding mapconfigs symlink to the length dependent reset file".format(mapname))
    if mapname not in images and not (maplength == 'fastcap' and mapstars == 1):
        print("Error: Mapvote '{}' has no corresponding map image".format(mapname))
for mapname in maps:
    if mapname not in votes:
        print("Error: Mapfile '{}.map' has no corresponding mapvote".format(mapname))
for mapname in maps07:
    if mapname not in votes:
        print("Error: 0.7 mapfile '{}.map' has no corresponding mapvote".format(mapname))
for mapname in configs:
    if mapname not in votes:
        print("Error: Mapconfig '{}.map.cfg' has no corresponding mapvote".format(mapname))
for mapname in images:
    if mapname not in votes:
        print("Error: Map image '{}.png' has no corresponding mapvote".format(mapname))

if args.validate_maps:
    print("Checking map files ...")
    for mapname, (maplength, mapstars) in votes.items():
        if mapname in maps and not (maplength == 'fastcap' and mapstars == 1):
            mappath = os.path.join(tw.racedir, 'maps', mapname) + '.map'
            validate_map(mappath, 'fastcap' if votes[mapname][0] == 'fastcap' else 'race', only_critical=not args.pedantic)

print("There are {} mapvotes in total ({short} short, {middle} middle, {long} long, {fastcap} fastcap)".format(sum(mapcount.values()), **mapcount))
