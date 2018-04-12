import datetime
import json
from pprint import pprint, pformat

import boto3
from my_utils.my_logging import log_error, log_return, log_warning
from my_utils.platform_vars import ROOTDIR, dir_sep
from steam_scraper.main import run_scrape


proxy_port = 3128

if __name__ == '__main__':

    # todo make filter configureable
    # todo make all the names a lot nicer
    # todo add commandline options
    # todo get list of instance ids
    # todo check if each instance is online and get ip
    # todo if not online start proxies and move on to the next. if everything is done just wait 5 mins.
    # todo scrape and save each region inside try catch then stop proxies
    # todo copy all files to s3 bucket

    regions = {
        "proxyless":  "eu-central-1"
        ,
        "proxied": [
            "ap-northeast-1",
            "eu-west-2",
            "us-east-1",
            "ap-southeast-2"
        ]
    }

    def get_proxy_instance(region):
        ec2 = boto3.client("ec2", region_name=region)
        resp = ec2.describe_instances()
        for inst in resp["Reservations"][0]["Instances"]:
            for tag in inst["Tags"]:
                if tag["Value"] == "steam_app":
                    return inst
        return None


    for region in regions["proxied"]:
        inst = get_proxy_instance(region)

        if inst is None:
            log_warning("instance not found in {}".format(region))
        else:
            proxy_ip = ""
            if inst["state"]["name"] != "running":
                pass
                # start instance
            else:
                proxy_ip = inst["PublicIpAddress"]

            # check if steamstore is reachable through proxy

            # do the scrape

            # stop the instance

            # upload to bucket


    # results, keys = run_scrape(is_test=False)
    #
    # served_subdir = "served"
    #
    # json_output = {
    #     "timestamp": str(datetime.datetime.now()),
    #     "filter settings": {
    #         "minimum_discount": 40,
    #         "min_reviews": 10,
    #         "min_positive": 40
    #     }, "items": []
    # }
    #
    # for i in range(len(results)):
    #     item = {}
    #
    #     for key in keys:
    #         item[key] = results[i][keys[key]]
    #
    #     json_output["items"].append(item)
    #
    # with open(ROOTDIR + dir_sep + served_subdir + dir_sep + "steamsale_data.json", "w", encoding='UTF-8') as json_file:
    #     json_file.write(json.dumps(json_output, indent=4))
    #
    # print("done dumping json")

else:
    print("This file must be run as main.")
