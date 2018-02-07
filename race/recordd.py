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
    with db.query as c:
        c.execute("CREATE TABLE IF NOT EXISTS race_recordqueue (Id INT UNSIGNED NOT NULL AUTO_INCREMENT, Map VARCHAR(128) BINARY NOT NULL, Name VARCHAR(16) BINARY NOT NULL, Timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, Time FLOAT DEFAULT 0, PRIMARY KEY(Id)) CHARACTER SET utf8mb4")

    currentid = 0
    nexttime = time.time()
    while running:
        diff = nexttime - time.time()
        time.sleep(diff if diff > 0 else 0)
        nexttime = time.time() + 1

        with db.commit as c:
            c.execute("DELETE FROM race_recordqueue WHERE Timestamp < (NOW() - INTERVAL 3 SECOND)")

        with db.query as c:
            c.execute("SELECT u1.Id, u1.Map, u1.Name, u1.Time FROM race_recordqueue u1 INNER JOIN (SELECT MIN(t1.Id) AS minId FROM race_recordqueue t1 INNER JOIN (SELECT Map, MIN(Time) AS minTime FROM race_recordqueue GROUP BY Map) t2 ON t1.Map = t2.Map AND t1.Time = t2.minTime GROUP BY t1.Map) u2 ON u1.Id = u2.minId WHERE u1.Id > %s AND u1.Timestamp > (NOW() - INTERVAL 2 SECOND)", (currentid, ))
            for row in c.fetchall():
                currentid = row[0]
                msg = '**{}** took the first rank on **{}** with __{:02}:{:06.3f}__ !'.format(tw.escape_discord(row[2]), tw.escape_discord(row[1]), int(row[3] // 60), row[3] % 60)
                tw.send_discord(msg, tw.passwords['discord_records'])
