
# coding: utf-8

# In[4]:

#!/usr/bin/env python

# This script will audit various cuisine names and updates them for consistency
import xml.etree.cElementTree as ET
import pprint
import re
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
def update_cuisine_name(name, cuisine_mapping):
    old_name = name
    for abbr, exp in cuisine_mapping.iteritems():
        name = name.replace(abbr, exp) 
    return name

def process_map(filename):

    original_cuisine = set()
    updated_cuisine = set()
    
   
    for _, element in ET.iterparse(filename):
         if element.tag == "tag":
            text= element.attrib.get('k') 
           
            if text == 'cuisine':   
                cuisine = element.attrib.get('v')
                original_cuisine.add(cuisine)
                # Fix cuisine name if needed
                better_name = update_cuisine_name(cuisine,cuisine_mapping)
                updated_cuisine.add(better_name)
               
                     
    print "Original Cuisine names"
    print original_cuisine
    print "\n"
    print "Updated cuisine names"
    print updated_cuisine
    return 

if __name__ == "__main__":
     process_map("sammamish.osm")


# In[ ]:



