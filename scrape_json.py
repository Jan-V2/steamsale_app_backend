import datetime
from pprint import pprint
import json

from my_utils.platform_vars import ROOTDIR, dir_sep
from steam_scraper.main import run_scrape

if __name__ == '__main__':
    results, keys = run_scrape(is_test=True)

    served_subdir = "served"

    # todo make filter configureable
    # todo make all the names a lot nicer
    # todo add commandline options

    json_output = {
        "timestamp": str(datetime.datetime.now()),
        "filter settings": {
            "minimum_discount": 40,
            "min_reviews": 10,
            "min_positive": 40
        }, "items": []
    }

    for i in range(len(results)):
        item = {}

        for key in keys:
            item[key] = results[i][keys[key]]

        json_output["items"].append(item)

    with open(ROOTDIR + dir_sep + served_subdir + dir_sep + "steamsale_data.json", "w", encoding='UTF-8') as json_file:
        json_file.write(json.dumps(json_output, indent=4))

    print("done dumping json")

else:
    print("This file must be run as main.")
