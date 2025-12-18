import ezdxf
from collections import namedtuple
import os
import re
from icecream import ic
#from ezdxf.enums import TextpieceAlignment
import numpy
from typing import List, Dict, Tuple, Set
import csv
from copy import deepcopy
from pathlib import Path


HEADER_NOTCH_FLAG_NAME="$HYPERLINKBASE"
HEADER_NOTCH_FLAG="TRANSFORMED"
NOTCH_LAYER_TO_IGNORE="NOTCH1"
MIN_NOTCH_SIZE=0.198
MAX_NOTCH_SIZE=0.21
RECIPIE="Recipe"	
NAME="Name"	
QTY="Quantity"
N_SETS="Number_of_sets"
N_PER_SET="Pieces_Per_Set"	
ORDERID="orderId"
CUSTOMER="Customer"
PATH="Path"	
FILENAME="Filename"	
MAT="Material"	
UD1="userdefined1"	
DATE="DueDate"
FIND_DXF_LABELS=r"(\d)\:(.*?)(?=\d\:|$)"
DATAFILESUFFIX="Data.csv"
LABEL_LAYER="LABELS"
NOTCH_LAYER="NOTCH"
LABEL_SQ="1"
LABEL_SIZE_OR_SECOND="2"
LABEL_FIRST="4"
LABEL_DESC="5"
LABEL_BIN="6"
LABEL_ORDER_QTY="7"
LABEL_PART_QTY="8"
LABEL_ORDER_MULTIPLYER="9"
VALID_DXF_GEOMETRIES=("POLYLINE", "CIRCLE", "ARC", "SPLNE","LINE")


def Make_Single_Piece_dxf(file_copy:ezdxf.document.Drawing, piece_num:int):
    copy_msp=file_copy.modelspace()
    for i,p in enumerate(copy_msp):
        if not i == piece_num:
            p.destroy()
        #else:
            #ic("keeping", piece_num)
    return file_copy

def _reverse_notch(line:ezdxf.entities.Line)->bool:

    start=line.dxf.start
    end=line.dxf.end
    diff=numpy.array(start)-numpy.array(end)
    has_notch=False
    diff=abs(diff)
    notchLen=numpy.hypot(diff[0],diff[2])
    ic(notchLen)
    #diff.sort()
    # sorting 
    if notchLen>MIN_NOTCH_SIZE and notchLen<MAX_NOTCH_SIZE:
        line.dxf.end=start
        line.dxf.start=end
        ic("changed",start,line.dxf.start)
        has_notch=True
    return has_notch

def _merge(A:dict, B:dict, f:callable)->dict:
    """updated A with B, if there are matches combine value using with F"""
    # Start with symmetric difference; keys either in A or B, but not both
    merged = {k: A.get(k, B.get(k)) for k in A.keys() ^ B.keys()}
    # Update with `f()` applied to the intersection
    merged.update({k: f(A[k], B[k]) for k in A.keys() & B.keys()})
    return merged

def _calc_qty(new_label_Dict:dict)->int:
    
    if LABEL_PART_QTY in new_label_Dict:# and str.isdigit(new_label_Dict[LABEL_PART_QTY]):
        copies=int(new_label_Dict[LABEL_PART_QTY])
    else: 
        copies=1
    multiplyer=int(new_label_Dict[LABEL_ORDER_QTY])
    return copies*multiplyer
 
def process_piece(piece:ezdxf.entities.Insert,doc:ezdxf.document.Drawing)->dict:
        '''covnerts all text into pathfinder format and deleted the rest returns dictionary of processed labels'''
        ic('------------------next---------------------')
        entityBuffer=[]
        labels=doc.blocks.get(piece.dxf.name)
        hasLabelsFlag=False
        labelList:list=[]
        labelListDict={}
        recycleBin=[]
        has_geometry=False
        pieceCoords=piece.dxf.insert
        for label in labels:
            # early exit in case file is already processed-------------------------------------------------------
                if label.dxf.layer==LABEL_LAYER:  
                    ic("piece already processed") 
                    return
                if label.dxftype() == 'TEXT':
                    #regex formats it already in [(int,str)]
                    newLabelListDict={k:v for k,v in re.findall(FIND_DXF_LABELS,label.dxf.text) }
                    #convert to dict to merge
                    if len(newLabelListDict)>1:
                        pieceCoords=label.dxf.insert
                    labelListDict=(_merge(labelListDict,newLabelListDict,lambda x,y:x+y))
                    #merge handles info comming in from pattern. 
                    hasLabelsFlag=True
                    recycleBin.append(label)
                elif label.dxftype() == "LINE" and label.dxf.layer==NOTCH_LAYER:
                    _reverse_notch(label)
                    has_geometry=True
                elif label.dxftype() in VALID_DXF_GEOMETRIES:
                    has_geometry=True
                    ic("has geo")

        # convert back to list for easy ordering
        labelList=[(k,v) for k,v in labelListDict.items()]
        entityBuffer.append([piece.dxf.name,labelList,pieceCoords])
        # entityBuffer=[entityName,new label data,coords of label]
        for doomedEntity in recycleBin:
            labels.delete_entity(doomedEntity)
        #ic(labelListDict,labelList)
        ic(labelListDict,has_geometry)
        if not labelListDict and has_geometry:
            ic("unlabeled geo")
            labelListDict={
                
            }
        return labelListDict

def BreakDxf(DXFpath:os,StartingIndex:int)->Tuple[dict,int]:
    '''splits the dxf file into one file for each piece and returns rows of data for csv (one line for each piece) and strating index.'''
    DataDicts:list[dict]=[]
    doc = ezdxf.readfile(DXFpath)
    header_vars = doc.header
    msp = doc.modelspace() #some kind of iterator with all the entities in it
    material=os.path.splitext(os.path.basename(DXFpath))[0]
    folder=os.path.dirname(DXFpath)
    
    outputPath=os.path.join(folder,"TEMP")
    i_out=StartingIndex
    # Iterate through all entities in the modelspace or pieces on the marker
    for piece_num,piece in enumerate(msp):
               
        newLabelDict=process_piece(piece,doc)

        if not newLabelDict: 
            ic(newLabelDict)
            continue
        i_out+=1
        ic(StartingIndex,piece.dxf.name,i_out)
        newDoc=deepcopy(doc)
        newDoc=Make_Single_Piece_dxf(newDoc,piece_num)
        newDoc.saveas(os.path.join(outputPath,str(i_out))+".dxf")
        peice_qty=1
        if N_PER_SET in newLabelDict:
            peice_qty=newLabelDict[LABEL_PART_QTY]
        #qty=_calc_qty(newLabelDict)
        data={FILENAME:f'{i_out}.dxf',
              MAT:material,
              UD1:newLabelDict[LABEL_FIRST],
              N_SETS:newLabelDict[LABEL_ORDER_QTY],
              N_PER_SET:peice_qty,
              NAME:newLabelDict["1"],
              ORDERID:newLabelDict[LABEL_SQ],
              PATH:outputPath,
              DATE:"",
              RECIPIE:"Simon",
              NAME:piece.dxf.name
              }
        
        DataDicts.append(data)
    return (DataDicts,i_out)

def process_DXF_Release(releasePath:os):

    DXF_files=Path(releasePath).glob("*.DXF")
    startingIndex=0
    release_data=[]
    CSV_Path=os.path.join(releasePath,DATAFILESUFFIX)

    for file in DXF_files:
        ic(file)
        marker_data=BreakDxf(file,startingIndex)
        ic(marker_data[1])
        startingIndex=marker_data[1]
        release_data.extend(marker_data[0])

    # Add string to header to prevent overwrite. 
    #header_vars[HEADER_NOTCH_FLAG_NAME]=HEADER_NOTCH_FLAG
    #try:
    ic(CSV_Path)
    with open(CSV_Path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=release_data[0].keys(), delimiter=';')
        writer.writeheader()
        writer.writerows(release_data)

    #except IOError as e:
    #print(f"Error writing to file: {e}")
    #doc.saveas(DXFpath)

process_DXF_Release(r"C:\AutometrixTools\SPEX_RAW_DXFs")
