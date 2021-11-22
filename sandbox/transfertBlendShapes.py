from maya import cmds

def transfertBlendshape():
    sel = cmds.ls(sl=True)
    if len(sel) != 2:
        return
    src = sel[0]
    dst = sel[1]
    originPos = cmds.xform(src, q=True, t=True)
    bbox = cmds.exactWorldBoundingBox(dst)
    width = abs(bbox[0] - bbox[3])
    height = abs(bbox[1] - bbox[4])
    print(bbox, width, height)
    pcTmp = cmds.parentConstraint(dst, src, mo=False)
    cmds.delete(pcTmp)
    cmds.select(cl=True)
    cmds.select(dst, src)
    cmds.CreateWrap()
    history = cmds.listHistory(src)        
    blendshapes = cmds.ls(history, type='blendShape')
    history = cmds.listHistory(dst)  
    wrapDef = cmds.ls(history, type='wrap')
    weights = cmds.listAttr(blendshapes[0] + '.w' , m=True)
    for i, w in enumerate(weights):
        print(w)
        cmds.setAttr(blendshapes[0] + "." + w, 1)
        dup = cmds.duplicate(dst, n=w)[0]
        for attr in cmds.listAttr(dup, k=True):
	        cmds.setAttr("{}.{}".format(dup, attr), lock=False)
        cmds.setAttr("{}.tx".format(dup), i * width + width)
        if w.endswith("_R"):
            cmds.setAttr("{}.ty".format(dup), height * 2)
        else:
            cmds.setAttr("{}.ty".format(dup), height)

        cmds.setAttr(blendshapes[0] + "." + w, 0)
    cmds.delete(wrapDef)

    cmds.xform(src, t=originPos)

transfertBlendshape()