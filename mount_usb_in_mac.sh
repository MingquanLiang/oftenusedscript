#!/bin/bash

if [ "$(whoami)" != "root" ]
then
    echo "Please Run as root"
    exit 1
fi

if [ $# != 1 ]
then
    echo "Usage: $0 Volumn_Name. eg $0 /Volumes/CentOS_6.6"
    exit 1
fi

target_dir="/Volumes/My_Mount_NTFS"

echo "mount the ntfs filesystem to ${target_dir} ... "
device_node=`diskutil info $1 | grep "Device Node" | awk '{print $NF}'`
sudo umount $1
sudo mount_ntfs -o rw,nobrowse ${device_node} ${target_dir}
ret=$?
if [ "$ret" == "0" ]
then
    echo "Done"
else
    echo "Failed"
fi
exit $ret
