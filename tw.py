import os
import json
import urllib
try:
    import MySQLdb
except:
    pass
import requests


basedir = '/srv/tw'
racedir = os.path.join(basedir, 'race')
srcdir = os.path.join(basedir, 'src')
sqldir = os.path.join(basedir, 'sql')

with open(os.path.join(basedir, 'local_config.json')) as configfile:
    config = json.load(configfile)
with open(os.path.join(srcdir, 'mods.json')) as modsfile:
    srcmods = json.load(modsfile)
with open(os.path.join(basedir, 'servers.json')) as serversfile:
    for location in json.load(serversfile):
        if location['name'] == config['location']:
            servers = location['servers']
            break
with open(os.path.join(basedir, 'passwords.json')) as pwsfile:
    passwords = json.load(pwsfile)


def escape_discord(text):
    for c in '*_~`':
        text = text.replace(c, '\\'+c)
    return text

def send_discord(msg, key):
    requests.post('https://discordapp.com/api/webhooks/'+key, data={'content': msg})

def encode_url(t):
    return urllib.parse.quote(t, safe='')


class DBCursor:

    def __init__(self, db, commit):
        self.db = db
        self.commit = commit

    def __enter__(self):
        self.c = self.db.cursor()
        return self.c

    def __exit__(self, exc, value, tb):
        if self.commit:
            if exc:
                self.db.rollback()
            else:
                self.db.commit()
        self.c.close()


class RecordDB:

    def __enter__(self):
        self.db = MySQLdb.connect(host=config['sql']['ip'], user=config['sql']['user'],
                                  passwd=config['sql']['password'], db=config['sql']['database'],
                                  use_unicode=True, charset='utf8')
        return self

    @property
    def query(self):
        return DBCursor(self.db, commit=False)

    @property
    def commit(self):
        return DBCursor(self.db, commit=True)

    def __exit__(self, exc, value, tb):
        self.db.close()


def select_items(items, args):
    selected = [i for i in items if any([i.startswith(a) or a.startswith(i) for a in args])]
    return selected or items
