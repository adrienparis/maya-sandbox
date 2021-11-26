from maya import cmds


def getSkinCluster(vtx):
    obj = vtx.split(".")[0]
    shp = obj.split("|")[-1]+ "Shape"
    shapeNode = obj + "|" + shp
    histList = cmds.listHistory(obj)
    if histList:
        for histItem in histList:
            if cmds.objectType(histItem) == "skinCluster":
                return histItem
def getInfluentJoints(vtx, skinCluster):
    weights = cmds.skinPercent( skinCluster, vtx, query=True, value=True)
    joints = cmds.skinCluster( skinCluster, q=True, inf=True)
    jointWeight = {}
    for j, w in zip(joints, weights):
        if w < 0.001:
            continue
        jointWeight[j] = w
    return jointWeight

getVtxNb = lambda mesh : len(cmds.getAttr( mesh + ".vrts", multiIndices=True ))

mesh = "msh_body"
print(getVtxNb(mesh))
skclst = getSkinCluster(mesh)
slVtx = []
for v in range(0, getVtxNb(mesh)):
    vtx = "{}.vtx[{}]".format(mesh, v)
    joints = getInfluentJoints(vtx, skclst)
    if "sk_jaw" in joints:
        slVtx.append(vtx)
cmds.select(cl=True)
cmds.select(slVtx)

