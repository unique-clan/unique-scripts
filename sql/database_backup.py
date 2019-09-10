#!/usr/bin/python3
import os
import subprocess
import datetime
from glob import glob

import tw


def backup(prefix, table_types):
    tables = ''
    for table_type in table_types:
        tables += prefix+'_'+table_type+' '
    datestr = datetime.date.today().strftime('%Y-%m-%d')
    path = os.path.join(tw.sqldir, 'backups', prefix+'_'+datestr+'.sql')
    cmd = 'mysqldump records {} > {}'.format(tables, path)
    print("Creating backup of {} from {}".format(prefix, datestr))
    subprocess.run(cmd, shell=True)
    clean_backups(prefix)

def clean_backups(prefix):
    """Keep just one backup per month and 10 at max."""
    backups = glob(os.path.join(tw.sqldir, 'backups', prefix+'_*.sql'))
    backups.sort(reverse=True)
    current_month = None
    for backup in backups.copy():
        month = backup[-14:-7]
        if month == current_month:
            backups.remove(backup)
            os.unlink(backup)
        current_month = month
    for backup in backups[10:]:
        os.unlink(backup)


backup('gores', ['race', 'teamrace'])
backup('race', ['lastrecords', 'maps', 'race', 'saves'])
