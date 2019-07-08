import pandas as pd
import numpy as np
import tools
import definitions
import os.path
import glob
import json

def process(df):
  bins = np.arange(0,61)
  labels = np.arange(0,60)
  df["min"] = np.floor((df.decimal_time % 1) * 60)
  df["hr"] = df.decimal_time // 1
  df["bin"] = pd.cut(df["min"], bins=bins, right=False, labels=labels)

  first_stop = 1451

  data = []
  for h in sorted(df[df.origin == first_stop].hr.unique()):
    data.append({"hr": h, "data": df[(df.origin == first_stop) & (df.start_date.dt.dayofweek < 5) & (df.hr == h)].cut.value_counts().sort_index().tolist()})

  return df

def write_departures(df, rt, rtdir):
  file_path = os.path.join(definitions.DEPARTURES_DIR, "{}_{}_departures.json".format(rt, rtdir))
  with open(file_path, "w") as f:
    json.dump(data, f)

def main(rt, rtdir):
  # do this with timetables instead of tw?
  tw_path = os.path.join(definitions.TRAVELS_WAITS_DIR, "{}_{}_*_travels_waits.csv".format(rt, rtdir))
  tw = load_all_dfs(tw_path)
  tw.start_date = pd.to_datetime(tw.start_date)
  departures = process(tw)
  write_departures(departures, rt, rtdir)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  parser.add_argument('-d', '--rtdir', default='')
  args = parser.parse_args()
  main(args.rt, args.rtdir)