#!/usr/bin/python3
import sys
import os
import argparse
import subprocess
import MySQLdb

import tw
from validate_map import validate_map


def create_config(suffix=''):
    confdest = os.path.join(tw.racedir, 'maps', args.mapname+suffix+'.map.cfg')
    conforg = os.path.join(tw.racedir, 'reset_'+length.lower()+suffix+'.cfg')
    print("Creating config at {}".format(confdest.replace(' ', '\\ ')))
    os.symlink(conforg, confdest)

def add_vote(c, suffix, stars):
    c.execute("INSERT INTO race_maps (Map, Server, Mapper, Stars) VALUES (%s, %s, %s, %s)", (args.mapname+suffix, length, mapper, stars))
    print("Added new vote {}".format(args.mapname+suffix))


parser = argparse.ArgumentParser()
parser.add_argument('mapfile', help="path to the map file")
parser.add_argument('imgfile', help="path to the map image file")
parser.add_argument('category', choices=["Short", "Middle", "Long Easy", "Long Advanced", "Long Hard", "Fastcap"])
parser.add_argument('-f', '--force', action='store_true', help="respect only critical validation errors")
parser.add_argument('--no-announce', action='store_true', help="don't send discord announcement message")
args = parser.parse_args()

length = args.category.split()[0]
difficulty = 0
if args.category == "Long Advanced":
    difficulty = 1
elif args.category == "Long Hard":
    difficulty = 2

if not os.path.isfile(args.mapfile):
    print("The specified map path is not a file")
    sys.exit()
args.mapname = os.path.basename(args.mapfile)
if not args.mapname.endswith('.map'):
    print("The map filename has to end on '.map'")
    sys.exit()

if not validate_map(args.mapfile, 'fastcap' if args.category == "Fastcap" else 'race', only_critical=args.force):
    sys.exit()

args.mapname = args.mapname[:-4]
newmapname = input("Mapname (default '{}'): ".format(args.mapname))
if newmapname:
    args.mapname = newmapname
if '|' in args.mapname:
    print("The mapname may not contain '|'")
    sys.exit()
if args.mapname.endswith('_no_wpns'):
    print("The mapname may not end on '_no_wpns'")
    sys.exit()

if not os.path.isfile(args.imgfile):
    print("The specified map image path is not a file")
    sys.exit()
if not args.imgfile.endswith('.png'):
    print("The map image filename has to end on '.png'")
    sys.exit()

mappers = []
n = 1
while True:
    mapper = input("Mapper {} (empty if not present): ".format(n))
    if mapper:
        if '|' in mapper:
            print("The mapper name may not contain '|'")
        elif ', ' in mapper:
            print("The mapper name may not contain ', '")
        elif ' & ' in mapper:
            print("The mapper name may not contain ' & '")
        else:
            mappers.append(mapper)
            n += 1
    else:
        break
mapper = ', '.join(mappers[:-1]) + (' & ' if len(mappers) > 1 else '') + mappers[-1] if mappers else None


dest = os.path.join(tw.racedir, 'maps', args.mapname+'.map')
print("Moving map to {}".format(dest.replace(' ', '\\ ')))
os.rename(args.mapfile, dest)
if args.category == "Fastcap":
    dest_no_wpns = os.path.join(tw.racedir, 'maps', args.mapname+'_no_wpns.map')
    print("Creating map symlink at {}".format(dest_no_wpns.replace(' ', '\\ ')))
    os.symlink(dest, dest_no_wpns)

create_config()
if args.category == "Fastcap":
    create_config('_no_wpns')

imgdest = os.path.join(tw.racedir, 'maps', args.mapname+'.png')
print("Moving map image to {}".format(imgdest.replace(' ', '\\ ')))
os.rename(args.imgfile, imgdest)

added_votes = False
with tw.RecordDB() as db:
    try:
        with db.commit as c:
            add_vote(c, '', difficulty)
            if args.category == "Fastcap":
                add_vote(c, '_no_wpns', 1)
            added_votes = True
    except MySQLdb.Error as e:
        if str(e).startswith('(1062,'):
            print("Mapname already exists, no new vote was added")
        else:
            raise

if added_votes:
    subprocess.run(os.path.join(tw.racedir, 'generate_votes.py'))
    if not args.no_announce:
        msg =  "@everyone **{}** ".format(tw.escape_discord(args.mapname))
        if mapper:
            msg += "by **{}** ".format(tw.escape_discord(mapper))
        msg += "released on *{}* !\nhttps://uniqueclan.net/map/{}".format(args.category, tw.encode_url(args.mapname))
        tw.send_discord(msg, tw.passwords['discord_main'])
