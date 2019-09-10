#!/usr/bin/env python

import argparse

def render_name_block(name):
  template = """
    CLASS
      NAME "{0}"
      EXPRESSION " "
      STYLE
        COLOR 255 255 255
      END
    END
  """

def render_range_block(low_pixel_value, high_pixel_value, rgb_string, inclusive_lower=True, inclusive_upper=False):
  include_upper_text = "=" if inclusive_upper else ""
  include_lower_text = "=" if inclusive_lower else ""
  template = """
  CLASS
    NAME "{0} - {1}"
    EXPRESSION ([PIXEL] >{3} {0} AND [PIXEL] <{4} {1})
    STYLE
      COLOR {2}
    END
  END
  """
  return template.format(low_pixel_value, high_pixel_value, rgb_string, include_lower_text, include_upper_text)


def render_simple_block(pixel_value, rgb_string, greater_than=False, less_than=False):
  if less_than and greater_than:
    raise ValueError("Unable to render simple block: less_than and greater_than flags are both True!")
  if less_than:
    inequality_text = "<"
  elif greater_than:
    inequality_text = ">"
  else:
    inequality_text = ""
  template = """
  CLASS
    EXPRESSION ([PIXEL] {2}= {0})
    STYLE
      COLOR {1}
    END
  END
  """
  return template.format(pixel_value, rgb_string, inequality_text)


def render_mapserver_colormap(colormaps, is_exact):
  if is_exact:
    return "".join([ render_simple_block(cmap[0], cmap[1]) for cmap in colormaps ])
  else:
    cmap_blocks = []
    # Skip the last block since it'll be slightly different
    for i in range(0, len(colormaps)-1):
      low_pixel_value = colormaps[i][0]
      high_pixel_value = colormaps[i+1][0]
      rgb_string = colormaps[i][1]
      cmap_blocks.append(render_range_block(low_pixel_value, high_pixel_value, rgb_string))
    # The last color map block is [PIXEL] = value
    cmap_blocks.append(render_simple_block(colormaps[-1][0], colormaps[-1][1]))
    return "".join(cmap_blocks)


def get_colormaps_from_clrfile(path):
  with open(path) as clrfile:
    colormaps = []
    for line in clrfile:
      # Strip the newline character and chop off the last two values
      # We're left with a list of the form [ PIXEL_VALUE, R, G, B ]
      line = line.strip().split(',')[:-2]
      pixel_value = line[0]
      rgb_value = ' '.join(line[1:])
      colormaps.append((pixel_value, rgb_value))
    return colormaps


def setup_arg_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--exact', action='store_true', help="Do not set colors for ranges of values. Map the colors for exact pixel values only, without setting colors for pixel values in between values in the clr file.")
  parser.add_argument('clrpath', help="Path to the .clr file to transform.")
  parser.add_argument('cmap_out', help="Name of the file to output to.")
  return parser


def main():
  parser = setup_arg_parser()
  args = parser.parse_args()
  colormaps = get_colormaps_from_clrfile(args.clrpath)
  full_colormap_string = render_mapserver_colormap(colormaps, args.exact)
  try:
    with open(args.cmap_out, 'w') as f:
      f.write(full_colormap_string)
  except Exception as e:
    print(e)
    print("Error writing to file!")


if __name__ == '__main__':
  main()



