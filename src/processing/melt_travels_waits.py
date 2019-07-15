import tools
import definitions
import pandas as pd
import os.path
import argparse
import json

def main(rt, rtdir, tag):
  df = tools.load_travels_waits(rt, rtdir, tag)
  travel_cols = df.columns[df.columns.str.contains("^[0-9]+")]
  wait_cols = df.columns[df.columns.str.contains("wait\|")]
  df["day_of_week"] = df.start_date.dt.dayofweek

  stpid_path = os.path.join(os.path.join(definitions.PROJECT_PAGE_DATA_DIR, "defaults"), "{}_defaults.json".format(rt))
  with open(stpid_path) as f:
    use_stpids = json.load(f)["stpids"] 

  melted = pd.melt(df, id_vars=["origin", "day_of_week", "decimal_time"] + list(wait_cols), value_vars=travel_cols, var_name="destination", value_name="travel_time")
  melted.dropna(subset=["travel_time"], inplace=True)
  melted.drop(melted.loc[~(melted.origin.isin(use_stpids) | melted.destination.isin(use_stpids))].index, inplace=True)

  out_dir = os.path.join(definitions.PROJECT_PAGE_DATA_DIR, "travels_waits/{}".format(rt))
  tools.check_if_path_exists(out_dir)
  for origin in melted.origin.unique():
    out_path = os.path.join(out_dir, "{}_{}_{}_{}_tw.csv".format(rt, rtdir.lower(), tag, origin))
    melted[melted.origin == origin].to_csv(out_path, index=False)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  parser.add_argument('-d', '--rtdir')
  parser.add_argument('-t', '--tag')
  args = parser.parse_args()
  main(args.rt, args.rtdir, args.tag)
