#!/bin/bash

module_name=$1
if [ $# == 1 ]
then
    output_filename="${module_name}_help.txt"
elif [ $# == 2 ]
then
    output_filename=$2
else
    echo "Usage: $0 module_name [output_filename]"
    exit 1
fi
python -c "import ${module_name}"
ret=$?
if [ "$ret" == "0" ]
then
    python -c "import ${module_name}; help($module_name)" > ${output_filename}
    echo "The help doc of module $module_name is $output_filename"
else
    echo "Failed to output the help doc of ${module_name}"
    exit 1
fi
exit 0
