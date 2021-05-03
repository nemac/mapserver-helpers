#!/usr/bin/env python3

'''
Convert a GeoTiff file to a Cloud-Optimized GeoTiff.

https://trac.osgeo.org/gdal/wiki/CloudOptimizedGeoTIFF

Assumes gdal tools (gdal_translate, gdalbuildvrt) are in PATH.

Use the --help option for more information:

python convert_to_cogeo.py --help

'''

import sys, os, os.path, argparse, subprocess, json

def convert_to_cogeotiff(of, ot, r, a_nodata, tmpdir, blocksize, convert_nodata, copy_overviews, src_dataset, scale):
  
  path_pair = os.path.split(src_dataset)
  filename_with_ext = path_pair[1]
  tmpdir = path_pair[0] if tmpdir is None else tmpdir

  gdal_translate = ['gdal_translate',
    '-stats',
    '-ot {0}'.format(ot),
    '-of {0}'.format(of),
    '-r  {0}'.format(r),
    '-co COMPRESS=LZW',
    '-co TILED=YES',
    '-co BLOCKXSIZE={0}'.format(str(blocksize)),
    '-co BLOCKYSIZE={0}'.format(str(blocksize)),
    '-co COPY_SRC_OVERVIEWS={}'.format('YES' if copy_overviews else 'NO'),
    '--config GDAL_TIFF_OVR_BLOCKSIZE {0}'.format(str(blocksize))
  ]

  if a_nodata:
    gdal_translate.append('-a_nodata {0}'.format(a_nodata))

    # Use an intermediate vrt file to convert nodata pixel values
    if convert_nodata:
      vrtpath = os.path.join(tmpdir, filename_with_ext) + '.vrt'
      gdalbuildvrt = ['gdalbuildvrt']
      gdalbuildvrt.append('-vrtnodata {0}'.format(a_nodata))
      gdalbuildvrt.append('"{0}" "{1}"'.format(vrtpath, src_dataset))
      gdalbuildvrt_command = ' '.join(gdalbuildvrt)
      print(gdalbuildvrt_command)
      try:
        os.system(gdalbuildvrt_command)
      except:
        print("Something went wrong when building the intermediate vrt file!")
        sys.exit(1)
    else:
      vrtpath = ''

  if scale:
    rio_info = ['rio', 'info', '-v', filename_with_ext]
    print(' '.join(rio_info))
    rio_info_results = subprocess.run(rio_info, stdout=subprocess.PIPE)
    stdout = rio_info_results.stdout.decode('utf-8')
    metadata = json.loads(stdout)
    scale_args = [
      '-scale_{0} {1} {2} 0 254'.format(i+1, b['min'], b['max'])
      for i,b in enumerate(metadata['stats'])
    ]
    gdal_translate.extend(scale_args)

  dst_dataset = '{0}_NEW'.format(src_dataset)
  gdal_translate.append('"{0}"'.format(src_dataset if not vrtpath else vrtpath))
  gdal_translate.append('"{0}"'.format(dst_dataset))
  
  gdal_translate_command = ' '.join(gdal_translate)
  print(gdal_translate_command)
  try:
    os.system(gdal_translate_command)
  except:
    print("Something went wrong while trying to run gdal_translate!")
    sys.exit(1)

  # Overviews
  gdaladdo = ['gdaladdo',
    '--config', 'COMPRESS_OVERVIEW', 'DEFLATE',
    '--config', 'PREDICTOR_OVERVIEW', '2',
    '--config', 'INTERLEAVE_OVERVIEW', 'PIXEL',
    dst_dataset,
    '2', '4', '8', '16' 
  ]

  # Cleanup
  try:
    os.remove(vrtpath)
  except:
    pass

  try:
    os.rename(src_dataset, '{}.old'.format(src_dataset))
    os.rename(dst_dataset, src_dataset)
    print('Done!')
  except:
    print("Error while attempting to rename intermediate translated dataset!")
    sys.exit(1)


def setup_arg_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-of', '--output_format',
    default='GTiff',
    help='Output format (a gdal driver).'
  )
  parser.add_argument('-ot', '--output_type',
    default='Byte',
    help='Output data type'
  )
  parser.add_argument('-r',  '--resample',
    default='average',
    help='Resampling algorithm to use.'
  )
  parser.add_argument('-nd', '-a_nodata', '--nodata',
    default=255,
    help='Override nodata value with this value'
  )
  parser.add_argument('--tmpdir',
    help='Directory in which to store temporary files.'
  )
  parser.add_argument('-bs', '--blocksize', '-blocksize',
    default=256,
    help='Blocksize to use for new dataset.'
  )
  parser.add_argument('-cn', '--convert_nodata',
    action='store_true',
    help='Use a VRT trick to convert the value of nodata from src_dataset to the nodata value given to this script with the -nd argument.'
  )
  parser.add_argument('--copy_overviews',
    action='store_true',
    help='Copy the source dataset overviews.'
  )
  parser.add_argument('src_dataset')
  parser.add_argument('--scale',
    action='store_true',
  )
  return parser


if __name__ == '__main__':
  parser = setup_arg_parser()
  args = parser.parse_args()
  print(args)
  convert_to_cogeotiff(
    args.output_format,
    args.output_type,
    args.resample,
    args.nodata,
    args.tmpdir,
    args.blocksize,
    args.convert_nodata, 
    args.copy_overviews, 
    args.src_dataset,
    args.scale
  )

