import sqlite3
import pandas as pd
from tools import *

def get_patterns(df):
  check_if_path_exists(patterns_path)
  
  pids = [str(pid) for pid in df.pid.unique()]
  # the getpatterns API only accepts upto 10 patterns at a time
  pids_chunks = [pids[i:i+10] for i in xrange(0, len(pids), 10)]
  for chunk in pids_chunks:
    pids_str = ",".join(chunk)
    payload = {'key': API_KEY, 'pid': pids_str, 'format': "json"}      
    r = requests.get(URL, params=payload)
    patterns = r.json().get('bustime-response').get('ptr')
          
    for pattern in patterns:
      pid = str(pattern['pid'])
      rt = str(df[df.pid == pid].rt.unique()[0])
      with open(os.path.join(patterns_path, "{}_{}.json".format(rt, pid)), 'w') as out_file:
        json.dump(pattern, out_file)

def main():
	#db_path = ".db"
  with sqlite3.connect(db_path) as conn:
    pids = pd.read_sql_query("SELECT DISTINCT pid FROM vehicles", conn)       
  get_patterns(pids)

if __name__ == '__main__':
  main()
