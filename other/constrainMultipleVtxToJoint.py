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

def getUVCoordToPoint(mesh_shape, point):

    #Creating the ClostPointOnMesh node to get U and V parameter
    CPOM=cmds.createNode('closestPointOnMesh')
    cmds.connectAttr(mesh_shape+'.worldMesh', CPOM+".inMesh")

    #Applying joints translate to InPosition on CPOM nodes
    for p, axis in zip(point, ['X','Y','Z']):
        cmds.setAttr(CPOM+'.inPosition'+axis, p)

    #Getting CPOM nodes UV values and applying it to follicles UV values
    valueU=cmds.getAttr(CPOM+'.parameterU')
    valueV=cmds.getAttr(CPOM+'.parameterV')
    #Deleting unused CPOM nodes
    cmds.delete(CPOM)
    return valueU, valueV




sel = cmds.ls(sl=True)
jnt = cmds.ls(sl=True, type="joint")[0]
vtx = [s for s in sel if s not in jnt]
mesh = vtx[0].split('.')[0]

follicles = []
for v in vtx:
    p = cmds.xform(v, query=True, translation=True, worldSpace=True)
    u, v = getUVCoordToPoint(shape, p)
    follicles.append(createAttach(mesh, u, v))

cmds.pointConstraint(follicles, jnt, mo=True, n="{}_PC".format(j.replace("sk_", "flc_")))
for i, f in enumerate(follicles):
    cmds.rename(f, "flc_{}_{}_attach".format(jnt, i))
cmds.select(sel)