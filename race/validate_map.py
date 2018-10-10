import os
import sys
sys.path.append('/srv/tw/race/tml')

from tml.tml import Teemap
from tml.constants import TILEINDEX, TELEINDEX, SPEEDUPINDEX, EXTERNAL_MAPRES


# Exceptions:
# - run_300_from_scratch and run_300_from_hatch use tunes
# - run_crossover uses weapon tele


NOHARM_SETTINGS =  set([b'sv_delete_grenades_after_death 0', b'sv_infinite_ammo 1', \
    b'sv_pickup_respawn -1', b'sv_regen 0', b'sv_rocket_jump_damage 0', \
    b'sv_strip 0', b'sv_teleport 0', b'sv_teleport_grenade 0', b'sv_teleport_kill 0', \
    b'sv_teleport_vel_reset 0', b'sv_teleport 1', b'sv_no_items 0'])

FRONT_TILES  = list(map(TILEINDEX.get, ['air', 'death', 'start', 'finish', 'armor', \
              'health', 'grenade', 'stopper', 'stopper_twoway', 'stopper_allway']))
GAME_TILES   = list(map(TILEINDEX.get, ['solid', 'nohook']))
NOHARM_TILES = [29, 30, 31, 68, 93, 94, 134, 176] + \
               list(map(TILEINDEX.get, ['shotgun', 'ninja', 'rifle']))

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
    except ValueError as err:
        crit(err)

def validate_info(t):
    if not t.info:
        err("No info data (load and save in editor to fix)")
        return
    if not t.info.settings or t.info.settings == [b'']:
        return
    if gametype == 'race' and t.info.settings == ['sv_health_and_ammo 1']:
        return
    if mapname == 'run_300_from_scratch' or mapname == 'run_300_from_hatch':
        return
    if set(t.info.settings).issubset(NOHARM_SETTINGS):
        err("Invalid server settings")
    else:
        crit("Invalid server settings {}".format(set(t.info.settings) - RACE_SETTINGS))

def validate_mapres(t):
    for image in t.images:
        if image.external and image.name not in EXTERNAL_MAPRES:
            err("Mapre '{}' not embedded".format(image.name))

def validate_layers(t):
    if t.switchlayer:
        crit("Switch layer forbidden")
    if t.tunelayer and mapname != 'run_300_from_scratch' and mapname != 'run_300_from_hatch':
        crit("Tune layer forbidden")

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

    if gametype == 'race' and (spawn_count == 0 or spawn_red_count != 0 or spawn_blue_count != 0 \
                               or flag_red_count != 0 or flag_blue_count != 0):
        crit("Invalid spawn and flagstand count")
    if gametype == 'fastcap' and (spawn_count != 0 or spawn_red_count != 1 or spawn_blue_count != 1 \
                               or flag_red_count != 1 or flag_blue_count != 1):
        crit("Invalid spawn and flagstand count")

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
        validate_info(t)
        validate_mapres(t)
        validate_layers(t)
        validate_gametiles(t)
        validate_teletiles(t)
        validate_speeduptiles(t)

    return success
