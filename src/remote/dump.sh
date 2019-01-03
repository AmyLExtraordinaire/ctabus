#!/bin/bash
DATE=`date -d "yesterday 13:00" +%Y%m%d`
sqlite3 bustracker.db <<EOF
.mode csv
.headers on
.output ${DATE}.dmp
SELECT *
FROM vehicles
WHERE (tmstmp >= strftime('%Y%m%d', date('now', '-1 day')) || ' 03:00:00')
  AND (tmstmp < strftime('%Y%m%d', 'now') || ' 03:00:00');
EOF
