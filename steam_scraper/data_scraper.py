import collections
from my_utils.my_logging import log_message as log
from my_utils.consts import ints_str_list as ints_str


class Data_Scraper:
    # todo make it more elegant by using map rather than having a for loop in each method
    # every methode in this class will be applied to the the results
    # they all must take the list of results as an argument and add a list to the dict in this object and have no return
    # a list in which each result lines up with a result from the argument
    # like this ["review_scores": [list of review scores]]
    scraped_dict = collections.defaultdict(list)
    curr_symbol = None# this is super inelegant
    curr_symbol_list = "¥$€£"

    def get_user_reviews(self, results):
        # returns 2 lists
        # the first list is how many user reviews the result got
        # the second list is what percentage was positive
        n_user_reviews = []
        percent_reviews_positive = []
        found = 0
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
        log('scraping discount percents')
        discount_percents = []
        for r in results_list:
            string = str(r.find("div", {"class": "col search_discount responsive_secondrow"}))
            span = "<span>"
            # for some fucking reason not all results have a discount number
            if string.find(span) != -1:
                # the +1 and -1 are to cut off the - and the %
                start = string.find(span) + len(span) + 1
                end = string.find("</span>") - 1
                discount_percents.append(int(string[start:end]))
            else:
                discount_percents.append(0)
        for item in discount_percents:
            self.scraped_dict["discount_percents"].append(item)

    def get_titles_list(self, results_list):
        log("scraping title")
        for result in results_list:
            self.scraped_dict["titles"].append(
                str(result.find("span", {"class": "title"}).string))

    def get_old_and_new_price(self, results_list):
        log('scraping the old+new price')

        for result in results_list:
            if result.find('div', {'class': 'col search_price discounted responsive_secondrow'}) is not None:
                price_str = str(result.find('div', {'class': 'col search_price discounted responsive_secondrow'}).text)
                price_str = price_str.replace('\t', '')
                price_str = price_str.replace("Free", "")# sloppy fix to a bug
                price_str = price_str.replace('\n', '')# there is apperently a return at the start of the string
                price_str = price_str.replace(',', '.')
                price_str = price_str.replace('--', '0')# if a price has no decimal places it apperently adds --

                if self.curr_symbol is None:
                    for sym in self.curr_symbol_list:
                        if sym in price_str:
                            self.curr_symbol = sym
                            break

                old_new_strs = price_str.split(self.curr_symbol)
                if old_new_strs[0] == "":# first or last item is empty
                    old_new_strs = old_new_strs[1:]
                else:
                    old_new_strs = old_new_strs[:2]

                self.scraped_dict["old_price"].append(float(old_new_strs[0]))
                if len(old_new_strs) > 1:
                    self.scraped_dict["new_price"].append(float(old_new_strs[1]))
                else:
                    self.scraped_dict["new_price"].append(float(0))
            else:
                self.scraped_dict["old_price"].append(float(0))
                self.scraped_dict["new_price"].append(float(0))

    def get_app_id(self, results_list):
        # THE APP ID(S) ARE STRORED AS STRINGS FOR NOW since i don't need them as ints right now.
        # nor can i think of a reason why i should want that.
        log("scraping appids")
        for result in results_list:
            try:
                if(',' in result['data-ds-appid']):# if it has multible appids which is when it's an old style bundle
                    self.scraped_dict["appids"].append(
                        result['data-ds-packageid'])
                    self.scraped_dict["is_bundle"].append(True)
                    self.scraped_dict["is_old_bundle"].append(True)
                else:
                    self.scraped_dict["appids"].append(
                        result['data-ds-appid'])
                    self.scraped_dict["is_bundle"].append(False)
                    self.scraped_dict["is_old_bundle"].append(False)
            except KeyError:
                self.scraped_dict["appids"].append(
                    result['data-ds-bundleid'])
                self.scraped_dict["is_bundle"].append(True)
                self.scraped_dict["is_old_bundle"].append(False)

    # def get_href(self, results_list):
    #     for result in results_list:
    #         self.scraped_dict["href"].append(result['href'])

    # def get_tumbnail(self, results_list):
    #     for result in results_list:
    #         thumbnail = result.find('div', {'class': 'col search_capsule'}).find("img")["src"]
    #         self.scraped_dict["thumbnail"].append(thumbnail)

