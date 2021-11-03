#!/usr/bin/env python3

'''
Recursively walk a directory and do the following:

- Remove .tfw and .wkt files
- Use gdal_calc.py to run an identity function (A*1) on each .img or .tif file.
  This has the effect of removing built-in attribute tables and creating a
  "fresh" file to work with. Sometimes this takes an extremely long time.
- Reproject to Web Mercator (EPSG:3857) and rename to [filename].EPSG3857.tif
- Run cogeotiff.py (turn it into a cloud-optimized geotiff)
'''

import os.path
import os, sys

# DOCKER VOLUME MOUNTS
cogeotiff = '/build/cogeotiff.py --convert_nodata'

BASE_DIR = '/fsdata1/fsdata-internal/efetac_nasa/AncillaryData/duration_new/'

os.chdir(BASE_DIR)

def convert(folder, filename):
  path = os.path.join(BASE_DIR, folder, filename)
  if path.endswith('.wkt') or path.endswith('.tfw') or path.endswith('.aux.xml'):
    print("Removing extra file {}".format(path))
    os.remove(path)
    return

  if not (path.endswith('.img') or path.endswith('.tif')):
    return

  os.system(f"{cogeotiff} {path}")

  tif_filename = os.path.splitext(filename)[0] + '.tif'

  if tif_filename != filename:
    os.remove(path)
    path = os.path.join(BASE_DIR, folder, tif_filename)

  filename_calc = os.path.splitext(filename)[0] + '.calc.tif'
  path_calc = os.path.join(folder, filename_calc)

  print("Removing color table...")
  os.system('gdal_calc.py -A {} --outfile={} --calc="A*1" --co="COMPRESS=LZW"'.format(path, path_calc))

  print("Deleting original file...")
  os.remove(path)
  print("Renaming calc file...")
  os.rename(path_calc, os.path.join(folder, filename_calc.replace('.calc', '')))

  print("Reprojecting to Web Mercator (EPSG:3857)...")
  warped_path = os.path.splitext(path)[0] + '.EPSG3857.tif'
  gdalwarp_cmd = f"gdalwarp -overwrite -r average -t_srs 'EPSG:3857' -co 'COMPRESS=LZW' -co 'TILED=YES' {path} {warped_path}"
  os.system(gdalwarp_cmd)

  print("Optimizing new tif...")
  os.system(f"{cogeotiff} {warped_path}")


for root, dirs, files, rootfd in os.fwalk(BASE_DIR):
  for d in dirs:
    print(d)
    for f in os.listdir(d):
      convert(d, f)

