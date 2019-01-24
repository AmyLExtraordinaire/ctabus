import sqlite3
import pandas as pd
import os.path
import tools
from definitions
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(definitions.CONFIG_PATH)
API_KEY = config.get("ctabustracker", "api_key")

def get_patterns(df):
  tools.check_if_path_exists(definitions.PATTERNS_DIR)
  
  pids = [str(pid) for pid in df.pid.unique()]
  # the getpatterns API only accepts upto 10 patterns at a time
  pids_chunks = [pids[i:i+10] for i in xrange(0, len(pids), 10)]
  for chunk in pids_chunks:
    pids_str = ",".join(chunk)
    payload = {'key': API_KEY, 'pid': pids_str, 'format': "json"}
    r = requests.get(definitions.GETPATTERNS_URL, params=payload)
    patterns = r.json().get('bustime-response').get('ptr')
          
    for pattern in patterns:
      pid = str(pattern['pid'])
      rt = str(df[df.pid == pid].rt.unique()[0])
      pattern_path = os.path.join(definitions.PATTERNS_DIR, "{}_{}.json".format(rt, pid))
      with open(pattern_path, 'w') as out_file:
        json.dump(pattern, out_file)

def main(db_path, route):
  if not route:
    rts = tools.load_routes()
  else:
    rts = [route]

  with sqlite3.connect(db_path) as conn:
    # TO DO: Add WHERE clause with rt=:rt
    pids = pd.read_sql_query("SELECT DISTINCT pid FROM vehicles", conn)       
  get_patterns(pids)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('db', help='sqlite db path')
  parser.add_argument('-r', '--route', help='choose a route to process')
  args = parser.parse_args()
  main(args.db, args.route)