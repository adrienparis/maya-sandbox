import maya.cmds as cmds

def getShapeAndOrig(name):
    o = cmds.listRelatives(name)
    if len(o) != 2:
        return None, None
    if "Orig" in o[0] and "Orig" in o[1]:
        print("The skinned mesh have two ShapeOrig")
        return None, None
    if not "Orig" in o[0] and not "Orig" in o[1]:
        print("The skinned mesh does not have a ShapeOrig")
        return None, None
    if not "Shape" in o[0] or not "Shape" in o[1]:
        print("there is not Shape in the skinned mesh")
        return None, None
    if "Orig" in o[0]:
        return name + "|" + o[1], name + "|" + o[0]
    else:
        return name + "|" + o[0], name + "|" + o[1]

def transfertUV(src, dest):
    '''src: mesh avec les nouveaux UVs
    dest: mesh avec le skin
    '''
    shape, orig = getShapeAndOrig(dest)
    if shape == None or orig == None:
        return
    print(shape + ".intermediateObject")
    cmds.setAttr(shape + ".intermediateObject", 1)
    cmds.setAttr(orig + ".intermediateObject", 0)
    cmds.transferAttributes(src, dest, transferPositions=0, transferNormals=0, transferUVs=2, transferColors=2, sampleSpace=0, sourceUvSpace="map1", targetUvSpace="map1", searchMethod=3, flipUVs=0, colorBorders=1)
    cmds.delete(dest, ch=True)
    cmds.setAttr(shape + ".intermediateObject", 0)
    cmds.setAttr(orig + ".intermediateObject", 1)

sl = cmds.ls(sl=True, l=True)
print(sl)
transfertUV(sl[0], sl[1])
