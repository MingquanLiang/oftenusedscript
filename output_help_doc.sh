#!/bin/bash

check_module=$1
if [ $# == 1 ]
then
    output_filename="${check_module}_help.txt"
elif [ $# == 2 ]
then
    output_filename=$2
else
    echo "Usage: $0 module_name [output_filename]"
    exit 1
fi

if [[ ${check_module} =~ '.' ]]
then
    module_name=$(echo "${check_module}" | awk -F'.' '{print $1}')
else
    module_name=${check_module}
fi

python -c "import ${module_name}"
ret=$?
if [ "$ret" == "0" ]
then
    python -c "import ${module_name}; help(${check_module})" > ${output_filename}
    echo "The help doc of module ${check_module} is ${output_filename}"
else
    echo "Failed to output the help doc of ${module_name}"
    exit 1
fi
exit 0
