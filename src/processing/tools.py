import os
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("../../keys.config")
API_KEY = config.get("ctabustracker", "api_key")
URL = "http://www.ctabustracker.com/bustime/api/v2/getpatterns"
patterns_path = "../../data/raw/getpatterns/"

def check_if_path_exists(path):
	try:
		os.makedirs(path)
	except OSError:
		if not os.path.isdir(path):
			raise
