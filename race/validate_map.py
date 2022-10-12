#!/usr/bin/python3
import os
import sys
import argparse
import subprocess
import re

sys.path.append('/srv/tw/race/tml')

from tml.tml import Teemap
from tml.constants import TILEINDEX, TELEINDEX, SPEEDUPINDEX, EXTERNAL_MAPRES

import tw


# Exceptions:
# - run_300_from_scratch uses tunes
# - run_crossover uses weapon tele
# - ctf1-7 not checked, we can't change standard maps


RACE_SETTINGS   = set(['sv_health_and_ammo 1', 'sv_kill_grenades 1'])
NOHARM_SETTINGS = set(['sv_delete_grenades_after_death 0', 'sv_infinite_ammo 1', \
    'sv_pickup_respawn -1', 'sv_regen 0', 'sv_rocket_jump_damage 0', \
    'sv_strip 0', 'sv_teleport 0', 'sv_teleport_grenade 0', 'sv_teleport_kill 0', \
    'sv_teleport_vel_reset 0', 'sv_teleport 1', 'sv_no_items 0', 'tune_zone .*'])

FRONT_TILES  = list(map(TILEINDEX.get, ['air', 'death', 'start', 'finish', \
              'armor', 'health', 'shotgun', 'grenade', 'ninja', 'rifle', \
              'stopper', 'stopper_twoway', 'stopper_allway']))
GAME_TILES   = list(map(TILEINDEX.get, ['solid', 'nohook']))
NOHARM_TILES = [29, 30, 31, 68, 93, 94, 134, 176]

TELE_TILES   = list(map(TELEINDEX.get, ['air', 'from', 'from_evil', 'to', 'cp', \
               'cp_from', 'cp_from_evil', 'cp_to']))


def err(msg):
    global success
    if show_error:
        print("Error: {}: {}".format(mapname, msg))
        success = False

def crit(msg):
    global success
    print("Critical: {}: {}".format(mapname, msg))
    success = False

def load_map():
    try:
        t = Teemap(mappath)
        return t
    except Exception as err:
        crit(err)

def validate_settings(t):
    if not t.info or not t.info.settings:
        return
    settings = set([s.decode() for s in t.info.settings])
    if not settings or settings == set(['']):
        return
    if mapname == 'run_300_from_scratch':
        return
    if gametype == 'race' and all(any(re.match(r, s) for r in RACE_SETTINGS) for s in settings):
        return
    if all(any(re.match(r, s) for r in NOHARM_SETTINGS) for s in settings):
        err("Invalid server settings")
    else:
        crit("Invalid server settings {}".format(settings - NOHARM_SETTINGS))

def validate_mapres(t):
    for image in t.images:
        if image.external and image.name not in EXTERNAL_MAPRES:
            err("Mapre '{}' not embedded".format(image.name))

def validate_layers(t):
    if t.switchlayer:
        crit("Switch layer forbidden")
    if t.tunelayer and mapname != 'run_300_from_scratch':
        err("Tune layer forbidden")

def validate_gametiles(t):
    spawn_count = 0
    spawn_red_count = 0
    spawn_blue_count = 0
    flag_red_count = 0
    flag_blue_count = 0

    warned = []
    layers = [t.gamelayer]
    if t.frontlayer:
        layers.append(t.frontlayer)
    for layer in layers:
        for tile in layer.gametiles:
            if tile.index in FRONT_TILES:
                continue
            if layer.is_gamelayer and tile.index in GAME_TILES:
                continue
            if TILEINDEX['cp_first'] <= tile.index <= TILEINDEX['cp_last']:
                continue

            if tile.index == TILEINDEX['spawn']:
                spawn_count += 1
                continue
            elif tile.index == TILEINDEX['spawn_red']:
                spawn_red_count += 1
                continue
            elif tile.index == TILEINDEX['spawn_blue']:
                spawn_blue_count += 1
                continue
            elif tile.index == TILEINDEX['flagstand_red']:
                flag_red_count += 1
                continue
            elif tile.index == TILEINDEX['flagstand_blue']:
                flag_blue_count += 1
                continue

            if tile.index not in warned:
                layer_name = 'gamelayer' if layer.is_gamelayer else 'frontlayer'
                if tile.index in NOHARM_TILES:
                    err("Invalid index {} in {}".format(tile.index, layer_name))
                else:
                    crit("Invalid index {} in {}".format(tile.index, layer_name))
                warned.append(tile.index)

    if gametype == 'race' and (spawn_count == 0 or spawn_red_count != 0 or spawn_blue_count != 0 or
                               flag_red_count != 0 or flag_blue_count != 0):
        crit("Invalid spawn or flagstand count")
    if gametype == 'race' and spawn_count > 1:
        err("More than one spawns")
    if gametype == 'fastcap' and (spawn_count != 0 or spawn_red_count == 0 or spawn_blue_count == 0 or
                                  flag_red_count != 1 or flag_blue_count != 1):
        crit("Invalid spawn or flagstand count")

def validate_teletiles(t):
    if not t.telelayer:
        return
    warned = []
    for tile in t.telelayer.gametiles:
        if tile.index in TELE_TILES:
            continue
        if mapname == 'run_crossover' and tile.index == TELEINDEX['weapon']:
            continue
        if tile.index not in warned:
            crit("Invalid index {} in telelayer".format(tile.index))
            warned.append(tile.index)

def validate_speeduptiles(t):
    if not t.speeduplayer:
        return
    for tile in t.speeduplayer.gametiles:
        if tile.index not in [0, SPEEDUPINDEX]:
            err("Invalid index in speeduplayer")
            return

def validate_map(path, gtype, only_critical=False):
    global mappath, mapname, gametype, show_error, success

    mappath = path
    mapname = os.path.basename(path)[:-4]
    gametype = gtype
    show_error = not only_critical
    success = True

    t = load_map()
    if t:
        validate_settings(t)
        validate_mapres(t)
        validate_layers(t)
        validate_gametiles(t)
        validate_teletiles(t)
        validate_speeduptiles(t)

    if show_error:
        ddnet_build_dir = os.path.join(tw.srcdir, 'ddnet', 'build')
        p = subprocess.run([os.path.join(ddnet_build_dir, 'map_convert_07'), mappath, '/dev/null'],
                           cwd=ddnet_build_dir, capture_output=True, text=True)
        for message in re.findall(f'\[map_convert_07\]: {re.escape(mappath)}: (.*)', p.stdout):
            err(message)

    return success


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mapfile', help="path to the map file")
    parser.add_argument('category', choices=["Short", "Middle", "Long Easy", "Long Advanced", "Long Hard", "Fastcap"])
    args = parser.parse_args()

    if validate_map(args.mapfile, 'fastcap' if args.category == "Fastcap" else 'race'):
        print("Found no errors")
