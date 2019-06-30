import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import os.path
import tools
import definitions
import argparse

def pattern_to_geodf(pattern):
  df = pattern.copy()
  df.sort_values('seq', inplace=True)
  df.ffill(inplace=True)
  df.dropna(inplace=True)

  df['lon_lat'] = [[xy] for xy in zip(df.lon, df.lat)]
  grouped = df.groupby(['stpid']).lon_lat.agg('sum').to_frame().reset_index()

  merged = df.merge(grouped, on='stpid')
  merged = merged[merged.typ != "W"]
  merged.rename({'lon_lat_y': 'coordinates', 'lon_lat_x': 'lon_lat'}, inplace=True, axis='columns')
  merged.coordinates = (merged.coordinates + merged.lon_lat.shift(-1))
  merged.dropna(inplace=True)

  geometry = [LineString(xys) for xys in merged.coordinates]
  gdf = gpd.GeoDataFrame(merged, geometry=geometry)
  gdf.drop(['lon', 'lat', 'lon_lat', 'coordinates'], inplace=True, axis=1)
  return gdf

def write_geojson(gdf, rt, pid):
  tools.check_if_path_exists(definitions.GEOMETRY_DIR)
  out_path = os.path.join(definitions.GEOMETRY_DIR, "{}_{}.geojson".format(rt, pid))
  gdf.to_file(out_path, driver='GeoJSON')
  # run bash script to convert geojson to topojson

def main(rt, pid):
  patterns = tools.load_patterns(rt, waypoints=True)
  pattern = patterns.loc[patterns.pid == int(pid)]
  gdf = pattern_to_geodf(pattern)
  write_geojson(gdf, rt, pid)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--rt', help='choose a route to process')
  parser.add_argument('-p', '--pid', default='')
  args = parser.parse_args()
  main(args.rt, args.pid)