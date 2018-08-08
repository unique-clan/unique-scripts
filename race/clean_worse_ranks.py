#!/usr/bin/python3
import sys
import os
import warnings
import time
import MySQLdb

sys.path.append('/srv/tw')
import tw


class NotDeletedError(Exception):
    pass


# we don't use binary logs so we can ignore this
warnings.filterwarnings('ignore', "Unsafe statement written to the binary log using statement format since BINLOG_FORMAT = STATEMENT\. The statement is unsafe because it uses a LIMIT clause\. This is unsafe because the set of rows included cannot be predicted\.", category=MySQLdb.Warning)


deleted_total = 0
with tw.RecordDB() as db:
    with db.commit as c:
        # delete worse ranks
        starttime = time.time()
        c.execute("DELETE t1 FROM race_race t1 LEFT JOIN (SELECT Map, Name, MIN(Time) AS minTime FROM race_race GROUP BY Map, Name) t2 ON t1.Map = t2.Map AND t1.Name = t2.Name AND t1.Time = t2.minTime WHERE t2.Map IS NULL")
        print("Successfully deleted {} worse ranks ({:.2f} sec)".format(c.rowcount, time.time() - starttime))

        # correct point entries
        starttime = time.time()
        c.execute("INSERT INTO race_points SELECT Name, SUM(mapPoints) FROM (SELECT t1.Name as Name, FLOOR(100*EXP(-S*(playerTime/bestTime-1))) as mapPoints FROM (SELECT Map, Name, ROUND(MIN(Time), 3) AS playerTime FROM race_race GROUP BY Map, Name) t1 INNER JOIN (SELECT Map, ROUND(MIN(Time), 3) AS bestTime FROM race_race GROUP BY Map) t2 ON t1.Map = t2.Map INNER JOIN (SELECT Map, CASE WHEN Server = 'Short' THEN 5.0 WHEN Server = 'Middle' THEN 3.5 WHEN Server = 'Long' THEN CASE WHEN Stars = 0 THEN 2.0 WHEN Stars = 1 THEN 1.0 WHEN Stars = 2 THEN 0.05 END END AS S FROM race_maps) t3 ON t1.Map = t3.Map) t WHERE mapPoints != 0 GROUP BY Name ON DUPLICATE KEY UPDATE Points=VALUES(Points)")
        count = c.rowcount
        c.execute("INSERT INTO race_catpoints SELECT Server, Name, SUM(mapPoints) FROM (SELECT Server, t1.Name as Name, FLOOR(100*EXP(-S*(playerTime/bestTime-1))) as mapPoints FROM (SELECT Map, Name, ROUND(MIN(Time), 3) AS playerTime FROM race_race GROUP BY Map, Name) t1 INNER JOIN (SELECT Map, ROUND(MIN(Time), 3) AS bestTime FROM race_race GROUP BY Map) t2 ON t1.Map = t2.Map INNER JOIN (SELECT Server, Map, CASE WHEN Server = 'Short' THEN 5.0 WHEN Server = 'Middle' THEN 3.5 WHEN Server = 'Long' THEN CASE WHEN Stars = 0 THEN 2.0 WHEN Stars = 1 THEN 1.0 WHEN Stars = 2 THEN 0.05 END END AS S FROM race_maps) t3 ON t1.Map = t3.Map) t WHERE mapPoints != 0 GROUP BY Server, Name ON DUPLICATE KEY UPDATE Points=VALUES(Points)")
        count += c.rowcount
        print("Successfully corrected {} point entries ({:.2f} sec)".format(count, time.time() - starttime))

        # delete zero point entries
        starttime = time.time()
        c.execute("DELETE FROM race_points WHERE Points = 0")
        count = c.rowcount
        c.execute("DELETE FROM race_catpoints WHERE Points = 0")
        count += c.rowcount
        print("Successfully deleted {} zero point entries ({:.2f} sec)".format(count, time.time() - starttime))
