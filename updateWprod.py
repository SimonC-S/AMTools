import os
from icecream import ic
import re
'''adds routing for <LL1> label text to all Wprod file in FOLDERPATH'''
FOLDERPATH=r"C:\AutometrixTools\Test_Wprods"
REPLACEMENT_STRING="""<WorkflowProductTemplatesVariable>
      <Name>LL1</Name>
      <Column>LL1</Column>
      <Value></Value>
      <ReadFromOrder>true</ReadFromOrder>
      <ValueType>String</ValueType>
    </WorkflowProductTemplatesVariable>
    </Properties>
    <Materials>"""
MATCH_STR_LL1=r"(<\/Properties>.*<Materials>)"

MATCH_STR_WORKFLOW_MAT=r"(?<=...<WorkflowMaterial>\n)\s*<Name>(.*)<\/Name>"
REPLACEMENT_WORKFLOW_MAT=r"<Name>xx \g<1></Name>"

for root, dirs, files in os.walk(FOLDERPATH):
    for filename in files:
        full_filename=os.path.join(root,filename)
        with open(full_filename,mode='r+',encoding="utf-8") as fileHandle:
            fileContent=fileHandle.read()
            fileHandle.seek(0)
            #ic(type(fileContent))
            #if "<Name>LL1</Name>" in fileContent:
            #    ic("Already has ll1")
            #    continue

            #fileContentUpdated=re.sub(MATCH_STR_LL1,REPLACEMENT_STRING,fileContent,flags=re.S)
            fileContentUpdated=re.sub(MATCH_STR_WORKFLOW_MAT,REPLACEMENT_WORKFLOW_MAT,fileContent,flags=re.S)

            ic(fileContent is fileContentUpdated)
            fileHandle.write(fileContentUpdated)
            fileHandle.truncate()
      