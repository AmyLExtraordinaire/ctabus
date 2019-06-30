import pandas as pd
import numpy as np
import argparse
import json
import glob
import os.path
import tools
import definitions

def load_timetable(filename):
  timetable = pd.read_csv(timetables_path + filename)
  timetable[stop_list] = timetable[stop_list].apply(pd.to_datetime)
  return timetable

def get_destination_stops(patterns, stop, direction):
  filtered = patterns[(patterns.stpid == stop) & (patterns.rtdir == direction)]
  query_str = " | ".join(["(pid == '{}' & seq > {})".format(pid, seq) for pid, seq in zip(filtered.pid, filtered.seq)])
  return list(patterns.query(query_str).stpid.unique())

def timedelta_to_decimal(td):
  return round(abs((td / np.timedelta64(1, 'D')) * 1440), 2)

def calculate_travel_times(df, origin, destinations):
  df[destinations] = df[destinations].sub(df[origin], axis=0)
  df[destinations] = df[destinations].applymap(timedelta_to_decimal)
  return df

def calculate_wait_times_OLD(df, stop):
  df["wait_time"] = df[stop] - df[stop].shift(-1)

  # removes wait times calculated between service days
  df["day_diff"] = df.start_date - df.start_date.shift(-1)
  df.loc[df.day_diff.dt.days != 0, "wait_time"] = None

  df.drop(columns=[stop, "day_diff"], inplace=True)
  df.wait_time = df.wait_time.apply(timedelta_to_decimal)
  return df

def calculate_wait_times(df, origin, terminal, pids):
  mask = df.pid.isin(pids)
  wait_col = "wait|{}".format(terminal)
  df.loc[mask, wait_col] = df.loc[mask, origin] - df.loc[mask, origin].shift(-1)

  # removes wait times calculated between service days
  df.loc[mask, "day_diff"] = df[mask].start_date - df[mask].start_date.shift(-1)
  df.loc[df.day_diff.dt.days != 0, wait_col] = None

  df.drop(columns=["day_diff"], inplace=True)
  df.loc[mask, wait_col] = df.loc[mask, wait_col].apply(timedelta_to_decimal)
  return df

# TO DO: organize and limit number of columns in output
def build_travel_waits_df(df, patterns, rtdir):
  #info_columns = ["start_date", "pid", "tatripid", "decimal_time", "wait_time"]
  info_columns = ["start_date","pid","tatripid"]

  stop_list = list(patterns[patterns.rtdir == rtdir].stpid.dropna().unique())
  directional_df = df.loc[df.rtdir == rtdir, stop_list + info_columns]
  #directional_df[stop_list] = directional_df[stop_list].apply(pd.to_datetime)

  terminals = list(patterns.loc[patterns[patterns.rtdir == rtdir].groupby('pid').seq.idxmax(), "stpid"].unique())
  pid_dict = {stp: list(patterns.loc[patterns.stpid == stp, "pid"].unique()) for stp in terminals}

  travels_waits = []
  for origin in stop_list:
    destinations = get_destination_stops(patterns, origin, rtdir)
    if not destinations:
      continue

    #orgin_and_dests = [origin] + destinations
    sorted_df = directional_df.sort_values(by=origin) # sorting by arrival times in origin column
    sorted_df["decimal_time"] = sorted_df[origin].map(lambda x: round(x.hour + x.minute / 60.0, 2))

    sorted_df = calculate_travel_times(sorted_df, origin, destinations)        
    #sorted_df = calculate_wait_times(sorted_df, origin)
    for terminal in terminals:
      if terminal in destinations:
        calculate_wait_times(sorted_df, origin, terminal, pid_dict[terminal])

    #melted_df = pd.melt(sorted_df, id_vars=info_columns, value_vars=destinations, var_name="destination", value_name="travel_time")
    #melted_df.dropna(subset=["wait_time", "travel_time"], inplace=True)
    #melted_df["origin"] = origin
    sorted_df.loc[:, sorted_df.columns.isin(set(stop_list) - set(destinations))] = None
    sorted_df["origin"] = origin
    sorted_df.dropna(subset=stop_list, how='all', inplace=True)
    #travels_waits.append(melted_df)
    travels_waits.append(sorted_df)
  return pd.concat(travels_waits, ignore_index=True)

def write_travel_waits(travels_waits, rt, rtdir, tag):
  tools.check_if_path_exists(definitions.TRAVELS_WAITS_DIR)
  out_path = os.path.join(definitions.TRAVELS_WAITS_DIR, "{}_{}_{}_travels_waits.csv".format(rt, rtdir.lower(), tag))
  travels_waits.to_csv(out_path, index=False)

def main(rt, tag):
  print "processing route {} for period {}...".format(rt, tag)
  timetable = tools.load_timetable(rt, tag)
  print "loaded timetable"
  patterns = tools.load_patterns(rt, False)
  print "loaded patterns"

  for rtdir in patterns.rtdir.unique():
    travels_waits = build_travel_waits_df(timetable, patterns, rtdir)
    print "built {} travels_waits".format(rtdir)
    write_travel_waits(travels_waits, rt, rtdir, tag)
    print "saved {} travels_waits".format(rtdir)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  parser.add_argument('-t', '--tag', default='')
  args = parser.parse_args()
  main(args.rt, args.tag)
