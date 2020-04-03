#!/usr/bin/python3
import sys
import time
import requests
import signal

sys.path.append('/srv/tw')
import tw


running = True
def handle_sigterm(x, y):
    global running
    running = False
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

with tw.RecordDB() as db:
    currentid = 0
    nexttime = time.time()
    while running:
        diff = nexttime - time.time()
        time.sleep(diff if diff > 0 else 0)
        nexttime = time.time() + 1

        with db.commit as c:
            c.execute("DELETE FROM race_recordqueue WHERE Timestamp < (NOW() - INTERVAL 3 SECOND)")
            c.execute("SELECT u1.Id, u1.Map, u1.Name, u1.Timestamp, u1.Time FROM race_recordqueue u1 INNER JOIN (SELECT MIN(t1.Id) AS minId FROM race_recordqueue t1 INNER JOIN (SELECT Map, MIN(Time) AS minTime FROM race_recordqueue GROUP BY Map) t2 ON t1.Map = t2.Map AND t1.Time = t2.minTime GROUP BY t1.Map) u2 ON u1.Id = u2.minId WHERE u1.Id > %s AND u1.Timestamp > (NOW() - INTERVAL 2 SECOND)", (currentid, ))
            for row in c.fetchall():
                currentid = row[0]
                c.execute("INSERT INTO race_lastrecords (Map, Name, Timestamp, Time) VALUES (%s, %s, %s, %s)", row[1:])
                msg = '[{}](https://uniqueclan.net/ranks/player/{}) took the first rank on [{}](https://uniqueclan.net/map/{}) with __{:02}:{:06.3f}__!'.format(tw.escape_discord(row[2]), tw.encode_url(row[2]), tw.escape_discord(row[1]), tw.encode_url(row[1] if not row[1].endswith('_no_wpns') else row[1][:-8]), int(row[4] // 60), row[4] % 60)
                tw.send_discord(msg, tw.passwords['discord_records'])
