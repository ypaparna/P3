
# coding: utf-8

# In[5]:

#!/usr/bin/env python

# this file audits and updates zip codes
import xml.etree.cElementTree as ET
import pprint
import re



def process_map(filename):

    original_codes = set()
    better_codes = set ()
    
   
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            text= element.attrib.get('k') 
           
            
            if text == 'postal_code' or text == 'addr:postcode' :
                zip = element.attrib.get('v')
                original_codes.add(zip)
                better_zip = update_zipcode(zip)
                better_codes.add(better_zip)
            
    print "Audit zipcodes"          
    print original_codes
    print "\n"
    print "corrected zip codes"
    print better_codes
    return 

# update zipcode to remove any alphabets and takes the first 5 digits in the zipcode
def update_zipcode(zip):
    code = re.sub("\D", "", zip)[:5]
    
    return code
    

if __name__ == "__main__":
     process_map("sammamish.osm")


# In[ ]:



