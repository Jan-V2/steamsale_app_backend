import datetime
import json
import traceback

import boto3
import time
import urllib3
from my_utils.my_logging import log_error, log_return, log_warning, log_message as log
from my_utils.platform_vars import ROOTDIR, dir_sep
from steam_scraper.scraper_main import run_scrape, steam_special_url_firstpage
from pprint import pformat
is_test = False
log_return()
proxy_port = 3128
bucket_name = "steamfilterapp"

# def test_proxy(proxy): not currently in use
#     cont = False
#     try:
#         urllib3.ProxyManager(proxy_url=proxy).request("GET", steam_special_url_firstpage)
#         cont = True
#     except Exception as e:
#         log_error(str(e))
#     return cont


def do_scrape(region_dict, use_proxy=False):

    aws_region = list(region_dict.keys())[0]
    region_name = region_dict[aws_region]

    def scrape_and_save(_proxy):
        log("scraping {}".format(region_name))
        results, keys = run_scrape(is_test=is_test, proxy=_proxy)
        format_and_save_results(results, keys, region_name)

    if use_proxy:
        log("scraping with proxy in aws region {}".format(aws_region))
        ec2 = boto3.client("ec2", region_name=aws_region)

        def get_proxy_instance(_ec2):
            resp = _ec2.describe_instances()
            for _inst in resp["Reservations"][0]["Instances"]:
                for tag in _inst["Tags"]:
                    if tag["Value"] == "steam_app":
                        return _inst
            return None

        inst = get_proxy_instance(ec2)
        if inst is None:
            log_warning("no instance found in {}".format(aws_region))
        else:
            inst_id = inst["InstanceId"]
            tries = 5
            while inst["State"]["Name"] != "running" and tries > 0:
                log("instance not running in {}. starting now. {} tries left.".format(aws_region, tries))
                ec2.start_instances(InstanceIds=[inst_id])
                time.sleep(45)
                inst = get_proxy_instance(ec2)
                tries -= 1

            proxy_ip = inst["PublicIpAddress"]
            proxy = "http://{}:{}".format(proxy_ip, proxy_port)
            scrape_and_save(proxy)
            log("saved results. now stopping proxy in {}".format(aws_region))
            ec2.stop_instances(InstanceIds=[inst_id])
    else:
        log("doing scrape without proxy in region {}".format(aws_region))
        proxy = None
        scrape_and_save(proxy)


def format_and_save_results(results, keys, region_name):
    served_subdir = "served"
    path = ROOTDIR + dir_sep + "served" + dir_sep + region_name + ".json"

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

    with open(path, "w", encoding='UTF-8') as json_file:
        json_file.write(json.dumps(json_output, indent=4))

    log("done saving json to disk")
    log("saving to s3")
    s3 = boto3.resource("s3")
    s3.meta.client.upload_file(path, bucket_name, region_name + ".json")


def run():
    # todo make filter configureable
    # todo make all the names a lot nicer
    # todo add commandline options
    # todo add much more logging
    # todo there is a bug in the scraper, because way to many doubles are removed

    regions = {
        "proxyless": [{"eu-central-1": "eu"}]
        ,
        "proxied": [
            # {"ap-northeast-1": "japan"},
            # {"eu-west-2": "uk"},
            # {"us-east-1": "usa"},
            # {"ap-southeast-2": "aus"}
        ]
    }

    for region_dict in regions["proxied"]:
        do_scrape(region_dict, True)
    for region_dict in regions["proxyless"]:
        do_scrape(region_dict)


def main():
    try:
        log_return()
        log("starting")
        run()
    except Exception as e:
        log_error(traceback.format_exc())
        log_error(pformat(traceback.format_stack()))
        raise e


if __name__ == '__main__':
    main()
else:
    print("This file must be run as main.")
