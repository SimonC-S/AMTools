import zipfile

import xml.dom.minidom 
from icecream import ic
from typing import Optional

RELEVANT_TAGS={"a2:MaterialID":"ID",
               "a2:Name":"CNC Name",
               "a2:CopySpacing":"Gap between pieces",
               "a2:MaterialPattern":"Width"
}

def getData(node:xml.dom.minidom.NodeList,convertValues:bool=True)->str:
    """recusive function to dive though tags until it finds data"""
    if node[0].nodeValue:
        return (node.nodeValue)

    if node[0].hasChildNodes():
        if node[0].childNodes[0].nodeValue is not None:
                value=node[0].childNodes[0].nodeValue
                if node[0].nodeName=="a1:Value" and convertValues:
                    value=str(round(float(value)*2.54,3))
                return value
        else:
            value=getData(node[0].childNodes)
            return     value
        
def unzip_specific_XML_file(file_path,target_inner_file_name)->xml.dom.minidom.Node:
    """
    Extracts the the doc Element of a specific XML file in a ziped directory.

    :param file_path: Path to the ZIP dir
    :param target_inner_file_name: file name and ext(XML)
    """    

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            ic(zip_ref.namelist())
            with zip_ref.open(target_inner_file_name) as inner_zip_ref:
                DOMTree = xml.dom.minidom.parse(inner_zip_ref)
                libraryData = DOMTree.documentElement

            zip_ref.extractall(extract_to)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return libraryData

def get_specific_XML_data(docXML:xml.dom.minidom.Node,targetIterableElement:str,relevantData:list,convertValues:bool=True)->list[dict]:
    """
    :param targetIterableElement: 
    :param relevantData: list of elements to extract data out of
    :param convertValues: values in value tag are stored in inches true convets them to mm false returns them as is
    """   
    #ic(str(docXML.nodeName))
    processedDicts=[]
    materials=docXML.getElementsByTagName(targetIterableElement)
    #ic(materials)
    #loops though each instance for the element you want data from
    for m in materials:
        materialDict={}
        #loops though each requested data element you need to try and find it
        for d in relevantData:
            node=m.getElementsByTagName(d)
            materialDict[d]=getData(node)
        processedDicts.append(materialDict)
    #ic(processedDicts)
    return processedDicts

def extract_zip_file(file_path, extract_to):
    """
    Extracts the contents of a ZIP file to a specified directory.

    :param file_path: Path to the ZIP file
    :param extract_to: Directory where the contents will be extracted
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:

            zip_ref.extractall(extract_to)
            
    except zipfile.BadZipFile:
        print("The file is not a valid ZIP file.")
    except Exception as e:
        print(f"An error occurred: {e}")


       
file_path = r"C:\Users\SimonCaldwell\Desktop\extracted files\1254-XXXX-000-UPGR.templates"
extract_to = r"C:\Users\SimonCaldwell\Desktop\extracted files"
