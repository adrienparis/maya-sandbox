import operator
import maya.OpenMaya as OpenMaya
import math
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

def createFollicleToMeshAt(mesh, vtxs, name=None):
    sel = ["{}.vtx[{}]".format(mesh, vtx )for vtx in vtxs]
    cmds.select(sel)
    cmds.ConvertSelectionToUVs()
    UVValues = cmds.polyEditUV(query=True, uValue=True )
    u = sum([i for i in UVValues[::2]]) / (len(UVValues) / 2)
    v = sum([i for i in UVValues[1::2]]) / (len(UVValues) / 2)

    return createAttach(mesh, u, v)

def distance(A, B):
    return math.sqrt(math.pow(A[0]-B[0],2) + math.pow(A[1]-B[1],2) + math.pow(A[2]-B[2],2))

def getClosestVtxToPoint(vtxs, point):
    closest = None
    for i, v in enumerate(vtxs):
        if closest is None:
            d = distance(point, v)
            closest = (i, v, d)
            continue
        vtxDist = distance(point, v)
        if vtxDist < closest[2]:
            closest = (i, v, vtxDist)
    return closest[0]

def getListClosestVtxToPoint(vtxs, point, radius=0.01):
    distVtxs = [(i, distance(point, v)) for i, v in enumerate(vtxs)]
    distVtxs = [(i, d) for i, d in distVtxs if d < radius]
#    distVtxs.sort()
#    distVtxs = distVtxs[:5]
    distVtxs = [i for i, d in distVtxs]
    return distVtxs

def getClosestVertex(mesh, pos=(0,0,0)):
    '''
    returns the closest vertex in mesh for a xyz position as pos
    '''
    print('/ / / Getting closest point on {} for selection / / /'.format(mesh))
    pos = OpenMaya.MPoint(pos)
    sel = OpenMaya.MSelectionList()
    sel.add(mesh)
    fn_mesh = OpenMaya.MFnMesh(sel.getDagPath(0))
    index = fn_mesh.getClosestPoint(pos, space=OpenMaya.MSpace.kWorld)[1]  # closest polygon index
    face_vertices = fn_mesh.getPolygonVertices(index)  # get polygon vertices
    print(face_vertices)
    vertex_distances = ((vertex, fn_mesh.getPoint(vertex, OpenMaya.MSpace.kWorld).distanceTo(pos))
                         for vertex in face_vertices)
    print(vertex_distances)
    return min(vertex_distances, key=operator.itemgetter(1))

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

def particleFillSelection(  ):

	# get the active selection
	selection = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList( selection )
	iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)

	# go througt selection
	while not iterSel.isDone():

		# get dagPath
		dagPath = OpenMaya.MDagPath()
		iterSel.getDagPath( dagPath )

		# create empty point array
		inMeshMPointArray = OpenMaya.MPointArray()

		# create function set and get points in world space
		currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
		currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kWorld)

		# put each point to a list
		pointList = []

		for i in range( inMeshMPointArray.length() ) :

			pointList.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )

		return pointList

mesh = cmds.ls(sl=True)[0]

vtxs = particleFillSelection()

# print(cmds.ls(type="joint"))
# closest = {}
# for j in cmds.ls(type="joint"):
#     p = cmds.xform(j, query=True, translation=True, worldSpace=True)
#     # closest[j] = getClosestVertex(mesh, p)
#     closest[j] = [getClosestVtxToPoint(vtxs, p)]
#     # closest[j] = getListClosestVtxToPoint(vtxs, p)

# for j, c in closest.items():
#     if c:
#         f = createFollicleToMeshAt(mesh, c, j)
#         cmds.parentConstraint(f, j, mo=True, n="{}_PC".format(j.replace("sk_", "flc_")))
#         cmds.rename(f, "flc_{}_attach".format(j))
# # closest = ["head_preDeform_geo.vtx[{}]".format(i) for i in closest]
# # cmds.select(closest)



for j in cmds.ls(type="joint"):
    p = cmds.xform(j, query=True, translation=True, worldSpace=True)
    u, v = getUVCoordToPoint(p)
    f = createAttach(mesh, u, v)
    cmds.parentConstraint(f, j, mo=True, n="{}_PC".format(j.replace("sk_", "flc_")))
    cmds.rename(f, "flc_{}_attach".format(j))


def getSkinCluster(self, dag):
    """A convenience function for finding the skinCluster deforming a mesh.

    params:
      dag (MDagPath): A MDagPath for the mesh we want to investigate.
    """

    # useful one-liner for finding a skinCluster on a mesh
    skin_cluster = cmds.ls(cmds.listHistory(dag.fullPathName()), type="skinCluster")

    if len(skin_cluster) > 0:
      # get the MObject for that skinCluster node if there is one
      sel = OpenMaya.MSelectionList()
      sel.add(skin_cluster[0])
      skin_cluster_obj = OpenMaya.MObject()
      sel.getDependNode(0, skin_cluster_obj)

      return skin_cluster[0], skin_cluster_obj

    else:
      raise RuntimeError("Selected mesh has no skinCluster")