#! /bin/bash

# Remove trailing slashes
dir_to_zip=$(echo $1 | sed -e 's/\/$//g')

file_ext=tif

for f in $(ls $dir_to_zip)
do
  base_f=${f%%.$file_ext}
  zip $dir_to_zip/$base_f.zip $dir_to_zip/$f
done
