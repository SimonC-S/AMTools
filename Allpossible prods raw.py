import xml.dom.minidom
import csv
from icecream import ic
import os
import Common_const as cc

SPEX_PROD_XML_PATH=r"C:\Users\SimonCaldwell\Medifab\Spex CNC - Controlled Files\Input\SPEX PRODUCTS.xml"
XML_PRODUCT="PRODUCT"
XML_PATTERN="PATTERN"
XML_VAR="VAR"
XML_RULE="RULE"
XML_PATH="PATH"
XML_GIVE="GIVE"
XML_GET="GET"
XML_VALUE="value"
CODECOMPONENTS=[cc.FIRST,cc.SECOND,cc.THIRD,cc.FORTH]
NONEISH_PATTERNS=[None,"NONE","PARENT"]

RESOURCE_PATH=r"C:\Users\SimonCaldwell\Medifab\Spex CNC - Controlled Files\Input"
OUTPUTPATH=r"C:\Users\SimonCaldwell\Medifab\Spex CNC - MarkerFiles-PatternSmith\ALL PRODS\DATA\ALL PRODSRAWRELEASE.csv"
HEAD_CSV_PATH=r"C:\Users\SimonCaldwell\Medifab\Spex CNC - Controlled Files\Input\SAVE_HEARDERS.csv"
MasterPatternList={}
DOMTree = xml.dom.minidom.parse(SPEX_PROD_XML_PATH)
productData = DOMTree.documentElement
possible_Prods=[]
products=productData.getElementsByTagName(XML_PRODUCT) #XML ELEMENTS
unique_Patterns=[]
for p in products:
    prod_added_flag=False
    
    
    codeDict={cc.FIRST: p.getElementsByTagName(cc.FIRST)[0].childNodes[0].data,
              cc.SECOND: p.getElementsByTagName(cc.SECOND)[0].childNodes[0].data,
              cc.THIRD: p.getElementsByTagName(cc.THIRD)[0].childNodes[0].data,
              cc.FORTH: p.getElementsByTagName(cc.FORTH)[0].childNodes[0].data,
              cc.SIZE:"1618",
              cc.BORDERCOLOUR:99,
              cc.PATTERNID:p.getElementsByTagName(cc.PATTERNID)[0].childNodes[0].data
              }
    
    #ic(codeDict)
    rules= p.getElementsByTagName(XML_RULE)
   
    # find all the rules that change the pattern, lookup the unique patterns and add them to the 
    if rules is not None:
    
        #try:
        for rule in rules:
            
            path=rule.getElementsByTagName(XML_PATH)[0].childNodes[0].data   #Path of the CSV to look up
            give=rule.getElementsByTagName(XML_GIVE)[0].childNodes[0].data   # Name of Value to look up needs to match one of the VARS
            get=rule.getElementsByTagName(XML_GET)[0].childNodes[0].data     # name of Expected return value. need to match one of the VARS
            reader=[]
            path=(RESOURCE_PATH+path)
            #ic(path)
            try:
                with open(path, mode='r') as csv_file:  
                    #print(path)                       # open CSV to look up
                    reader=csv.DictReader(csv_file)       
                    reader=[row for row in reader]
            except:
                print=f'cant open{path}'
                
            if XML_PATTERN in get:
                
                directions_to_unique_patterns=[]
                for r in reader:
                    if r[get] not in unique_Patterns:
                        
                        unique_Patterns.append(r[get])
                        directions_to_unique_patterns.append([give,r[give]])
                    
                #ic(directions_to_unique_patterns)
                for dtup in directions_to_unique_patterns:
                    # dtup=[column name,value to give]
                    # for cases when the WIDTH is used as a criteria to select the pattern
                    if dtup[0] == cc.WIDTH:
                        # make a copy of the dict for this case
                        newCodeDict=dict(codeDict)
                        # add preceeding 0 if WIDTH has only one digit 
                        if len(dtup[1])>2:
                            dtup[1]="0"+dtup[0]
                        #add Depth or Height always 16
                        size=dtup[1]+"16"
                        newCodeDict[cc.SIZE]=size
                        possible_Prods.append(newCodeDict)
                        prod_added_flag=True
                    elif dtup[0] == cc.DEPTH or dtup[0]==cc.HEIGHT:
                        newCodeDict=dict(codeDict)
                        if len(dtup[1])>2:
                            dtup[1]="0"+dtup[0]
                        size="16"+dtup[1]
                        newCodeDict[cc.SIZE]=size
                        possible_Prods.append(newCodeDict)
                        prod_added_flag=True
                    elif dtup[0] == cc.BORDERCOLOUR:
                        newCodeDict=dict(codeDict)
                        newCodeDict[cc.BORDERCOLOUR]=dtup[1]
                        possible_Prods.append(newCodeDict)
                        prod_added_flag=True
                    elif dtup[0] in CODECOMPONENTS:
                        newCodeDict=dict(codeDict)
                        newCodeDict[dtup[0]]=dtup[1]
                        possible_Prods.append(newCodeDict)
                        #ic(newCodeDict)
                        prod_added_flag=True
                    elif dtup[0] == cc.CODE:
                        newCodeDict=dict(codeDict)
                        new_code={CODECOMPONENTS[i]:split for i,split in enumerate(dtup[1].split("-"))}
                        newCodeDict.update(new_code)
                        ic(newCodeDict)
                        possible_Prods.append(newCodeDict)
                        #ic(newCodeDict)
                        prod_added_flag=True
                    elif dtup[0] == cc.SIZE:
                        newCodeDict=dict(codeDict)                        
                        newCodeDict[cc.SIZE]=dtup[1]
                        possible_Prods.append(newCodeDict)
                        prod_added_flag=True
                        
        if prod_added_flag==False:
            #ic("basic prod")
            
            if cc.PATTERNID in codeDict.keys():
                if codeDict[cc.PATTERNID] not in unique_Patterns and not codeDict[cc.PATTERNID] in NONEISH_PATTERNS:
                    possible_Prods.append(dict(codeDict))
                unique_Patterns.append(codeDict[cc.PATTERNID])  
#ic(possible_Prods)
processed_Prods=[]
for d in possible_Prods:
    pn=f'{d[cc.FIRST]}-{d[cc.SECOND]}-{d[cc.THIRD]}'
    if not d[cc.FORTH] == cc.NONE and not d[cc.FORTH] == cc.XML_ANY:
        pn=f"{pn}-{d[cc.FORTH]}"
    #ic( not d[cc.BORDERCOLOUR]==int(cc.BLACK_PALMHIVE),not d[cc.BORDERCOLOUR] == '')
    if not str(d[cc.BORDERCOLOUR])== cc.BLACK_PALMHIVE :
        if str(d[cc.BORDERCOLOUR])=="209":
            pn=f"{pn}_{d[cc.BORDERCOLOUR]}"
        else:
            pn=f"{pn}_0{d[cc.BORDERCOLOUR]}"
    processed_Prods.append({cc.PART_NUMBER:pn,
                            cc.QTYSHEET:"1",
                            cc.SIZE_SHEET:d[cc.SIZE],
                            cc.SQSHEET:pn
                            })
#ic(processed_Prods)
with open(OUTPUTPATH,mode="w")as csvw:
    dictWriter=csv.DictWriter(csvw,fieldnames=cc.CSV_HEADERS)
    dictWriter.writeheader()
    dictWriter.writerows(processed_Prods)