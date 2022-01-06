#!/usr/bin/env python

'''A script that translates an FCAV config file (ews_config.xml) from XML to json.'''

import xml.etree.ElementTree as ET
import json

tree = ET.parse('ews_config.xml')
root = tree.getroot()
layers = root.find('wmsLayers')
groups = layers.findall('wmsGroup')

layer_types = { 'wmsLayer': 'WMS', 'wmtsLayer': 'WMTS', 'restLayer': 'REST', 'xyzLayer': 'XYZ' }


def get_layer(layer, layer_type):
  d = {}
  for k, v in layer.items():
    d[k] = v
  d['type'] = layer_types[layer_type]
  return d


def get_layers_of_type(subgroup, type_tag):
  layers = subgroup.findall(type_tag)
  if layers:
    return [ get_layer(e, type_tag) for e in layers ]
  else:
    return []


def get_subgroup_layers(subgroup):
  all_layers = []
  for type_tag in layer_types:
    all_layers.extend(get_layers_of_type(subgroup, type_tag))
  return all_layers


def get_subgroup(subgroup):
  return {
    subgroup.get('label') : {
      #restLayer, wmtsLayer
      'layers': get_subgroup_layers(subgroup)
    }
  }


d = {
  g.get('gid') : {
    'name': g.get('name'),
    'label': g.get('label'),
    'subgroups': [ get_subgroup(e) for e in g.findall('wmsSubgroup') ]
  }
  for g in groups
}

_json = json.dumps(d, indent=2)
with open('fcav_config.json', 'w') as f:
  f.write(_json)
