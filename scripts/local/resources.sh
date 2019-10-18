#!/usr/bin/env bash
set -e

check_deps () {
  test -f $(which numfmt) || error_exit "numfmt command not detected in path, please install it"
}

function remove_trailing_quotes() {
    temp=$1
    temp=${temp%\"}
    echo "${temp#\"}"
}

function add_array_to_json() {
    array=$1
    array_name=$2
    end=$3

    ma+="\\\"${array_name}\\\": \\\""

    len=${#array[*]}
    leni=len-1
    for (( i = 0; i < len; ++i));
    do
        if [[ i -lt leni ]]; then
            ma+="${array[i]} "
        else
            ma+="${array[i]}\\\""
        fi
    done
    ma+=${end}
    echo "$ma"
}

nodes=$(kubectl get nodes | egrep -v NAME | awk '{print $1}')

declare cpus
declare gpus
declare memories

i=0
for node in ${nodes}
do
    allocatable=$(kubectl get node ${node} -o=json | jq '.status.allocatable')
    capacity=$(kubectl get node ${node} -o=json | jq '.status.capacity')

    cpu=$(remove_trailing_quotes $(echo ${allocatable} | jq '.cpu // "0"' ))
    memory=$(remove_trailing_quotes $(echo ${allocatable} | jq '.memory // "0Ki"'))
    gpu=$(remove_trailing_quotes $(echo ${capacity} | jq '."nvidia.com/gpu" // "0"'))
    memory=$(numfmt ${memory} --from=iec-i --to=iec-i --to-unit=G)


    cpus[i]=${cpu}
    gpus[i]=${gpu}
    memories[i]=${memory}
    i=${i}+1

done

res="{ "
res+=$(add_array_to_json ${cpus} "cpu" ",")
res+=$(add_array_to_json ${memories} "memory" ",")
res+=$(add_array_to_json ${gpus} "gpu" "")
res+=" }"

printf "${res}"
