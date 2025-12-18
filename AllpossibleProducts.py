from xml.dom.minidom import parseString
import xml.dom.minidom 
import csv
from icecream import ic

import os
SPEX_PROD_XML_PATH=r"C:\AutometrixTools\SPEX PRODUCTS.xml"
XML_PRODUCT="PRODUCT"
XML_PATTERN="PATTERN"
XML_VAR="VAR"
XML_RULE="RULE"
XML_PATH="PATH"
XML_GIVE="GIVE"
XML_GET="GET"
RESOURCE_PATH=r"C:\Users\SimonCaldwell\Medifab\Spex CNC - Controlled Files\Input"
OUTPUTPATH=r"C:\AutometrixTools\allProds.csv"
HEAD_CSV_PATH=r"C:\Users\SimonCaldwell\Medifab\Spex CNC - Controlled Files\Input\SAVE_HEARDERS.csv"
MasterPatternList={}
DOMTree = xml.dom.minidom.parse(SPEX_PROD_XML_PATH)
productData = DOMTree.documentElement
def getHeader():
     with open(HEAD_CSV_PATH,mode='r') as csv_file:
                                                     # Header contains all possible Variables our products need Workflow need these even if they arent populated.
            reader = csv.reader(csv_file,delimiter=',')

            spex1Header=reader.__next__() #read fist line
            return spex1Header

products=productData.getElementsByTagName(XML_PRODUCT) #XML ELEMENTS
for p in products:
    
    vars = p.getElementsByTagName(XML_VAR)
    varDict={}
    for var in vars:
                var=var.childNodes[0].data
                
                var=var.split('=')    # allows you to assign variable directly in the XML
                if len(var)==2:
                    varDict[var[0]]=var[1]
                else:
                    varDict[var[0]]='0'
    rules= p.getElementsByTagName(XML_RULE)
    varDict["WIDTH"]=16
    varDict["DEPTH"]=18
    varDict["HEIGHT"]=18
    varDict["BOARDERCOLOUR"]="28"
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
                patterns=[r[get] for r in reader ]
                unique_Patterns=list(set(patterns))
                ic(unique_Patterns)                                
            '''for row in reader:
                
                #if row[give]==varDict[give]:
                    #append to label dont overwrite.
                    #if get==cc.LABEL:
                     #   varDict[get]=varDict[get]+row[get]
                      #  break
                    varDict[get]=row[get]
                    
                    if XML_PATTERN in get:
                        varDict[XML_PATTERN]=row[get]
                        
                    break
            else: 
        
                ic(f'Couldnt Fetch: PATH: {path} GIVE: {give}:{varDict[give]} GET: {get}')'''
        
        for Up in unique_Patterns:
            VardictCopy=dict(varDict)
            VardictCopy[XML_PATTERN]=Up
            MasterPatternList[Up]=VardictCopy
            
    #ic(varDict,p.getElementsByTagName(XML_PATTERN)[0].childNodes[0].data)
    if len(unique_Patterns)==0:
        MasterPatternList[p.getElementsByTagName(XML_PATTERN)[0].childNodes[0].data]=varDict
ic(MasterPatternList)
#ic((MasterPatternList))
#with open(OUTPUTPATH,mode='w') as dump:
#    for line in MasterPatternList:
#         dump.write(str(line))
with open(OUTPUTPATH,mode="w")as csvw:
    dictWriter=csv.DictWriter(csvw,fieldnames=getHeader())
    dictWriter.writeheader()
    dictWriter.writerows(MasterPatternList.values())