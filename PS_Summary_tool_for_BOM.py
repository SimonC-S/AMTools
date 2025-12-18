from pypdf import PdfReader
from icecream import ic
import re
import csv
import os
from functools import reduce
from dataclasses import dataclass

"""
Simon Caldwell 04-2025
processed print to PDF patternsmith exports 
Processes all in target folder
use qty to define sizes for graded patterns!! 
Layered fabrics to sort out lamitated and double layer fabrics.
"""
target_folder=r'C:\Users\SimonCaldwell\Medifab\Spex CNC - MarkerFiles-PatternSmith\WSS\BOM'
PDF_FILE=r'\.pdf$'
WEIRD_FACTOR=0.000254
LAYERED_FABRICS={"PALMHIVE,LOOP":["LOOP","PALMHIVE"]
                 ,"10MM EVA75 DOUBLE LAYER":["10MM EVA 75","10MM EVA 75"]}
NAMED_COLS={
    "INDEX":0,
    "Pattern_Name":1,
    "Copies":2,
    "Qty":3,
    "Area":4,
    "Total:Area":5,
}

relevant_area=NAMED_COLS["Area"]

@dataclass
class piece():
    qtyName:str
    mat:dict
    area:float

    def __post_init__(self):
        newDict={}
        # find if any of the fabrics in mat are layered fabrics and add them to the mat dict if they are. 
        for k,v in list(self.mat.items()):
            if not k in LAYERED_FABRICS:
                continue
            for nf in LAYERED_FABRICS[k]:
                if nf in self.mat:
                    self.mat[nf]=self.mat[nf]*2
            #self.mat hasnt been updated yet do if both entries in layered fabrics are the same update newdict instead
                elif nf in newDict:
                    newDict[nf]=self.area*2
                else:
                    newDict.update({nf:self.mat[k]})
        ic(newDict)
        self.mat.update(newDict)
        ic(self.mat)

    def __add__(self,other):
        #ic(other.mat)
        newDict={}
        for k,v in other.mat.items():
            if k in self.mat:
                self.mat[k]+=other.mat[k]
            else: 
                newDict.update({k:v})
        self.mat.update(newDict)
        return self
    
    def getDict(self):
        dictrep=self.mat
        dictrep.update({"Size":self.qtyName})
        ic(dictrep)
        return dictrep

def GroupLike(table:list[piece]):
    '''takes table and groups all the parts adding their area values'''
    #make empty dict of all the names
    ic(table)
    rolCall={p.qtyName:[] for p in table}
    #fill dict wth piece objects
    for row in table:
        rolCall[row.qtyName].append(row)
    for k ,v in rolCall.items():
        rolCall[k]=reduce(lambda x, y: x+y,v)

    return rolCall

def extractTable(fn,root)->list:
    reader = PdfReader(os.path.join(root,fn))
    #merge all pages into one
    pages = reader.pages
    book=''
    for page in pages:
        book+=page.extract_text(extraction_mode="layout")
  
    table=book.split('#')
    for t in table[1:]:
        t='#'+t
    table=reduce(lambda x, y: "#"+x+"#"+y,table)
    ic(table)
    table=table.split('\n')
    ic(len(table))
    newTable=[]

    for i in range(len(table)):
        table[i]=re.sub(r"\s{3,}",'|',table[i])
        table[i]=table[i].split('|')
        #check for end of table
        #if len(table[i])<8:
            # reached end of table
            #trunc=i
           # break
    
        #remove the empty first col
        

        if len(table[i])<8 or not (table[i][relevant_area]).isdigit():
            continue 
        
        if table[i][0]=='':
            table[i].pop(0)
        
            table[i][4]=float(table[i][relevant_area])*WEIRD_FACTOR
   
            #table[i][4]=table[i][4]+"M2"
        newTable.append(piece(qtyName=table[i][NAMED_COLS["Qty"]],area=table[i][relevant_area],mat={fn.split(".")[0]:float(table[i][relevant_area])}))
        #table[i].pop(1)
        #ic(len(table[i]),table[i])

    ##   table=table[:trunc]
    return newTable


for root, dirs, files in os.walk(target_folder):
    allTables=[]
    for filename in files:
        if not re.search(PDF_FILE, filename, re.I):
            continue
        allTables+=(extractTable(filename,root))
result=GroupLike(allTables)
ic(result)
data=[v.getDict() for K,v in result.items()]
header=[]
ic(data)
for DataDict in data:
    ic(DataDict)
#head+=([k for k in l.keys() if k not in head])
    header+=[k for k in DataDict.keys() if k not in header]


csvPath=os.path.join(target_folder,"total.csv")
with open(csvPath, 'w',newline='') as csvfile:
        # creating a csv writer object
        csvwriter = csv.DictWriter(csvfile,fieldnames=header)
        csvwriter.writeheader()
        csvwriter.writerows(data)

