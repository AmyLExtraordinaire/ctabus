import json
import os.path
import tools
import definitions
import argparse

def main(rt):
  defaults_path = os.path.join(os.path.join(definitions.PROJECT_PAGE_DATA_DIR, "defaults"), "{}_defaults.json".format(rt))

  with open(defaults_path) as f:
    defaults = json.load(f)

  pid1, pid2 = defaults["pids"]
  use_stpids = defaults["stpids"]

  patterns = tools.load_patterns(rt, False)
  patterns.stpid = patterns.stpid.astype(int)
  patterns = patterns.loc[(patterns.pid.isin([int(pid1), int(pid2)])) & (patterns.stpid.isin(use_stpids))]

  df1 = patterns[patterns.pid == int(pid1)]
  df2 = patterns[patterns.pid == int(pid2)]

  data = {df1.rtdir.unique()[0]: df1.to_dict(orient='records'), df2.rtdir.unique()[0]: df2.to_dict(orient='records')}
  out_path = os.path.join(os.path.join(definitions.PROJECT_PAGE_DATA_DIR, "stop_lists"), "{}_stop_list.json".format(rt))
  
  with open(out_path, 'w') as f:  
    json.dump(data, f)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  args = parser.parse_args()
  main(args.rt)