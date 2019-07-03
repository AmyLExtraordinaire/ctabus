import sqlite3
import pandas as pd
import os.path
import tools
import definitions
import ConfigParser
import argparse
import requests
import json

config = ConfigParser.ConfigParser()
config.read(definitions.CONFIG_PATH)
API_KEY = config.get("ctabustracker", "api_key")

def get_patterns(pids, rt):
  tools.check_if_path_exists(definitions.PATTERNS_DIR)
  
  # the getpatterns API only accepts upto 10 patterns at a time
  pids_chunks = [pids[i:i+10] for i in xrange(0, len(pids), 10)]
  for chunk in pids_chunks:
    pids_str = ",".join(chunk)
    payload = {'key': API_KEY, 'pid': pids_str, 'format': "json"}
    r = requests.get(definitions.GETPATTERNS_URL, params=payload)
    patterns = r.json().get('bustime-response').get('ptr')
          
    for pattern in patterns:
      pid = pattern['pid']
      pattern_path = os.path.join(definitions.PATTERNS_DIR, "{}_{}.json".format(rt, pid))
      with open(pattern_path, 'w') as out_file:
        json.dump(pattern, out_file)

def main(db_path, rt):
  #if not rts:
  #  rts = tools.load_routes()

  print "fetching patterns for route {}...".format(rt)

  with sqlite3.connect(db_path) as conn:
    sql = "SELECT DISTINCT pid FROM vehicles;"
    pids_df = pd.read_sql_query(sql, conn)
  pids_df.pid = pids_df.pid.astype(str)
  get_patterns(pids_df.pid, rt)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('db', help='sqlite db path')
  parser.add_argument('-r', '--rt', nargs='+')
  args = parser.parse_args()
  main(args.db, args.rt)