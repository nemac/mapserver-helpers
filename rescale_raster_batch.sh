#!/bin/bash

# Remove trailing slashes
DIR=$(echo $1 | sed -e 's/\/$//g')

for tif in $(ls $DIR/*.tif)
do
  echo "Rescaling $tif."
  ./rescale_raster.py -f $tif
  echo "Finished rescaling $tif."
done

