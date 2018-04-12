# -*- coding: utf-8 -*-
import collections

import bs4
import urllib3
import re
from my_utils.my_logging import log_message as log, log_return
from my_utils.util_funcs import listmerger, list_demerger, get_methods_from_class
from steam_scraper.filter import Filter
from steam_scraper.data_scraper import Data_Scraper


steam_special_url_firstpage = "http://store.steampowered.com/search/?specials=1"
and_page = "&page="

html_file = "test.html"


def run_scrape(is_test, proxy=None):
    log("running scrape")
    if proxy is None:
        http = urllib3.PoolManager()
    else:
        http = urllib3.ProxyManager(proxy_url=proxy)

    results_as_strs = []
    if is_test:
        num_pages = 3
    else:
        num_pages = get_number_pages()
    data_scraper = Data_Scraper()
    for i in range(1,  num_pages+1):
        page_results_as_bs4 = get_results_from_page_n(i, http)
        log("got page " + str(i) + "/" + str(num_pages))
        apply_data_scraping(page_results_as_bs4, data_scraper)

    merged_results, keys = apply_filters(data_scraper.scraped_dict)
    log('scrape done')
    return merged_results, keys


def apply_data_scraping(page_as_bs4, data_scraper):
    methods = get_methods_from_class(data_scraper)  # returns list of 2 tuoles 0 = name 1 = method
    for method in methods:
        method[1](page_as_bs4)


def apply_filters(scraped_dict):
    keys = collections.defaultdict(int)# a dict contianing the indexes for bits of data
    merged_results = []

    i = 0
    for key in scraped_dict.keys():
        merged_results.append(scraped_dict[key])
        keys.update({key: i})
        i += 1

    merged_results = listmerger(merged_results)
    filter = Filter()
    for method in get_methods_from_class(filter):
        merged_results = method[1](merged_results, keys)

    return merged_results, keys


def get_results_from_page_n(page_n, http):
    page_results = []
    if page_n == 1:  # page 1 is special because it has no &page=n
        url =  steam_special_url_firstpage
    else:
        url = steam_special_url_firstpage + and_page + str(page_n)

    page = bs4.BeautifulSoup(http.request("GET", url).data, 'html.parser')

    i = page.find_all("a", {"class": "search_result_row"})
    for result in i:
        page_results.append(result)
    return page_results


def get_result_list(pages):
    results = []
    for page in pages:
        i = page.find_all("a", {"class": "search_result_row"})
        for result in i:
            results.append(result)
        i.clear()
    return results

def get_number_pages():
    first_page = http.request("GET", steam_special_url_firstpage)
    html_soup = bs4.BeautifulSoup(first_page.data, 'html.parser')

    result = html_soup.find_all("div", {"class": "search_pagination_right"})
    result = str(result)

    searchstring = 'page='
    pagelist = [m.start() for m in re.finditer(searchstring, result)]

    # it assumes that the 2nd to last result is the total number of pages
    index = pagelist[len(pagelist) - 2] + len(searchstring)
    # this code
    i = 0
    page_number = ""
    while result[index + i] != "\"":
        page_number += result[index + i]
        i += 1

    return int(page_number)



# todo i could make this more effecient by doing basic data scrape -> filter -> rest of datascraping
if __name__ == '__main__':
    from pprint import pprint
    #pprint(run_scrape(True, "http://13.231.152.169:3128"))
    pprint(run_scrape(True, None))