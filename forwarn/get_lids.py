#!/usr/bin/env python

'''A little script that extracts layer ids from an FCAV config file (ews_config.xml)
'''

import xml.etree.ElementTree as ET

config_file = './ews_config.xml'

tree = ET.parse('ews_config.xml')

theme_elems = tree.find('mapviews').findall('view')

themes = [] 

for theme_elem in theme_elems:
  theme = { 'label': theme_elem.get('label') }
  theme['viewGroups'] = [ e.get('name') for e in theme_elem.findall('viewGroup') ]
  themes.append(theme)

wms_layers = tree.find('wmsLayers')

wms_groups = wms_layers.findall('wmsGroup')


def get_themes_using_wms_group(wms_group, themes):
  themes_with_group = []
  for theme in themes:
    if wms_group.get('name') in theme['viewGroups']:
      themes_with_group.append(theme['label'])
  return themes_with_group
   

with open('data.csv', 'w') as f:
  for wms_group in wms_groups:
    themes_using_group = get_themes_using_wms_group(wms_group, themes)
    f.write('\n\n')
    f.write("ACCORDIAN GROUP: {}\n\n".format(wms_group.get('label')))
    f.write("USED IN THEMES:\n{}\n\n".format("\n".join(themes_using_group)))
    for wms_subgroup in wms_group.findall('wmsSubgroup'):
      f.write("\n\nSUBGROUP: {}\n\n".format(wms_subgroup.get('label').encode('utf-8')))
      f.write("LAYER NAME,LID\n")
      for layer in wms_subgroup.findall('wmsLayer'):
        name = layer.get('name').encode('utf-8')
        lid = layer.get('lid').encode('utf-8')
        f.write("{},{}\n".format(name, lid))
        
