
import ezdxf
import os
import re
'''opens DXF and seperates the LL1 into seperate blocks'''
DXFfile_=r"SPEXTEX Forge 1 x-1.dxf"

#DXFfile_ = os.path.join(root,filename)
doc = ezdxf.readfile(DXFfile_)
msp = doc.modelspace() #some kind of iterator with all the entities in it
for entity in msp:
    print(f"Entity type: {entity.dxftype()}, Layer: {entity.dxf.layer}")
    # entity is an insert type some kind of reference or container the represents a piece 
    labels=doc.blocks.get(entity.dxf.name)
    #print(entity.dxf.insert)
    hasLabelsFlag=False
    for label in labels: 
            
            print(f"Entity type: {label.dxftype()}, Layer: {label.dxf.layer}")
            if label.dxftype()=="LINE":
                print(f"start: {label.dxf.start}, end: {label.dxf.end}")
            """ if label.dxftype() == 'TEXT':
                #print(label.dxf.text)
                pieceCoords=label.dxf.insert
                labelList=(re.findall(r"(\d)\:(.*?)(?=\d\:|$)",label.dxf.text))
                hasLabelsFlag=True

                if labelList:
                    labels.delete_entity(label)
                    labelList.sort(key=lambda x:x[0])  
                    labelList.insert(0,[0,"CAD PIECE NUM"])

                for l in labelList:
                    Ypos=int(pieceCoords[1])-10*int(l[0])
                    Xpos=int(pieceCoords[0])
                    labels.add_text(l[1],dxfattribs={'layer':cc.LABELLAYER }).set_placement((Xpos, Ypos))
                    
                #print(labelList)"""


 
    #if new_filename!=filename:
        #os.remove(os.path.join(root,filename))
    #new_file_=os.path.join(root,new_filename+DXF_SUFFIX)

    #----------- prevents overwrite and numbers the layers------

        #-----------------------------------------------------------

#doc.saveas(new_file_)

