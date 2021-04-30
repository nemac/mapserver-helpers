#!/usr/bin/env python

import argparse, os

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Convert a batch of tiffs that exist in a local folder.')
  parser.add_argument('folder', help='Folder where your tiffs are.')
  parser.add_argument('--ext', help='Filter by file extension. Default is \'.tif\'.')
  args = parser.parse_args()
  folder = args.folder
  ext = args.ext or '.tif'
  files = [ f for f in os.listdir(folder) if f.endswith(ext) ]
  for f in files:
    path = os.path.join(folder, f)
    os.system('./cogeotiff.py --convert_nodata {}'.format(path))
