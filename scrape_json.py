import datetime
import json
import boto3
import time
import urllib3
from my_utils.my_logging import log_error, log_return, log_warning, log_message as log
from my_utils.platform_vars import ROOTDIR, dir_sep
from steam_scraper.main import run_scrape, steam_special_url_firstpage

is_test = True

def get_proxy_instance(ec2):
    resp = ec2.describe_instances()
    for inst in resp["Reservations"][0]["Instances"]:
        for tag in inst["Tags"]:
            if tag["Value"] == "steam_app":
                return inst
    return None


def test_proxy(proxy):
    cont = False
    try:
        urllib3.ProxyManager(proxy_url=proxy).request("GET", steam_special_url_firstpage)
        cont = True
    except Exception as e:
        log_error(str(e))
    return cont


def do_scrape(path, proxy = None):
    results, keys = run_scrape(is_test=is_test, proxy=proxy)

    served_subdir = "served"

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

    log("done dumping json")

proxy_port = 3128
bucket_name = "steamfilterapp"


def main():
    # todo make filter configureable
    # todo make all the names a lot nicer
    # todo add commandline options

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

    for region in regions["proxied"]:
        ec2 = boto3.client("ec2", region_name=region)
        inst = get_proxy_instance(ec2)
        inst_id = inst["InstanceId"]

        if inst is None:
            log_warning("no instance found in {}".format(region))
        else:

            tries = 5
            while inst["State"]["Name"] != "running" and tries > 0:
                log("instance not running in {}. {} tries left.".format(region, tries))
                ec2.start_instances(InstanceIds=[inst_id])
                time.sleep(45)
                inst = get_proxy_instance(ec2)
                tries -= 1

            proxy_ip = inst["PublicIpAddress"]
            proxy = "http://{}:{}".format(proxy_ip, proxy_port)
            path = ROOTDIR + dir_sep + "served" + dir_sep + region + ".json"
            do_scrape(path, proxy)
            ec2.stop_instances(InstanceIds=[inst_id])
            s3 = boto3.resource("s3")
            s3.meta.client.upload_file(path, bucket_name, region + ".json")


    region_name = regions["proxyless"]
    path = ROOTDIR + dir_sep + "served" + dir_sep + region_name + ".json"
    do_scrape(path)
    s3 = boto3.resource("s3")
    s3.meta.client.upload_file(path, bucket_name, path)


if __name__ == '__main__':
    main()
else:
    print("This file must be run as main.")
