import maya.cmds as cmds

def createAttach(mesh, U=0, V=0, name=None):
    """ Create an attachment point on a mesh at a given UV point """
    obj_type = cmds.objectType(mesh)
    if obj_type == "transform":
        mesh = cmds.listRelatives(mesh, type="shape")[0]
    elif obj_type == "shape":
        pass
    else:
        raise RuntimeError("Please select a poly shape")

    fol = cmds.createNode("follicle", name="%s_attach" % mesh if name is None else name)
    fol_trans = cmds.listRelatives(p=True)[0]

    cmds.connectAttr("%s.outMesh" % mesh, "%s.inputMesh" % fol, force=True)
    cmds.connectAttr("%s.worldMatrix[0]" % mesh, "%s.inputWorldMatrix" % fol, force=True)
    cmds.connectAttr("%s.outTranslate" % fol, "%s.translate" % fol_trans, force=True)
    cmds.connectAttr("%s.outRotate" % fol, "%s.rotate" % fol_trans, force=True)
    cmds.setAttr("%s.parameterU" % fol, U)
    cmds.setAttr("%s.parameterV" % fol, V)
    cmds.setAttr("%s.translate" % fol_trans, lock=True)
    cmds.setAttr("%s.rotate" % fol_trans, lock=True)

    return fol_trans

def createFollicleToMeshAt(mesh, vtxs):
    sel = ["{}.vtx[{}]".format(mesh, vtx )for vtx in vtxs]
    cmds.select(sel)
    cmds.ConvertSelectionToUVs()
    UVValues = cmds.polyEditUV(query=True, uValue=True )
    u = sum([i for i in UVValues[::2]]) / (len(UVValues) / 2)
    v = sum([i for i in UVValues[1::2]]) / (len(UVValues) / 2)
    
    return createAttach(mesh, u, v)


def createLocator(name, coord):
    loc = cmds.spaceLocator(n=name)[0]
    cmds.setAttr(loc + ".tx", coord[0])
    cmds.setAttr(loc + ".ty", coord[1])
    cmds.setAttr(loc + ".tz", coord[2])

# createFollicleToMeshAt("pSphere1", [279])

sel = cmds.ls(sl=True)
mesh = sel[0].split(".")[0]
vtxs = [int(v.split("[")[-1].split("]")[0]) for v in sel]
pos = cmds.xform(sel[0], q=True, t=True)
meshPose = cmds.xform(sel[0], q=True, t=True)
rel_pos = [a - b for a, b in zip(pos, meshPose)]


createLocator("jaw_init", pos)
createLocator("relative", pos)

print(mesh, vtxs)

BS = cmds.listRelatives("BS_tmp_GRP", c=True)
jaw_bs = [sh for sh in BS if "jaw" in sh.lower()]
print(jaw_bs)
for j in jaw_bs:
    jMeshPose = cmds.xform(sel[0], q=True, t=True)
    createLocator("loc_" + j, [a + b for a, b in zip(rel_pos, jMeshPose)])

