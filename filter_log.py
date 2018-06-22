import re
from functools import reduce

import os

from my_utils.platform_vars import ROOTDIR, dir_sep

with open(ROOTDIR + dir_sep + "log.log.txt", "r") as file:
    lines = file.read().split("\n")

new_log = reduce(lambda acc, line: acc + "\n" + line,
                 filter(lambda line: re.match(re.compile("Warning:"), line) is None,
                        filter(lambda line: re.match(re.compile("Message:"), line) is None, lines))
                 )

new_log = os.linesep.join([s for s in new_log.splitlines() if s])

with open(ROOTDIR + dir_sep + "filter_log.txt", "w") as file:
    file.write(new_log)
