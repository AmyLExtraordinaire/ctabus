import pandas as pd
import numpy as np
import tools
import definitions
import os.path
import glob
import json
import argparse

first_stop = 1451

def preprocess(df):
  df.start_date = pd.to_datetime(df.start_date)
  #bins = np.arange(0,61)
  #labels = np.arange(0,60)
  day_mapping = {0: "W", 1: "W", 2: "W", 3: "W", 4: "W", 5: "S", 6: "U"}
  #df["hr"] = df.decimal_time // 1
  #df["min"] = np.floor((df.decimal_time % 1) * 60)
  #df["bin"] = pd.cut(df["min"], bins=bins, right=False, labels=labels)
  df["dow"] = df.start_date.dt.dayofweek.map(day_mapping)
  return df

def process(df, origin):
  bins = np.arange(0,61)
  labels = np.arange(0,60)
  df["hr"] = df[origin].dt.hour
  df["min"] = df[origin].dt.minute
  df["bin"] = pd.cut(df["min"], bins=bins, right=False, labels=labels)
  return df

def build_hourly_departures(df, terminals):
  json_obj = {}
  for pid in df.pid.unique():
    by_pid = []
    origin_stpid = terminals.loc[terminals.pid == pid, "stpid"].unique()[0]
    tmp = df.loc[df.pid == pid].copy()
    tmp = process(tmp, origin_stpid)
    for d in ["W", "S", "U"]:
      if d not in tmp.dow.unique():
        continue
      num_days = tmp.groupby(["dow"]).nunique().start_date.reset_index()
      hourly_departures = []
      hr_avgs = tmp[(tmp.dow == d)].groupby(["dow", "pid", "hr", "start_date"]).count().unstack().fillna(0).stack().groupby(["dow", "pid", "hr"])[origin_stpid].mean().reset_index().round(1)
      for h in sorted(tmp[~pd.isnull(tmp[origin_stpid]) & (tmp.dow == d)].hr.unique()):
        departures = (tmp[(tmp.dow == d) & (tmp.hr == h)]["bin"].value_counts().sort_index() / float(num_days.loc[num_days.dow == d, "start_date"])).tolist()
        avg = float(hr_avgs.loc[hr_avgs.hr == h, origin_stpid])
        hourly_departures.append({"hr": int(h), "departures": departures, "avg": avg})
      by_pid.append({"stpid": origin_stpid, "dow": d, "data": hourly_departures})
    json_obj[str(pid)] = by_pid
  return json_obj



def build_daily_departures(df, terminals):
  daily_depatures = []
  for rtdir in sorted(terminals.rtdir.unique()):
    data = []
    for pid in terminals[terminals.rtdir == rtdir].pid.unique():
      origin_stpid = terminals.loc[terminals.pid == pid, "stpid"].unique()[0]
      daily = df[df.pid == pid].groupby(["dow", "pid", "start_date"])[origin_stpid].count().groupby(["dow", "pid"]).mean().reset_index().round().rename(columns={origin_stpid: "counts"})
      origin = terminals.loc[terminals.pid == pid, "stpnm_x"].unique()[0]
      destination = terminals.loc[terminals.pid == pid, "stpnm_y"].unique()[0]
      counts = {d.lower(): int(daily.loc[daily.dow == d, "counts"]) if d in list(daily.dow) else 0 for d in ["W", "S", "U"]}
      data.append({"pid": int(pid), "origin": origin, "destination": destination, "counts": counts})
    daily_depatures.append({"direction": rtdir, "data": data})
  return daily_depatures

def write_departures(json_obj, rt, tag):
  tools.check_if_path_exists(definitions.DEPARTURES_DIR)
  daily_path = os.path.join(definitions.DEPARTURES_DIR, "{}_{}_departures.json".format(rt, tag))
  with open(daily_path, "w") as f:
    json.dump(json_obj, f)

def main(rt):
  timetables_path = os.path.join(definitions.TIMETABLES_DIR, "{}_*_timetable.csv".format(rt))
  tt = tools.load_all_dfs(timetables_path)
  tt = preprocess(tt)

  patterns = tools.load_patterns(rt, False)
  g = patterns.groupby(["pid"])
  idxmins = g.seq.idxmin()
  first_stops = patterns.loc[idxmins]
  idxmaxs = g.seq.idxmax()
  last_stops = patterns.loc[idxmaxs]
  terminals = first_stops.merge(last_stops[["pid", "stpnm"]], on='pid')

  tt[list(first_stops.stpid)] = tt[list(first_stops.stpid)].apply(pd.to_datetime)

  hourly_departures = build_hourly_departures(tt, terminals)
  daily_departures = build_daily_departures(tt, terminals)
  write_departures(hourly_departures, rt, "hourly")
  write_departures(daily_departures, rt, "daily")

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  args = parser.parse_args()
  main(args.rt)