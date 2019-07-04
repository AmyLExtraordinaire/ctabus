import os.path

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__ ,"../..")))
CONFIG_PATH = os.path.join(ROOT_DIR, "keys.config")

# Data directory paths
DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
PROJECT_PAGE_DATA_DIR = os.path.join(DATA_DIR, "project_page")

## Raw data
PATTERNS_DIR = os.path.join(RAW_DATA_DIR, "getpatterns")
ROUTES_DIR = os.path.join(RAW_DATA_DIR, "getroutes")
VEHICLES_DIR = os.path.join(RAW_DATA_DIR, "getvehicles")

## Processed data
TIMETABLES_DIR = os.path.join(PROCESSED_DATA_DIR, "timetables")
TRAVELS_WAITS_DIR = os.path.join(PROCESSED_DATA_DIR, "travels_waits")
BUNCHING_DIR = os.path.join(PROCESSED_DATA_DIR, "bunching")
GEOMETRY_DIR = os.path.join(PROCESSED_DATA_DIR, "geometry")

## Date/Time Definitions 
CTA_TIME_PERIODS = [6, 9, 15, 19, 22]
CTA_TIME_PERIOD_LABELS = ["AM Peak", "Midday", "PM Peak", "Evening"]

# Holiday schedules
# Our services operate on a Sunday schedule on New Year's Day, Memorial Day,
# July 4th (Independence Day), Labor Day, Thanksgiving Day and Christmas Day.
CTA_HOLIDAYS = [
  "2017-01-01", "2017-05-29", "2017-07-04", "2018-09-04", "2018-11-23", "2017-12-25",
  "2018-01-01", "2018-05-28", "2018-07-04", "2018-09-03", "2018-11-22", "2018-12-25",
  "2019-01-01", "2019-05-27", "2019-07-04", "2019-09-02", "2019-11-28", "2019-12-25"
]

## Bus Tracker API
GETVEHICLES_URL = "http://www.ctabustracker.com/bustime/api/v2/getvehicles"
GETPATTERNS_URL = "http://www.ctabustracker.com/bustime/api/v2/getpatterns"
