import datetime
from pprint import pprint
import json

from my_utils.platform_vars import ROOTDIR, dir_sep
from steam_scraper.main import run_scrape


results, keys = run_scrape(True)

json_output = {}
json_output["timestamp"] = str(datetime.datetime.now())
json_output["filter settings"] = {}#todo
json_output["items"] = []

for i in range(len(results)):
    item = {}

    for key in keys:
        item[key] = results[i][keys[key]]


    json_output["items"].append(item)

with open(ROOTDIR + dir_sep + "steamsale_data.json", "w", encoding='UTF-8') as json_file:
    json_file.write(json.dumps(json_output, indent=4))


print("done")