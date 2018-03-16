#!/usr/bin/python3
import sys
import os
import warnings
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
        c.execute("SELECT Map, Name, COUNT(*) FROM race_race GROUP BY Map, Name")
        for row in c:
            delnum = row[2] - 1
            if delnum:
                c.execute("DELETE FROM race_race WHERE Map = %s AND Name = %s ORDER BY Time DESC LIMIT %s", (row[0], row[1], delnum))
                if c.rowcount != delnum:
                    raise NotDeletedError("The following query didn't delete the expected number of rows\n" + c._last_executed.decode('utf-8'))
                deleted_total += delnum
        c.execute("DELETE FROM race_points WHERE Points = 0")
        points_deleted = c.rowcount
        c.execute("DELETE FROM race_catpoints WHERE Points = 0")
        c.execute("INSERT INTO race_points SELECT Name, SUM(mapPoints) FROM (SELECT t1.Name as Name, FLOOR(100*EXP(-S*(playerTime/bestTime-1))) as mapPoints FROM (SELECT Map, Name, ROUND(MIN(Time), 3) AS playerTime FROM race_race GROUP BY Map, Name) t1 INNER JOIN (SELECT Map, ROUND(MIN(Time), 3) AS bestTime FROM race_race GROUP BY Map) t2 ON t1.Map = t2.Map INNER JOIN (SELECT Map, CASE WHEN Server = 'Short' THEN 5.0 WHEN Server = 'Middle' THEN 3.5 WHEN Server = 'Long' THEN CASE WHEN Stars = 0 THEN 2.0 WHEN Stars = 1 THEN 1.0 WHEN Stars = 2 THEN 0.05 END END AS S FROM race_maps) t3 ON t1.Map = t3.Map) t WHERE mapPoints != 0 GROUP BY Name ON DUPLICATE KEY UPDATE Points=VALUES(Points)")
        points_corrected = c.rowcount
        c.execute("INSERT INTO race_catpoints SELECT Server, Name, SUM(mapPoints) FROM (SELECT Server, t1.Name as Name, FLOOR(100*EXP(-S*(playerTime/bestTime-1))) as mapPoints FROM (SELECT Map, Name, ROUND(MIN(Time), 3) AS playerTime FROM race_race GROUP BY Map, Name) t1 INNER JOIN (SELECT Map, ROUND(MIN(Time), 3) AS bestTime FROM race_race GROUP BY Map) t2 ON t1.Map = t2.Map INNER JOIN (SELECT Server, Map, CASE WHEN Server = 'Short' THEN 5.0 WHEN Server = 'Middle' THEN 3.5 WHEN Server = 'Long' THEN CASE WHEN Stars = 0 THEN 2.0 WHEN Stars = 1 THEN 1.0 WHEN Stars = 2 THEN 0.05 END END AS S FROM race_maps) t3 ON t1.Map = t3.Map) t WHERE mapPoints != 0 GROUP BY Server, Name ON DUPLICATE KEY UPDATE Points=VALUES(Points)")

print("Successfully deleted {} worse ranks".format(deleted_total))
print("Successfully deleted {} zero point entries".format(points_deleted))
print("Successfully corrected {} point entries".format(points_corrected))
