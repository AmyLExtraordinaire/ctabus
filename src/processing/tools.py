import os
import json

def check_if_path_exists(path):
  try:
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
      raise

def load_routes():
  with open(os.path.join(definitions.ROUTES_DIR, "routes.json")) as f:
    rts_json = json.load(f)
  routes = [rts.get('rt') for rts in rts_json.get('bustime-response').get('routes')]
  return routes
