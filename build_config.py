#!/usr/bin/python3
import os
import inspect
import argparse

import tw


excludes = ('src', )

smallcaps = {'a':'ᴀ', 'b':'ʙ', 'd':'ᴅ', 'e':'ᴇ', 'f':'ꜰ', 'g':'ɢ', 'h':'ʜ', 'i':'ɪ',
             'j':'ᴊ', 'k':'ᴋ', 'l':'ʟ', 'm':'ᴍ', 'n':'ɴ', 'p':'ᴘ', 'q':'ǫ', 'r':'ʀ',
             't':'ᴛ', 'u':'ᴜ', 'y':'ʏ'}
def conv_smallcaps(text):
    for org, new in smallcaps.items():
        text = text.replace(org, new)
    return text

def escape(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')


class Config:

    def __init__(self, path):
        self._cfg = open(path, 'w')
        self._path = path
        self._head()

    def __del__(self):
        self._foot()
        self._cfg.close()

    def write(self, text):
        self._cfg.write(text)


    def _command(self, cmd, *args):
        self.write(cmd + ' ' + ' '.join(['"' + escape(arg) + '"' for arg in args]) + '\n')

    def _vote(self, text, cmd=None):
        if cmd == None:
            cmd = 'sv_high_bandwidth 0'
        self._command('add_vote', text, cmd)

    def _content(self, text, cmd=None):
        self._vote('│ ' + text, cmd)

    def _head(self):
        pass

    _wrote_welcome = False
    def _welcome(self):
        self._content('Welcome to Unique,')
        self._content('visit uniqueclan.net!')
        self._vote('╰───────────────────╯')
        self._wrote_welcome = True

    _blank_space = 1
    def _blank(self):
        self._vote(' '*self._blank_space)
        self._blank_space += 1

    _wrote_heading = False
    def heading(self, text):
        if not self._wrote_welcome: self._welcome()
        if self._wrote_heading: self._heading_end()
        self._blank()
        self._vote('╭──┤ ' + conv_smallcaps(text))
        self._wrote_heading = True

    def comment(self, text):
        self._content(text)

    def option(self, text, cmd):
        self._content('• ' + text, cmd)

    def switch(self, text, cmd, state=False):
        self._content(('☑' if state else '☐') + ' ' + text, cmd)

    def chmap(self, mapname, *mappers):
        self.option(os.path.basename(mapname) + (' by ' + ', '.join(mappers[:-1]) + (' & ' if len(mappers) > 1 else '') + mappers[-1] if mappers else ''), 'change_map ' + mapname)

    def findmaps(self, mapdir, mappath):
        if not os.path.isdir(mapdir):
            return
        for filename in sorted(os.listdir(mapdir)):
            self.chmap(os.path.join(mappath, filename[:-4]))

    def sqlserver(self, prefix, create_tables='0'):
        for use in ('r', 'w'):
            self._command('add_sqlserver', use, tw.config['sql']['database'], prefix, tw.config['sql']['user'], tw.config['sql']['password'], tw.config['sql']['ip'], tw.config['sql']['port'], create_tables)

    def sqlservername(self):
        self._command('sv_sql_servername', tw.config['location'])

    def name(self, gametype):
        self._command('sv_name', 'Unique ' + tw.config['location'] + ' - ' + gametype)

    def ban(self, ip):
        self._command('ban', ip, '0')

    def passwd(self, pwtype, name):
        if pwtype == 'access':
            self._command('password', tw.passwords[name])
        elif pwtype == 'rcon':
            self._command('sv_rcon_password', tw.passwords[name])
        elif pwtype == 'helper':
            self._command('sv_rcon_helper_password', tw.passwords[name])
        elif pwtype == 'econ':
            self._command('ec_password', tw.passwords[name])

    _heading_end_space = 0
    def _heading_end(self):
        self._vote('╰──┤' + ' '*self._heading_end_space)
        self._heading_end_space += 1

    def _foot(self):
        if self._wrote_heading: self._heading_end()


def needs_build(path, cfg_path):
    if (args.force_build or not os.path.exists(cfg_path) or
       (os.path.isfile(cfg_path) and os.path.getmtime(path) > os.path.getmtime(cfg_path))):
        return True
    else:
        return False

def handle_template(path):
    cfg_path = path[:-5]
    if not needs_build(path, cfg_path):
        return
    with open(path) as cont:
        cfg = Config(cfg_path)
        for line in cont:
            if line[0] == '@':
                part = ''
                parts = []
                escape = False
                for c in line[1:-1]:
                    if c == '\\' and not escape:
                        escape = True
                    elif c == '|' and not escape:
                        parts.append(part)
                        part = ''
                    else:
                        escape = False
                        part += c
                parts.append(part)
                name = parts[0]
                args = parts[1:]
                if not name.startswith('_') and hasattr(cfg, name):
                    function = getattr(cfg, name)
                    minnum = 0
                    maxnum = 0
                    for para in inspect.signature(function).parameters.values():
                        if para.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                            if para.default == inspect.Parameter.empty:
                                minnum += 1
                            maxnum += 1
                        elif para.kind == inspect.Parameter.VAR_POSITIONAL:
                            maxnum = float('inf')
                    if minnum <= len(args) <= maxnum:
                        function(*args)
                    else:
                        print("{}: Command '{}' expected {} to {} arguments".format(path, name, minnum, maxnum))
                else:
                    print("{}: Unknown command '{}'".format(path, name))
            else:
                cfg.write(line)


def excluded(path):
    for exclude in excludes:
        if path == os.path.join(tw.basedir, exclude):
            return True
    return False

def search(path):
    if excluded(path):
        return
    files = os.listdir(path)
    for f in files:
        f = os.path.join(path, f)
        if os.path.isdir(f):
            search(f)
        elif os.path.isfile(f):
            if f.endswith('.cfg.tmpl'):
                handle_template(f)


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force-build', action='store_true',
                    help="force rebuilding config")
args = parser.parse_args()

print("Building config")

search(tw.basedir)
