# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 17:11:59 2017

@author: ypaparna
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script helps to audit different k values for the element "tag"
import xml.etree.cElementTree as ET


def process_map(filename):

    tags = set()
      
   
    for _, element in ET.iterparse(filename):
         if element.tag == "tag":
            text= element.attrib.get('k')         
            tags.add(text)
     
    
    
    print(tags)
    return 

if __name__ == "__main__":
     process_map("sammamish.osm") 