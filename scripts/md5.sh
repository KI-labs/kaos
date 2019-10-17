#!/bin/bash
set -e

function check_deps() {
  test -f $(which md5) || error_exit "md5 command not detected in path, please install it"
  test -f $(which jq) || error_exit "jq command not detected in path, please install it"
}

timestamp() {
  date +"%s"
}
path=$(jq -r '.path')
md5=$( find "$path" -type f -exec md5 -r {} ";" | md5 -r | cut -d' ' -f1 )

printf "{\\\"md5\\\":\\\"$md5\\\"}"