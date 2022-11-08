from maya import cmds

def getVtxPos(obj, vtx):
    return cmds.xform("{}.vtx[{}]".format(obj, vtx), q=True, translation=True, os=True, r=True) 

def copyShape(src, tgt):
    vtxIndSrc = cmds.getAttr( src + ".vrts", multiIndices=True )
    positions = []
    src_pos = cmds.xform(src, q=True, translation=True)

    for v in vtxIndSrc:
        pos = getVtxPos(src, v)
        positions.append(pos)
    
    tgt_pos = cmds.xform(tgt, q=True, translation=True, ws=True, a=True)

    for v, pos in enumerate(positions):
        new_pos = [x + y for x, y in zip(pos, tgt_pos)]
        cmds.xform("{}.vtx[{}]".format(tgt, v), translation=new_pos, ws=True, a=True) 
        

FROM_GRP = "BS_GRP_new"
TO_GRP = "BS_GRP"

for sel in cmds.ls(sl=True):
    print(sel.split("|")[-1])
    tgt = "{}|{}".format(TO_GRP, sel.split("|")[-1])
    copyShape(sel, tgt)