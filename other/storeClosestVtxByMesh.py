
import maya.OpenMaya as OpenMaya
from maya import cmds
import time

fakeDistanceBetween = lambda x, y: sum([(a - b)**2 for a, b in zip(x, y)])


class Clock:
    def __init__(self):
        self.start = time.time()
        self.elapse = time.time()

    def lapse(self):
        v = time.time() - self.elapse
        self.elapse = time.time()
        return v

    def read(self):
        return time.time() - self.start

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

def combineCleanMeshs(meshs):
    if not meshs:
        return
    dup = cmds.duplicate(meshs)
    cmds.parent(dup, w=True)
    comb = cmds.polyUnite(dup, ch=False, mergeUVSets=1, centerPivot=True, name=meshs[0] + "_Combine")
    cmds.delete(dup)
    return comb

def fastGetClosestUnique(combMesh, smallMeshs):
    c = Clock()
    cmds.progressWindow(title="Match closest vtx", progress=0, status="starting")

    combVtx = getVtxPos(combMesh)
    meshMatch = {}
    combIndex = range(len(combVtx))
    totalSize = len(combIndex)
    for im, s in enumerate(smallMeshs):
        smVtx = getVtxPos(s)
        result = []
        remain = len(combIndex)
        cmds.progressWindow(e=True, title="{}/{}".format(im, len(smallMeshs)))
        for ismv, pointSmV in enumerate(smVtx):
            closest = None

            amount = (float(ismv) / float(len(smVtx))) * 100
            cmds.progressWindow(e=True, progress=amount, status="vtx: {}/{}".format(ismv, len(smVtx)))

            for i in combIndex:
                pointCmV = combVtx[i]
                vtxDist = fakeDistanceBetween(pointSmV, pointCmV)
                closest = (i, pointCmV, vtxDist) if closest is None or vtxDist < closest[2] else closest
            result.append(closest[0])
            combIndex.remove(closest[0])
        meshMatch[s] = result
        print(s, c.lapse())
    cmds.progressWindow(endProgress=True)
    print(c.read())
    return meshMatch

def ezGetMatchingVtx(meshs):
    count = 0
    meshMatch = {}
    for s in meshs:
        vtx = cmds.ls(s+'.vtx[*]', fl=True)
        meshMatch[s] = range(count, count + len(vtx))
        count += len(vtx)
    return meshMatch

def getSkinCluster(node):
    hist = cmds.listHistory(node, lv=1)
    if hist:
        skinCl = cmds.ls(hist, type="skinCluster")
        if skinCl:
            return skinCl
    return None

def copySkin(setSource, setDest):
    oldSel = cmds.ls(sl=True)
    cmds.select(setSource, setDest)
    cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
    cmds.select(oldSel)

def get_shell_faces(mesh):
    shells = []  # We'll be putting in lists of face indexes in here later. Each sub-list will represent a separate shell.

    sel = cmds.ls(sl=True)

    faces = cmds.ls(mesh + ".f[*]", flatten=True)  # Get all face indexes from the object.

    for face in faces:
        index = int(face.split("[")[1].rstrip("]"))  # Extract the faces index number.
        cmds.polySelect(mesh, extendToShell=index)  # Use the face's index to select the whole shell.

        new_faces = cmds.ls(sl=True, flatten=True)  # Now that the shell is selected, capture its faces.
        shells.append(new_faces)  # Append the face's as a new shell.

        # Remove indexes from the new shell from this current loop, to optimize, and to avoid adding duplicate shells.
        for new_face in new_faces:
            if new_face in faces:
                faces.pop(faces.index(new_face))

    cmds.select(sel)  # Restore selection.

    return shells

def getWeightsFrom(meshs):
    weights = []
    for s in meshs:
        skclst = getSkinCluster(s)
        if not skclst:
            continue
        print(skclst)
        weights += cmds.skinCluster(skclst, q=True, wi=True)
    weights = list(set(weights))
    return weights


sel = cmds.ls(sl=True)
comb = combineCleanMeshs(sel)[0]
weights = getWeightsFrom(sel)
mm = ezGetMatchingVtx(sel)
firstElem = sel.pop(0)

# mm = fastGetClosestUnique(comb, sel)


skclst = cmds.skinCluster(comb, weights, tsb=True)[0]

skclstStart = getSkinCluster(firstElem)[0]
cmds.copySkinWeights(ss=skclstStart, ds=skclst, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')

for k, v in mm.items():
    print(k)
    skclst = getSkinCluster(k)
    if not skclst:
        continue
    src = [u"{}.vtx[{}]".format(k, i) for i in v]
    dst = [u"{}.vtx[{}]".format(comb, i) for i in v]
    copySkin(src, dst)
