import pandas as pd
import tools
import definitions
import glob
import os.path
import argparse

def load_all_waits(rt, rtdir):
  tw_path = os.path.join(definitions.TRAVELS_WAITS_DIR, "{}_{}_*_travels_waits.csv".format(rt, rtdir))
  data_files = glob.glob(tw_path)
  dfs = (pd.read_csv(f) for f in data_files)
  travels_waits  = pd.concat(dfs, ignore_index=True)
  travels_waits.start_date = pd.to_datetime(travels_waits.start_date)
  return travels_waits


def process(df):
  holidays_df = pd.DatetimeIndex(definitions.CTA_HOLIDAYS)
  df["time_of_day"] = pd.cut(df.decimal_time, definitions.CTA_TIME_PERIODS, labels=definitions.CTA_TIME_PERIOD_LABELS, right=False)
  df.drop(df[(df.start_date.dt.dayofweek >= 5) | df.start_date.isin(holidays_df)].index, inplace=True)

  terminals = df.columns[df.columns.str.contains("wait\|")]

  # total number of trips
  tot_trips = df.groupby(["time_of_day", "origin"])[terminals].count()

  # bunching incidents
  df[terminals] = (df[terminals] < 2)
  bunching_incidents = df.groupby(["time_of_day", "origin"])[terminals].sum()

  # proportion of trips that were bunched
  rt_bunching = bunching_incidents / tot_trips

  melted = pd.melt(bunching_incidents.reset_index(), id_vars=["time_of_day", "origin"], value_vars=terminals, var_name="terminal", value_name="count")
  melted["count"] = melted["count"].astype(int)
  melted2 = pd.melt(rt_bunching.reset_index(), id_vars=["time_of_day", "origin"], value_vars=terminals, var_name="terminal", value_name="proportion")
  melted2.proportion = melted2.proportion.fillna(0).map(lambda x: round(x, 2))
  merged = melted.merge(melted2, on=["time_of_day", "origin", "terminal"])
  group = merged.groupby(["terminal", "time_of_day"], as_index=True)
  bunching = group.apply(lambda x: {int(o): {"count": c, "proportion": p} for o,c,p in x[["origin", "count", "proportion"]].values}).reset_index().rename(columns={0: "values"})
  return bunching

def write_bunching(bunching, rt, rtdir):
  tools.check_if_path_exists(definitions.BUNCHING_DIR)
  out_path = os.path.join(definitions.BUNCHING_DIR, "{}_{}_bunching.csv".format(rt, rtdir))
  bunching.to_json(out_path, orient='records')

def main(rt, rtdir):
  df = load_all_waits(rt, rtdir)
  bunching = process(df)
  write_bunching(bunching, rt, rtdir)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  parser.add_argument('-d', '--rtdir', default='')
  args = parser.parse_args()
  main(args.rt, args.rtdir)
