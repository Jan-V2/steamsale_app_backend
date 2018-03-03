from my_utils.my_logging import log_message as log

#todo figure out what a resonable filter setting
#todo make configureable from the outside

class Filter:
    # every methode in this class will be applied to the the results
    # they all must take the list of results as an argument and returns the filtered list


    minimum_discount = 40

    def get_highly_discounted(self, merged_results, keys):
        percents_index = keys["discount_percents"]
        # parameters for get_good_games
        # todo make configureable
        merged_results.sort(key=lambda p: p[percents_index], reverse=True)
        before = len(merged_results)
        for i in range(0, len(merged_results)):
            if merged_results[i][percents_index] < self.minimum_discount:
                break
        merged_results = merged_results[:i]
        log(str(len(merged_results)) + " out of " + str(before) + " had deep enough discount")
        return merged_results

    # parameters for get_good_games

    min_reviews = 10
    min_positive = 40

    def get_good_games(self, merged_results, keys):
        n_rev_idx = keys['n_user_reviews']
        min_positive_idx = keys['percent_reviews_positive']
        ret = []
        before = len(merged_results)
        for result in merged_results:
            if result[n_rev_idx] >= self.min_reviews and result[min_positive_idx] >= self.min_positive:
                ret.append(result)
        log(str(len(ret)) + " out of " + str(before) + " had good enough reviews")
        return ret

    def delete_duplicates(self, merged_results, keys):
        # i think that it adds results onto the final page until it's 25
        doubles_found = 0
        ret = []
        appid_key = keys['appids']
        is_bundle_key = keys['is_bundle']
        for line in merged_results:
            if len(ret) > 0:
                double = False
                for i in ret:
                    if i[appid_key] == line[appid_key] and i[is_bundle_key] == line[is_bundle_key]:
                        double = True
                        doubles_found += 1
                        break
                if not double:
                    ret.append(line)
            else:
                ret.append(line)
        log('removed ' + str(doubles_found) + ' doubles')
        return ret

