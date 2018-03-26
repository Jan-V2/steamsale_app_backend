#!/usr/bin/env bash

rm -rf my_utils
git clone https://github.com/johnvanderholt/utils.git utils
mv ./utils/my_utils/ ./
rm -rf utils/
git add ./my_utils/*