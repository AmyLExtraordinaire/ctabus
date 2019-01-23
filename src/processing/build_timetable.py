import sqlite3
import pandas as pd
import arrow
import argparse
from tools.py import *

def load_raw_data(db_path, rt):
  with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query(
    	"SELECT * FROM vehicles WHERE rt=?",
    	conn,
    	params=(rt,)
    )
  return df

def remove_unknown_patterns(df, patterns):    
  not_include = set(df.pid) - set(patterns.pid)
  df.drop(df[df.pid.isin(not_include)].index, inplace=True)
  print "Deleted pattern IDs {}".format(list(not_include))

def create_unique_ids(df):
  df["unix_tmstmp"] = df.tmstmp.apply(lambda x: arrow.get(x, 'US/Central').timestamp)
  df.sort_values(["tripid", "tmstmp"], inplace=True)
  # If two data points with same tripID are more than 30 minutes a part, they probably belong to different trips
  # In practice, such data points will usually (but not always), be at least 24 hours apart.
  g = df.groupby(["tripid", (df.tmstmp.diff() > pd.Timedelta('30 minutes')).astype(int).cumsum()])
  idxmins = g.unix_tmstmp.idxmin()
  df_idxmins = df.loc[idxmins]
  df.loc[idxmins, "ID"] = (df_idxmins.tmstmp - pd.DateOffset(hours=3)).dt.strftime('%Y%m%d') + "_" + df_idxmins.pid + "_" + df_idxmins.tripid
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

def main(db_path, rt):
  df = load_raw_data(db_path, rt)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('db', help='sqlite db path')
  parser.add_argument('rt', help='chose a route to process')
  args = parser.parse_args()
  main(args.db, args.rt)
