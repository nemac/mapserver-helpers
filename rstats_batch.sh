#!/bin/bash

# Remove trailing slashes
rasters_dir=$(echo $1 | sed -e 's/\/$//g')
out_dir=$(echo $2 | sed -e 's/\/$//g')

for file_path in $(ls $rasters_dir/*.tif)
do
  tif=$(basename $file_path)
  meta_file=$tif.meta.json
  echo "Outputting metadata for $(basename $tif) to $out_dir/$meta_file..."
  rio info -v $file_path > $out_dir/$meta_file
done

