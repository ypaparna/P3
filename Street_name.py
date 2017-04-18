
# coding: utf-8

# In[17]:


"""
Created on Fri Apr 14 17:04:05 2017

@author: ypaparna
"""

""""
This program is created to audit street names and update over abbreviated street names for consistency.

"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sammamish.osm"
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

# Audit type of street names. If it is not in the expected set, add it to the list of street names 
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# Is this element a street name?
def is_street_name(elem):
    return (elem.attrib['k'] == "name")

# Audit and select only "node" and "way" tags to explore child elements
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

#Update over abbreviated street names using the mapping 
def update_name(name, mapping):
    words = name.split() 
    for i in range(len(words)):
        if words[i] in mapping:
            words[i] = mapping[words[i]]
        name = " ".join(words)
    return name



def test():
    st_types = audit(OSMFILE)

    for st_type, ways in st_types.iteritems():
        for name in ways:   
            old_name = name
            better_name = update_name(name, mapping)
            if old_name != better_name:
                print old_name, "=>", better_name
            
            
     
           
if __name__ == '__main__':
    test()


# In[ ]:



