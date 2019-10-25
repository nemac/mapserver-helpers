#!/bin/bash

# Remove trailing slashes
clr_dir=$(echo $1 | sed -e 's/\/$//g')
cmap_dir=$(echo $2 | sed -e 's/\/$//g')

for file_path in $(ls $clr_dir/*.txt)
do
  clr=$(basename $file_path)
  cmap=${clr%%.txt}.cmap
  ./clr2mapserver.py $file_path $cmap_dir/$cmap
done

