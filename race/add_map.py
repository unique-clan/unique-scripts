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
    os.symlink(conforg, confdest)

def add_vote(c, suffix, stars):
    c.execute("INSERT INTO race_maps (Map, Server, Mapper, Stars) VALUES (%s, %s, %s, %s)", (args.mapname+suffix, length, mapper, stars))


parser = argparse.ArgumentParser()
parser.add_argument('mapname', help="map file and image are expected in race/release/")
parser.add_argument('category', choices=["Short", "Middle", "Long Easy", "Long Advanced", "Long Hard", "Fastcap"])
parser.add_argument('mapper', nargs='*', help="mapper name (no mappers are valid)")
parser.add_argument('-f', '--force', action='store_true', help="respect only critical validation errors")
parser.add_argument('--no-announce', action='store_true', help="don't send discord announcement message")
parser.add_argument('--dry-run', action='store_true', help="validate the release without actually performing it")
args = parser.parse_args()

length = args.category.split()[0]
difficulty = 0
if args.category == "Long Advanced":
    difficulty = 1
elif args.category == "Long Hard":
    difficulty = 2

if '|' in args.mapname:
    print("The mapname may not contain '|'")
    sys.exit()
if args.mapname.endswith('_no_wpns'):
    print("The mapname may not end on '_no_wpns'")
    sys.exit()

with tw.RecordDB() as db:
    with db.query as c:
        c.execute("SELECT Map FROM race_maps WHERE Map = %s", (args.mapname, ))
        if c.rowcount:
            print("Mapvote for mapname already exists")
            sys.exit()

mappath = os.path.join(tw.racedir, 'release', args.mapname+'.map')
if not os.path.isfile(mappath):
    print("Expected map file at {}".format(mappath))
    sys.exit()

imgpath = os.path.join(tw.racedir, 'release', args.mapname+'.png')
if not os.path.isfile(imgpath):
    print("Expected image file at {}".format(imgpath))
    sys.exit()

if not validate_map(mappath, 'fastcap' if args.category == "Fastcap" else 'race', only_critical=args.force):
    sys.exit()

for mapper in args.mapper:
    if '|' in mapper:
        print("Mapper names may not contain '|'")
    elif ', ' in mapper:
        print("Mapper names may not contain ', '")
    elif ' & ' in mapper:
        print("Mapper names may not contain ' & '")
mapper = ', '.join(args.mapper[:-1]) + (' & ' if len(args.mapper) > 1 else '') + args.mapper[-1] if args.mapper else None

if args.dry_run:
    sys.exit()


dest = os.path.join(tw.racedir, 'maps', args.mapname+'.map')
os.rename(mappath, dest)
if args.category == "Fastcap":
    dest_no_wpns = os.path.join(tw.racedir, 'maps', args.mapname+'_no_wpns.map')
    os.symlink(dest, dest_no_wpns)

create_config()
if args.category == "Fastcap":
    create_config('_no_wpns')

imgdest = os.path.join(tw.racedir, 'maps', args.mapname+'.png')
os.rename(imgpath, imgdest)

with tw.RecordDB() as db:
    with db.commit as c:
        add_vote(c, '', difficulty)
        if args.category == "Fastcap":
            add_vote(c, '_no_wpns', 1)

subprocess.run(os.path.join(tw.racedir, 'generate_votes.py'))
if not args.no_announce:
    msg = "@everyone [{}](https://uniqueclan.net/map/{}) ".format(tw.escape_discord(args.mapname), tw.encode_url(args.mapname))
    if args.category == "Fastcap":
        msg += "and **{}** ".format(tw.escape_discord(args.mapname+'_no_wpns'))
    if mapper:
        msg += "by [{}](https://uniqueclan.net/mapper/{}) ".format(tw.escape_discord(mapper), tw.encode_url(mapper))
    msg += "released on *{}* !".format(args.category)
    tw.send_discord(msg, tw.passwords['discord_main'])
