import sqlite3
import pandas as pd
import numpy as np
import arrow
import argparse
import json
import glob
import os
from tools import *

def build_sql_query(params):
  sql = "SELECT * FROM vehicles WHERE rt=:rt"
  if 'start_date' in params:
    sql += " AND tmstmp >= :start_date"
  if 'end_date' in params:
    sql += " AND tmstmp < :end_date"
  sql += ";"
  return sql

def load_raw_data(db_path, **kwargs):
  params = {k:v for k,v in kwargs.items() if v is not None}
  sql = build_sql_query(params)
  with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query(sql, conn, params=params)
  return df

def load_routes():
  # TO DO: FIX PATH
  with open("../../data/raw/getroutes/routes.json") as f:
    routes_json = json.load(f)
  routes = [route.get('rt') for route in routes.get('bustime-response').get('routes')]
  return routes

def load_patterns(rt):
  dfs = []
  # TO DO: FIX PATH
  for file in glob.glob(os.path.join(patterns_path, "{}_*".format(rt))):
    with open(file) as f:
      pattern_json = json.load(f)
    stops = [stop for stop in pattern_json.get('pt') if stop.get('typ') != "W"]
    df = pd.DataFrame(stops)
    pattern_json.pop('pt')
    dfs.append(df.assign(**pattern_json))
  patterns = pd.concat(dfs, ignore_index=True)
  patterns.pid = patterns.pid.astype(str)
  return patterns

def shift_terminal_stop_pdists(patterns):
  patterns.loc[np.intersect1d(patterns.groupby('pid').seq.idxmin(), patterns[patterns.pdist < 500].index), "pdist"] = 500
  idxs = np.intersect1d(patterns.groupby('pid').seq.idxmax(), patterns[patterns.pdist > patterns.ln - 500].index)
  pattern_lengths = patterns.loc[idxs].ln 
  patterns.loc[idxs, "pdist"] = pattern_lengths - 500

def remove_unknown_patterns(df, patterns):    
  not_include = set(df.pid) - set(patterns.pid)
  df.drop(df[df.pid.isin(not_include)].index, inplace=True)
  print "Deleted pattern IDs {}".format(list(not_include))

def create_unique_ids(df):
  df["unix_tmstmp"] = df.tmstmp.apply(lambda x: arrow.get(x, 'US/Central').timestamp)
  df.sort_values(["tatripid", "tmstmp"], inplace=True)
  # If two data points with same tripID are more than 30 minutes a part, they probably belong to different trips
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

# Holiday schedules
# Our services operate on a Sunday schedule on New Year's Day, Memorial Day,
# July 4th (Independence Day), Labor Day, Thanksgiving Day and Christmas Day.
holidays = [
  "2017-01-01", "2017-05-29", "2017-07-04", "2018-09-04", "2018-11-23", "2017-12-25",
  "2018-01-01", "2018-05-28", "2018-07-04", "2018-09-03", "2018-11-22", "2018-12-25",
  "2019-01-01", "2019-05-27", "2019-07-04", "2019-09-02", "2019-11-28", "2019-12-25"
]
cta_holidays = pd.DatetimeIndex(holidays)
# TO DO: FIX PATH
timetables_path = "../../data/processed/timetables/"

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
  timetable["holiday"] = timetable.start_date.isin(cta_holidays)
  return timetable

def write_timetable(timetable, rt):
  # TO DO: FIX PATH
  check_if_path_exists(timetables_path)
  out_path = os.path.join(timetables_path, "{}_timetable.csv".format(rt))
  timetable.to_csv(out_path, index=False)

def main(db_path, route, start_date, end_date):
  if not route:
    rts = load_routes()
  else:
    rts = [route]

  for rt in rts:
    print "processing route {}...".format(rt)

    df = load_raw_data(db_path, rt=rt, start_date=start_date, end_date=end_date)
    print "loaded raw data"
    patterns = load_patterns(rt)
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
  parser.add_argument('-r', '--route', help='chose a route to process')
  parser.add_argument('-s', '--start')
  parser.add_argument('-e', '--end')
  args = parser.parse_args()
  main(args.db, args.route, args.start, args.end)
