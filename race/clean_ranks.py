#!/usr/bin/python3
import time

import tw


with tw.RecordDB() as db:
    with db.commit as c:
        print("==========================================================")
        print("Clean up after missing maps (e.g. due to deleted maps)")
        print("==========================================================")

        c.execute("DELETE t1 FROM race_race t1 LEFT JOIN race_maps t2 ON t1.Map = t2.Map WHERE t2.Map IS NULL")
        print("Deleted {} time entries because of missing maps".format(c.rowcount))

        c.execute("DELETE t1 FROM race_lastrecords t1 LEFT JOIN race_maps t2 ON t1.Map = t2.Map WHERE t2.Map IS NULL")
        print("Deleted {} last record entries because of missing maps".format(c.rowcount))

        c.execute("DELETE t1 FROM race_ranks t1 LEFT JOIN race_maps t2 ON t1.Map = t2.Map AND t1.Server = t2.Server WHERE t2.Map IS NULL")
        print("Deleted {} rank cache entries because of missing maps".format(c.rowcount))

        c.execute("DELETE t1 FROM race_saves t1 LEFT JOIN race_maps t2 ON t1.Map = t2.Map WHERE t2.Map IS NULL")
        print("Deleted {} save entries because of missing maps".format(c.rowcount))

        print("")
        print("==========================================================")
        print("Clean up after missing ranks (e.g. due to renamed players)")
        print("==========================================================")

        starttime = time.time()
        c.execute("DELETE t1 FROM race_points t1 LEFT JOIN race_race t2 ON t1.Name = t2.Name WHERE t2.Name IS NULL")
        count = c.rowcount
        c.execute("DELETE t1 FROM race_catpoints t1 LEFT JOIN (SELECT j1.Name, j2.Server FROM race_race j1 LEFT JOIN race_maps j2 ON j1.Map = j2.Map) t2 ON t1.Name = t2.Name AND t1.Server = t2.Server WHERE t2.Name IS NULL");
        count += c.rowcount
        print("Deleted {} point entries because of missing ranks ({:.2f} sec)".format(count, time.time() - starttime))

        c.execute("DELETE t1 FROM race_lastrecords t1 LEFT JOIN race_race t2 ON t1.Map = t2.Map AND t1.Name = t2.Name WHERE t2.Name IS NULL")
        print("Deleted {} last record entries because of missing ranks".format(c.rowcount))

        c.execute("DELETE t1 FROM race_ranks t1 LEFT JOIN race_race t2 ON t1.Map = t2.Map AND t1.Name = t2.Name WHERE t2.Name IS NULL")
        print("Deleted {} rank cache entries because of missing ranks".format(c.rowcount))

        print("")
        print("==========================================================")
        print("Recalculate points")
        print("==========================================================")

        starttime = time.time()
        c.execute("INSERT INTO race_points SELECT Name, SUM(mapPoints) FROM (SELECT t1.Name as Name, FLOOR(100*EXP(-S*(playerTime/bestTime-1))) as mapPoints FROM (SELECT Map, Name, ROUND(MIN(Time), 3) AS playerTime FROM race_race GROUP BY Map, Name) t1 INNER JOIN (SELECT Map, ROUND(MIN(Time), 3) AS bestTime FROM race_race GROUP BY Map) t2 ON t1.Map = t2.Map INNER JOIN (SELECT Map, CASE WHEN Server = 'Short' THEN 5.0 WHEN Server = 'Middle' THEN 3.5 WHEN Server = 'Long' THEN CASE WHEN Stars = 0 THEN 2.0 WHEN Stars = 1 THEN 1.0 WHEN Stars = 2 THEN 0.03 END WHEN Server = 'Fastcap' THEN 5.0 END AS S FROM race_maps) t3 ON t1.Map = t3.Map) t WHERE mapPoints != 0 GROUP BY Name ON DUPLICATE KEY UPDATE Points=VALUES(Points)")
        count = c.rowcount
        c.execute("INSERT INTO race_catpoints SELECT Server, Name, SUM(mapPoints) FROM (SELECT Server, t1.Name as Name, FLOOR(100*EXP(-S*(playerTime/bestTime-1))) as mapPoints FROM (SELECT Map, Name, ROUND(MIN(Time), 3) AS playerTime FROM race_race GROUP BY Map, Name) t1 INNER JOIN (SELECT Map, ROUND(MIN(Time), 3) AS bestTime FROM race_race GROUP BY Map) t2 ON t1.Map = t2.Map INNER JOIN (SELECT Server, Map, CASE WHEN Server = 'Short' THEN 5.0 WHEN Server = 'Middle' THEN 3.5 WHEN Server = 'Long' THEN CASE WHEN Stars = 0 THEN 2.0 WHEN Stars = 1 THEN 1.0 WHEN Stars = 2 THEN 0.03 END WHEN Server = 'Fastcap' THEN 5.0 END AS S FROM race_maps) t3 ON t1.Map = t3.Map) t WHERE mapPoints != 0 GROUP BY Server, Name ON DUPLICATE KEY UPDATE Points=VALUES(Points)")
        count += c.rowcount
        print("Corrected {} point entries ({:.2f} sec)".format(count, time.time() - starttime))

        c.execute("DELETE FROM race_points WHERE Points = 0")
        count = c.rowcount
        c.execute("DELETE FROM race_catpoints WHERE Points = 0")
        count += c.rowcount
        print("Deleted {} zero point entries".format(count))

        c.execute("DELETE t1 FROM race_saves t1 LEFT JOIN (SELECT Map FROM race_maps WHERE Server='Long') t2 ON t1.Map = t2.Map WHERE t2.Map IS NULL")
        print("")
        print("Deleted {} non-long saves".format(c.rowcount))
