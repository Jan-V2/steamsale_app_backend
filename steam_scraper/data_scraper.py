import collections
import traceback
from pprint import pprint, pformat

from my_utils.my_logging import log_message as log, log_warning, log_error
from my_utils.consts import ints_str_list as ints_str
import re

verbose = False


class Data_Scraper:
    # todo make it more elegant by using map rather than having a for loop in each method
    # every methode in this class will be applied to the the results
    # they all must take the list of results as an argument and add a list to the dict in this object and have no return
    # a list in which each result lines up with a result from the argument
    # like this ["review_scores": [list of review scores]]
    scraped_dict = collections.defaultdict(list)
    curr_symbol = "€"  # this is super inelegant
    curr_symbol_list = "¥$€£"

    def get_user_reviews(self, results):
        # returns 2 lists
        # the first list is how many user reviews the result got
        # the second list is what percentage was positive
        n_user_reviews = []
        percent_reviews_positive = []
        found = 0
        if verbose:
            log("scraping reviews")
        for result in results:
            var = result.find("span", {"class": "search_review_summary"})
            if not isinstance(var, type(None)):  # if true it contains a review
                var = str(var)
                of_the_str = "% of the "
                of_the_start = var.find(of_the_str)
                of_the_end = of_the_start + len(of_the_str)
                # this part checks how many of the reviews where positive
                percent_positive_as_str = ""
                for char in var[of_the_start - 3:of_the_start]:  # 3 is because a max of 3 digets
                    if char in ints_str:
                        percent_positive_as_str += char

                percent_reviews_positive.append(int(percent_positive_as_str))

                # this part get how many reviews it got
                temp_n_reviews = ""
                for char in var[of_the_end:]:
                    if char == " ":
                        break
                    else:
                        if not char == "," and not char == ".":
                            temp_n_reviews += char
                # print("reviews " + temp_n_reviews)
                n_user_reviews.append(int(temp_n_reviews))

                found += 1
            else:
                n_user_reviews.append(0)
                percent_reviews_positive.append(0)
        for i in range(len(n_user_reviews)):
            self.scraped_dict['n_user_reviews'].append(n_user_reviews[i])
            self.scraped_dict['percent_reviews_positive'].append(percent_reviews_positive[i])

    def get_discount_percents(self, results_list):
        if verbose:
            log('scraping discount percents')
        discount_percents = []
        for result in results_list:

            discount_elem = result.find("div", {"class", "discount_pct"})
            if discount_elem is not None:
                digits = re.findall("\d+", discount_elem.text)[0]
                discount_percents.append(int(digits))
            else:
                discount_percents.append(0)
        for item in discount_percents:
            self.scraped_dict["discount_percents"].append(item)

    def get_titles_list(self, results_list):
        if verbose:
            log("scraping title")
        for result in results_list:
            self.scraped_dict["titles"].append(
                str(result.find("span", {"class": "title"}).string))

    def get_old_and_new_price(self, results_list):
        if verbose:
            log('scraping the old+new price')

        def set_curr_symbol(_price_str):
            for sym in self.curr_symbol_list:
                if sym in _price_str:
                    self.curr_symbol = sym
                    break

        def safe_to_float(_str):
            try:
                _str = _str.replace(" ", "")
                return float(_str)
            except Exception as e:
                log_error("error converting price to float:")
                log_error(traceback.format_exc())
                log_error(pformat(traceback.format_stack()))
                return float(0)

        for result in results_list:
            def clean(_str):
                def clean_extra_dots(__str):
                    # to deal with prices higher that 1000
                    dots_idx = [m.start() for m in re.finditer("\.", __str)]
                    if len(dots_idx) > 1:
                        log("found multible dots in price {}".format(__str))
                        for dot_idx in reversed(dots_idx[:len(dots_idx) - 1]):
                            __str = __str[:dot_idx] + __str[dot_idx + 1:]
                        log("cleaned multible dots. is now {}".format(__str))
                    return __str

                return clean_extra_dots(
                    _str.replace(',', '.')
                    .replace(self.curr_symbol, "")
                    .replace('--', '0')  # if a price has no decimal places it apparently adds --
                )

            cont = result.find('div', {'class': 'discount_block'})
            if cont is not None:
                elem_old = cont.find("div", {"class": "discount_original_price"})
                elem_new = cont.find("div", {"class": "discount_final_price"})

                if elem_old:
                    old_price = elem_old.text
                    old_price = clean(old_price)
                else:
                    old_price = 0
                if elem_new:
                    new_price = elem_new.text
                    new_price = clean(new_price)
                    new_price = new_price.replace('\t', '') \
                        .replace('\n', '')
                    if "Free" in new_price:
                        new_price = 0
                else:
                    new_price = 0

                if self.curr_symbol is None:
                    set_curr_symbol(old_price)



                self.scraped_dict["old_price"].append(safe_to_float(old_price))
                self.scraped_dict["new_price"].append(safe_to_float(new_price))

            else:
                log_warning("could not find price container, probably because the item isn't discounted. appending 0s")
                self.scraped_dict["old_price"].append(float(0))
                self.scraped_dict["new_price"].append(float(0))

    def get_app_id(self, results_list):
        # THE APP ID(S) ARE STORED AS STRINGS FOR NOW since i don't need them as ints right now.
        # nor can i think of a reason why i should want to.
        if verbose:
            log("scraping appids")
        for result in results_list:
            try:
                if (',' in result['data-ds-appid']):  # if it has multible appids which is when it's an old style bundle
                    self.scraped_dict["appids"].append(
                        result['data-ds-packageid'])
                    self.scraped_dict["is_bundle"].append(True)
                    self.scraped_dict["is_old_bundle"].append(True)
                    self.scraped_dict["new_cdn_id"].append("")

                else:
                    self.scraped_dict["appids"].append(
                        result['data-ds-appid'])
                    self.scraped_dict["is_bundle"].append(False)
                    self.scraped_dict["is_old_bundle"].append(False)
                    self.scraped_dict["new_cdn_id"].append("")
            except KeyError:
                self.scraped_dict["appids"].append(
                    result['data-ds-bundleid'])
                self.scraped_dict["is_bundle"].append(True)
                self.scraped_dict["is_old_bundle"].append(False)

                # The url for the thumbnail.
                url = result.find("div", {"class": "search_capsule"}).find("img")["src"]
                cdn_id = re.search("/(\w+)/capsule", url)

                if cdn_id is None:
                    log_warning("could not find img_id in {} appending blank string".format(url))
                    self.scraped_dict["new_cdn_id"].append("")
                else:
                    self.scraped_dict["new_cdn_id"].append(cdn_id.group(1))

    # def get_href(self, results_list):
    #     for result in results_list:
    #         self.scraped_dict["href"].append(result['href'])

    # def get_tumbnail(self, results_list):
    #     for result in results_list:
    #         thumbnail = result.find('div', {'class': 'col search_capsule'}).find("img")["src"]
    #         self.scraped_dict["thumbnail"].append(thumbnail)
