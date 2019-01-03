import os
import sys
import sqlite3
import datetime
import requests
import json
import logging
import argparse
import pandas as pd

os.environ['TZ'] = 'US/Central'

insert = """
  INSERT OR IGNORE INTO vehicles (
    vid, tmstmp, lat, lon, hdg, pid, rt, des, pdist, dly, tatripid, tablockid, zone
  ) VALUES (
    :vid, :tmstmp, :lat, :lon, :hdg, :pid, :rt, :des, :pdist, :dly, :tatripid, :tablockid, :zone
  )
"""

database_name = "bustracker.db"
URL = "http://www.ctabustracker.com/bustime/api/v2/getvehicles"
schedule_path = "bus_schedule.csv"

def configure_logger(log_path):
  logging.basicConfig(
    filename=log_path,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
  )

def load_bus_schedule(filepath):
  schedule = pd.read_csv(filepath, dtype=str)
  schedule.first_departure = (pd.to_datetime(schedule.first_departure)).dt.time
  schedule.last_arrival = (pd.to_datetime(schedule.last_arrival)).dt.time
  return schedule    

def get_active_routes():
  now = datetime.datetime.now()
  d = now.weekday()
  t = now.time()
  
  schedule = load_bus_schedule(schedule_path)
  
  if t < datetime.time(3,0):
    d = (d - 1) % 7

  if d < 5:
    weekday_type = "W"
  elif d == 5:
    weekday_type = "S"
  else:
    weekday_type = "U"
  
  active_routes = schedule[(schedule.type == weekday_type) & (schedule.first_departure <= t) & (schedule.last_arrival >= t)].route
  return list(active_routes)

def get_vehicles(api_key):
  vehicles = []
  
  routes = get_active_routes()

  rt_chunks = [routes[i:i+10] for i in xrange(0, len(routes), 10)]
  for chunk in rt_chunks:
    rts_str = ",".join(chunk)
    payload = {'key': api_key, 'rt': rts_str, 'tmres': 's', 'format': 'json'}

    try:
      r = requests.get(URL, params=payload)
    except requests.exceptions.RequestException as e:
      logging.error(e)
      sys.exit(1)

    response = r.json().get('bustime-response')
    
    try:
      vehicles += response.get('vehicle')
    except TypeError:
      e = response.get('error')
      logging.error(e)
      
  return vehicles

def main(api_key, log_path):
  configure_logger(log_path)

  with sqlite3.connect(database_name) as conn:
    c = conn.cursor()
    vehicles = get_vehicles(api_key)
    c.executemany(insert, vehicles)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('key', help='bustracker api key')
  parser.add_argument('--log', default='bustracker_errors.log', help='specify log filepath')
  args = parser.parse_args()
  main(args.key, args.log)
