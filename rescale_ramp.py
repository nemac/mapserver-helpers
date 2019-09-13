#!/usr/bin/env python

"""Rescale a color ramp file.

This script takes a metadata file (the output of `rio info -v`) and
rescales a .clr type color ramp file. Only the first band of a raster
is considered when determining the min and max. You an also explicitly
set the min and max values of the original ramp instead of providing
a metadata file.
"""

import argparse, json, os, sys
import rasterio as rio


def setup_arg_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--filename', help='Color ramp file to rescale.')
  parser.add_argument('-mf', '--metadata_file', help='Metadata file to read stats from (output of rio info -v).')
  parser.add_argument('-o', '--out_file', help='Output color ramp file.')
  parser.add_argument('--in_min', help='Min value to use for original scale.')
  parser.add_argument('--in_max', help='Max value to use for original scale.')
  parser.add_argument('--out_min', default=0, help='Min value to use for rescaled color ramp.')
  parser.add_argument('--out_max', default=254, help='Max value to use for rescaled color ramp.')
  return parser


def is_valid_args(args):
  is_valid = True
  not_enough_args = not (args.metadata_file or (args.in_min and args.in_max))
  too_many_args = args.metadata_file and (args.in_min or args.in_max)
  if not_enough_args or too_many_args:
    print('Error: no metadata file or min/max values provided.')
    is_valid = False
  if not args.out_file:
    print('Error: no output path provided.')
    is_valid = False
  # min/max values for original color ramp should be numbers
  if not args.metadata_file and (args.in_min and args.in_max):
    try:
      float(args.in_min)
      float(args.in_max)
    except ValueError:
      print('Error: min and max values must be numbers.')
      is_valid = False
  return is_valid


def get_raster_min_max(metadata_file, in_min, in_max):
  if (metadata_file):
    with open(metadata_file) as f:
      file_contents = f.read()
      metadata = json.loads(file_contents)
      stats = metadata['stats']
      return stats[0]['min'], stats[0]['max']
  else:
    return float(in_min), float(in_max)


def is_number(x):
  try:
    float(x)
    return True
  except:
    return False


def process_line(line, in_min, in_max, out_min, out_max):
  in_range = float(abs(in_max - in_min))
  out_range = float(abs(out_max - out_min))
  pieces = line.split(',')
  val = float(pieces[0])
  new_val = out_range*((val-in_min)/in_range)
  pieces[0] = str(int(new_val))
  return ','.join(pieces)



# This is not working as expected
def strip_duplicates(lines):
  new_lines = []
  for line in lines:
    if line.strip(',')[0] not in [ line.strip(',')[0] for line in new_lines ]:
      new_lines.append(line)
  return new_lines


def rescale_ramp(in_file, out_file, in_min, in_max, out_min, out_max):
  with open(in_file) as f:
    # Remove any comment lines by QGIS
    lines = [ line.rstrip() for line in f.readlines() if is_number(line.split(',')[0]) ]
    new_lines = [ process_line(line, in_min, in_max, out_min, out_max) for line in lines ]
    #new_lines = strip_duplicates(new_lines)
    with open(out_file, 'w') as f_out:
      f_out.write('\n'.join(new_lines))


def main():
  parser = setup_arg_parser()
  args = parser.parse_args()
  if not is_valid_args(args):
    sys.exit()
  min, max = get_raster_min_max(args.metadata_file, args.in_min, args.in_max)
  rescale_ramp(args.filename, args.out_file, min, max, args.out_min, args.out_max)


if __name__ == '__main__':
  main()

