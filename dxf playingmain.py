import ezdxf
from collections import namedtuple
import os
import re
from icecream import ic
from ezdxf.enums import TextEntityAlignment
import numpy
from ezdxf.entities import Line

HEADER_NOTCH_FLAG_NAME="$HYPERLINKBASE"
HEADER_NOTCH_FLAG="TRANSFORMED"
NOTCH_LAYER_TO_IGNORE="NOTCH1"
MIN_NOTCH_SIZE=0.198
MAX_NOTCH_SIZE=0.21

def process_entity(entity,doc):
    
    if entity.dxftype() == 'TEXT':
        print(f"Text: {entity.dxf.text}, Position: {entity.dxf.insert}")
        lableLines=(re.findall(r"(\d)\:(.*?)(?=\d\:|$)",entity.dxf.text))
        lableLines.sort(key=lambda x:x[0])  
        
        for l in lableLines:
            newline=entity.new()
            newline.dxf.text=l[1]

        return(entity.dxf.text)

def GetMarkerInfo(DXFpath:os):
    '''returns a named tuple with width length and number of pieces in a DXF marker file given the path of the file'''
    
    doc = ezdxf.readfile(DXFpath)
    header_vars = doc.header
    msp = doc.modelspace() #some kind of iterator with all the entities in it

    ic(header_vars.get(HEADER_NOTCH_FLAG_NAME))
    #for layer in doc.layers:
        #print(f"Layer Name: {layer.dxf.name}")
        #print(f"Layer Name: {layer.dxf.XDATA}")

    # Iterate through all entities in the modelspace or pieces on the marker
    for entity in msp:

        print(entity.dxf.name)
        # entity is an insert type some kind of reference or container the represents a piece 
        labels=doc.blocks.get(entity.dxf.name)
        
        for label in labels:
                ic(label.dxftype())
                print(f"layer{label.dxf.layer}")
                #print(f"layer{label.dxf.layer}")
                
                if label.dxftype() == 'TEXT':
                    print(label.dxf.insert)
                    print(label.dxf.text)
                    
                    labelList=(re.findall(r"(\d)\:(.*?)(?=\d\:|$)",label.dxf.text))
                    if labelList:
                        labels.delete_entity(label)
        
                    labelList.sort(key=lambda x:x[0])  
                    
                    for l in labelList:
                        Ypos=30+10*int(l[0])
                        labels.add_text(l[1]).set_placement((20, Ypos))
                
                elif label.dxftype()=='LINE' :

                    start=label.dxf.start
                    end=label.dxf.end
                    diff=numpy.array(start)-numpy.array(end)
                    has_notch=False
                    diff=abs(diff)
                    notchLen=numpy.hypot(diff[0],diff[2])
                    ic(notchLen)
                    #diff.sort()
                    # sorting 
                    #if notchLen>MIN_NOTCH_SIZE and notchLen<MAX_NOTCH_SIZE and label.dxf.layer!=NOTCH_LAYER_TO_IGNORE:
                    #    label.dxf.end=start
                    #    label.dxf.start=end
                    #    ic("changed",start,label.dxf.start)
                    #    has_notch=True
        
                
    # Add string to header to prevent overwrite. 
    header_vars[HEADER_NOTCH_FLAG_NAME]=HEADER_NOTCH_FLAG
    
    doc.saveas(DXFpath)

    return()

GetMarkerInfo(r"C:\AutometrixTools\5.dxf")
