#!/usr/bin/python3
import os
import subprocess
import datetime

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


backup('gores', ['race', 'teamrace'])
backup('race', ['lastrecords', 'maps', 'race'])
