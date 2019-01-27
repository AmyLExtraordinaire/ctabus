import sqlite3
import pandas as pd
import numpy as np
import arrow
import argparse
import json
import glob
import os.path
import tools
import definitions

def shift_terminal_stop_pdists(patterns):
  patterns.loc[patterns[patterns.pdist < 500].groupby('pid').seq.idxmin(), "pdist"] = 500
  idxs = patterns[patterns.pdist > patterns.ln - 500].groupby('pid').seq.idxmax()
  pattern_lengths = patterns.loc[idxs, "ln"] 
  patterns.loc[idxs, "pdist"] = pattern_lengths - 500

def remove_unknown_patterns(df, patterns):    
  not_include = set(df.pid) - set(patterns.pid)
  df.drop(df[df.pid.isin(not_include)].index, inplace=True)
  print "Deleted pattern IDs {}".format(list(not_include))

def create_unique_ids(df):
  df["unix_tmstmp"] = df.tmstmp.apply(lambda x: arrow.get(x, 'US/Central').timestamp)
  df.sort_values(["tatripid", "tmstmp"], inplace=True)
  # If two data points with same tatripID are more than 30 minutes a part, they probably belong to different trips
  # In practice, such data points will usually (but not always), be at least 24 hours apart.
  g = df.groupby(["tatripid", (df.tmstmp.diff() > pd.Timedelta('30 minutes')).astype(int).cumsum()])
  idxmins = g.unix_tmstmp.idxmin()
  df_idxmins = df.loc[idxmins]
  df.loc[idxmins, "ID"] = (df_idxmins.tmstmp - pd.DateOffset(hours=3)).dt.strftime('%Y%m%d') + "_" + df_idxmins.pid + "_" + df_idxmins.tatripid
  df.ID.ffill(inplace=True)

def remove_short_trips(df):
  df.drop(df.groupby('ID').filter(lambda x: x.pdist.max() - x.pdist.min() < 5000).index, inplace=True)
          
def clean(df, patterns):
  df.drop_duplicates(inplace=True)
  df.tmstmp =  pd.to_datetime(df.tmstmp)
  df.pdist = df.pdist.astype(int)
  remove_unknown_patterns(df, patterns)
  create_unique_ids(df)
  remove_short_trips(df)

def build_query_strings(stop, patterns):
  filtered = patterns[patterns.stpnm == stop][["pid", "pdist"]]

  query_str_before = " | ".join(["(pid == '{}' & pdist < {})".format(pid, pdist) for pid, pdist in zip(filtered.pid, filtered.pdist)])
  query_str_after = " | ".join(["(pid == '{}' & pdist >= {})".format(pid, pdist) for pid, pdist in zip(filtered.pid, filtered.pdist)])
  return query_str_before, query_str_after

def find_linear_interpolant_endpoints(df, stop, patterns):
  query_str_before, query_str_after = build_query_strings(stop, patterns)

  idxmaxs = df.query(query_str_before).groupby('ID').unix_tmstmp.idxmax()
  idxmins = df.query(query_str_after).groupby('ID').unix_tmstmp.idxmin()

  before = df.loc[idxmaxs, ["pdist", "unix_tmstmp", "ID"]].set_index("ID")
  after = df.loc[idxmins, ["pdist", "unix_tmstmp", "ID"]].set_index("ID")

  return before, after

def build_interpolation_table(df, stop, patterns):
  table = pd.DataFrame(np.nan, index=df.ID.unique(), columns=[stop])
  table = table.join(df.groupby('ID').pid.first())

  before, after = find_linear_interpolant_endpoints(df, stop, patterns)
  table = table.join(before, rsuffix="_before").join(after, rsuffix="_after")

  pid_to_pdist = patterns[patterns.stpnm == stop].groupby('pid').pdist.first()
  mask = table.pid.isin(pid_to_pdist.index)
  table.loc[mask, "stop_pdist"] = table[mask].pid.map(pid_to_pdist)

  return table

def interpolate_stop_arrival_times(df, stop, patterns):
  table = build_interpolation_table(df, stop, patterns)
  interpolated_arrivals = (
    ((table.unix_tmstmp_after - table.unix_tmstmp) / (table.pdist_after - table.pdist))
    * (table.stop_pdist - table.pdist)
    + table.unix_tmstmp
  ) 
  mask = pd.notnull(interpolated_arrivals)
  interpolated_arrivals.loc[mask] = interpolated_arrivals[mask].map(lambda x: arrow.get(x).to('US/Central').format('YYYY-MM-DD HH:mm:ss'))
  return interpolated_arrivals

def build_timetable(df, patterns):
  stop_list = patterns.stpnm.dropna().unique()
  timetable = pd.DataFrame(np.nan, index=df.ID.unique(), columns=stop_list)
  timetable.index.name = "ID"

  for stop in stop_list:
    timetable[stop] = interpolate_stop_arrival_times(df, stop, patterns)

  timetable.reset_index(inplace=True)
  # TO DO: Update timetable columns
  timetable[["start_date", "pid", "tatripid"]] = timetable.ID.str.split("_", expand=True)
  timetable["rtdir"] = timetable.pid.map(patterns.groupby('pid').rtdir.first())
  timetable["start_date"] = pd.to_datetime(timetable.start_date)
  timetable["day_of_week"] = timetable.start_date.dt.dayofweek
  cta_holidays = pd.DatetimeIndex(definitions.HOLIDAYS)
  timetable["holiday"] = timetable.start_date.isin(cta_holidays)
  return timetable

def write_timetable(timetable, rt):
  tools.check_if_path_exists(definitions.TIMETABLES_DIR)
  out_path = os.path.join(definitions.TIMETABLES_DIR, "{}_timetable.csv".format(rt))
  timetable.to_csv(out_path, index=False)

def main(db_path, route, start_date, end_date):
  if not route:
    rts = tools.load_routes()
  else:
    rts = [route]

  for rt in rts:

    print "processing route {}...".format(rt)

    df = tools.load_raw_data(db_path, rt=rt, start_date=start_date, end_date=end_date)
    print "loaded raw data"
    patterns = tools.load_patterns(rt, False)
    print "loaded patterns"
    shift_terminal_stop_pdists(patterns)
    print "shifted terminal stops"
    clean(df, patterns)
    print "cleaned"
    timetable = build_timetable(df, patterns)
    print "built timetable"
    write_timetable(timetable, rt)
    print "saved"

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('db', help='sqlite db path')
  parser.add_argument('-r', '--route', help='choose a route to process')
  parser.add_argument('-s', '--start')
  parser.add_argument('-e', '--end')
  args = parser.parse_args()
  main(args.db, args.route, args.start, args.end)
