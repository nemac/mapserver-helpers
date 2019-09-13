#!/usr/bin/env python

import os, os.path, json, subprocess
import argparse


def setup_arg_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--filename', help='File to rescale')
  return parser


def main():
  parser = setup_arg_parser()
  args = parser.parse_args()
  filename = args.filename
  rio_info = ['rio', 'info', '-v', filename]
  print(' '.join(rio_info))
  rio_info_results = subprocess.run(rio_info, stdout=subprocess.PIPE)
  stdout = rio_info_results.stdout.decode('utf-8')
  metadata = json.loads(stdout)
  print(metadata)

  gdal_translate = ['gdal_translate',
    '-strict', 
    '-a_nodata', '255',
    '-ot', 'Byte', 
    '-of', 'GTiff', 
    '-co', 'NUM_THREADS=ALL_CPUS',
    '-co', 'TILED=YES',
    '-co', 'BLOCKXSIZE=256',
    '-co', 'BLOCKYSIZE=256',
    '-co', 'COMPRESS=DEFLATE',
    '-co', 'PREDICTOR=2'
  ]

  scale_args = [
    '-scale_{0} {1} {2} 0 254'.format(i+1, b['min'], b['max'])
    for i,b in enumerate(metadata['stats'])
  ]

  dst_filename = '{0}.byte.tif'.format(os.path.splitext(filename)[0])

  filename_args = [
    filename,
    dst_filename
  ]

  gdal_translate.extend(scale_args)
  gdal_translate.extend(filename_args)

  print(' '.join(gdal_translate))

  subprocess.run(gdal_translate)

  gdaladdo = ['gdaladdo',
    '--config', 'COMPRESS_OVERVIEW', 'DEFLATE',
    '--config', 'PREDICTOR_OVERVIEW', '2',
    '--config', 'INTERLEAVE_OVERVIEW', 'PIXEL',
    dst_filename,
    '2', '4', '8', '16' 
  ]

  print(' '.join(gdaladdo))

  subprocess.run(gdaladdo)
    
if __name__ == '__main__':
  main()

