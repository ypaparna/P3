
# coding: utf-8

# In[ ]:

#!/usr/bin/env python


"""
This code will fix the problems identified during auditing(street names, zipcode, cuisine)and will write the records
into 5 different CSV files. 
Record structure in each CSV file is shown below
### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
child tags of node which have the tag name/type: "tag". Each dictionary should have the following
fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.



### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
-  user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules as
for "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element


"""

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "sammamish.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]


# This is the street name mapping
mapping = { "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "St" : "Street",
            "ST" :  "Street",
            "Ave": "Avenue",
            "Rd" : "Road",
            "S.E." : "SE",
            "Pl"  : "Place",
            "PL"  : "Place",
            "Ct"  : "Court",
            "CT"  : "Court",
            "Dr"  : "Drive",
            "Dr."  : "Drive"
            }

cuisine_mapping = { "Mexican": "mexican",
                    "English": "english",
                    "Taiwanese": "taiwanese",
                    "taiwan":  "taiwanese",
                    "Vegan":  "vegan",
                    "chineese": "chinese",
                    "chicken;mexican": "mexican",
                    "noodles;asian":  "asian",
                    "pancake;breakfast": "breakfast",
                    "donut;coffee_shop": "coffee_shop"              
                      }

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

##This function will read the xml file and shape the data to be loaded into csv files
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for field in node_attr_fields:
            node_attribs[field] = element.attrib[field]
    
        for child in element:
                if child.tag == 'tag':
                    node_tags ={}
                    text = child.attrib["k"]
                    n = LOWER_COLON.match(text)
                    o = PROBLEMCHARS.match(text)
                    if o:
                        pass
                    if n:
                        node_tags["key"] = text.split(':', 1)[1]
                        node_tags["type"] = text.split(':',1)[0]
                    else:
                        node_tags["key"] = child.attrib["k"]
                        node_tags["type"] = "regular"
                    node_tags["id"] = node_attribs["id"]
                    
                    if is_street_name(child):                        
                        node_tags["value"] = update_name(child.attrib["v"], mapping)
                    #### remove any alphabets and take first five digits of zipcode
                    elif is_zip_code:
                        node_tags["value"] = re.sub("\D", "", child.attrib.get('v'))[:5]
                    ### use mapping to update cuisine names 
                    elif is_cusine:
                        node_tags["value"] = update_cuisine_name(child.attrib.get('v'),cuisine_mapping)
                    else:                                    
                        node_tags["value"] = child.attrib["v"]
                    tags.append(node_tags) 
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field] = element.attrib[field]
            nodepos =0
         
        for child in element:
                if child.tag == 'nd':
                    way_node_fields = {}
                    way_node_fields["id"] = way_attribs["id"]
                    way_node_fields["node_id"] = child.attrib["ref"]
                    way_node_fields["position"] = nodepos 
                    nodepos +=1
                    way_nodes.append(way_node_fields) 
                elif child.tag == 'tag':
                    way_tags ={}
                    text = child.attrib["k"]
                    n = LOWER_COLON.match(text)
                    o = PROBLEMCHARS.match(text)
                    if o:
                        pass
                    if n:
                        way_tags["key"] = text.split(':', 1)[1]
                        way_tags["type"] = text.split(':',1)[0]
                    else:
                        way_tags["key"] = child.attrib["k"]
                        way_tags["type"] = "regular"
                    way_tags["id"] = way_attribs["id"]
            
                    if is_street_name(child):                        
                        way_tags["value"] = update_name(child.attrib["v"], mapping)
                    #### remove any alphabets and take first five digits of zipcode
                    elif is_zip_code(child):
                        zip = child.attrib.get('v')
                        way_tags["value"] = re.sub("\D", "", child.attrib.get('v'))[:5]
                    ### use mapping to update cuisine names                      
                    elif is_cuisine(child):
                        way_tags["value"] = update_cuisine_name(child.attrib.get('v'),cuisine_mapping)
                    else:
                        
                         way_tags["value"] = child.attrib["v"]                        
                        
                    tags.append(way_tags) 
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #



def is_street_name(elem):
    return (elem.attrib['k'] == "name")

def is_zip_code(elem):
    return (elem.attrib['k'] == 'postal_code' or elem.attrib['k'] == 'addr:postcode')

def is_cuisine(elem):
    return (elem.attrib['k'] == "cuisine")

def update_name(name, mapping):
    words = name.split() 
    for i in range(len(words)):
        if words[i] in mapping:
            words[i] = mapping[words[i]]
        name = " ".join(words)
    return name


def update_cuisine_name(name, cuisine_mapping):
    for abbr, exp in cuisine_mapping.iteritems():
        name = name.replace(abbr, exp) 
    return name


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                   # print (el['way_tags'])
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)

