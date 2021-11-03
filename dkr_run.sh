#!/bin/bash

docker run -it \
  -v /home/mgeiger/new_tifs/:/build/ \
  -v /fsdata1:/fsdata1 \
  gdal:2.4.2 /build/new_tifs.py
  
