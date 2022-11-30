
import maya.OpenMaya as OpenMaya
from maya import cmds
import time

fakeDistanceBetween = lambda x, y: sum([(x[i] - y[i])**2 for i, x, y in enumerate(zip(x, y))])

def getVtxPos(mesh):
    """mesh : str = name of the mesh (the transform, not the shape)
    return value : array of array (first array is for each vtx, second array is x y z coordinates)

    Get the coordinate of each vertex of a mesh

    author -> Dorian Fevrier
    """

    # get the active selection
    selection = OpenMaya.MSelectionList()
    selection.add(mesh)
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
        currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kObject)

        # put each point to a list
        pointList = []
        for i in range( inMeshMPointArray.length() ) :
            pointList.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )

        return pointList

def getClosestVtxToPnt(vtxs, point):
    closest = None
    for i, v in enumerate(vtxs):
        if closest is None:
            d = fakeDistanceBetween(point, v)
            closest = (i, v, d)
            continue
        vtxDist = fakeDistanceBetween(point, v)
        if vtxDist < closest[2]:
            closest = (i, v, vtxDist)
    return closest[0]

def matchinVtxClosest(meshAlpha, meshBeta):
    vtxPosAlpha = getVtxPos(meshAlpha)
    vtxPosBeta = getVtxPos(meshBeta)
    newList = []
    for vtx in vtxPosAlpha:
        clstVtx = getClosestVtxToPnt(meshBeta, vtx)
        newList.append((vtx, clstVtx))
    return newList

if __name__ == "__main__":
    tStart = time.time()
    matchinVtxClosest()
    tStop = time.time()
    print(tStart - tStop)
