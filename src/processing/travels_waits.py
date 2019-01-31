import pandas as pd
import numpy as np
import argparse
import json
import glob
import os
import tools

def load_timetable(filename):
  timetable = pd.read_csv(timetables_path + filename)
  timetable[stop_list] = timetable[stop_list].apply(pd.to_datetime)
  return timetable

def get_destination_stops(patterns, stop, direction):
  filtered = patterns[(patterns.stpnm == stop) & (patterns.rtdir == direction)]
  query_str = " | ".join(["(pid == '{}' & seq > {})".format(pid, seq) for pid, seq in zip(filtered.pid, filtered.seq)])
  return list(patterns.query(query_str).stpnm.unique())

def timedelta_to_decimal(td):
  return round(abs((td / np.timedelta64(1, 'D')) * 1440), 2)

def calculate_travel_times(df, origin, destinations):
  df[destinations] = df[destinations].sub(df[origin], axis=0)
  df[destinations] = df[destinations].apply(timedelta_to_decimal)
  return df

def calculate_wait_times(df, stop):
  df["wait_time"] = df[stop] - df[stop].shift(-1)

  # removes wait times calculated between service days
  df["day_diff"] = df.start_date - df.start_date.shift(-1)
  df.loc[df.day_diff.dt.days != 0, "wait_time"] = None

  df.drop(columns=[stop, "day_diff"], inplace=True)
  df.wait_time = df.wait_time.apply(timedelta_to_decimal)
  return df

def build_travel_waits_df(df, patterns, direction):
  info_columns = ["start_date", "pid", "tatripid", "rtdir", "day_of_week", "holiday", "decimal_time", "wait_time"]

  stop_list = patterns[patterns.rtdir == direction].stpnm.dropna().unique()
  directional_df = df.loc[df.rtdir == direction]
  directional_df[stop_list] = directional_df[stop_list].apply(pd.to_datetime)

  travels_waits = []
  for origin in stop_list:
    destinations = get_destination_stops(patterns, origin, direction)

    if not destinations:
      continue

    orgin_and_dests = [origin] + destinations
    sorted_df = directional_df.sort_values(by=origin) # sorting by arrival times in origin column
    sorted_df["decimal_time"] = sorted_df[origin].map(lambda x: round(x.hour + x.minute / 60.0, 2))

    sorted_df = calculate_travel_times(sorted_df, origin, destinations)        
    sorted_df = calculate_wait_times(sorted_df, origin)

    melted_df = pd.melt(sorted_df, id_vars=info_columns, value_vars=destinations, var_name="destination", value_name="travel_time")
    melted_df.dropna(subset=["wait_time", "travel_time"], inplace=True)
    melted_df["origin"] = origin
    travels_waits.append(melted_df)
  return pd.concat(travels_waits, ignore_index=True)

def write_travel_waits():
  #travel_waits_path = "../../data/processed/trips_and_waits/" + str(rt) + "/"
  #check_if_path_exists(travel_waits_path)
  #file_name = travel_waits_path + origin.replace("/", "").replace(".", "") + "_" + direction + ".csv"
  #melted_df.to_csv(file_name, columns=header, header=False, index=False, mode='ab+')
  pass

def main(db_path, route, start_date, end_date):
  if not route:
    rts = tools.load_routes()
  else:
    rts = [route]

  for rt in rts:
    print "processing route {}...".format(rt)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('db', help='sqlite db path')
  parser.add_argument('-r', '--route', help='chose a route to process')
  parser.add_argument('-s', '--start')
  parser.add_argument('-e', '--end')
  args = parser.parse_args()
  main(args.db, args.route, args.start, args.end)
