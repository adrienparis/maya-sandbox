import maya.OpenMaya as om

class vertex():
    mesh = ""
    id = 0
    x = 0
    y = 0
    z = 0
    neighbor = []
    weight = {}

    def __init__():
        pass

    def weightBucket(self, joint, weightFilter=lambda x, y, z: 1):
        self.weight[joint] = weightFilter(self.x, self.y, self.z)
        for n in self.neighbor:
            if joint not in n.weight:
                n.weightBucket(joint, weightFilter)



# Get the active selection
# Will work either on the selected mesh as a whole or on selected vertices
mSel = om.MSelectionList() # creation d'un objet de type selection
om.MGlobal.getActiveSelectionList(mSel) # initialisation de mSel
dagPath = om.MDagPath() # creation d'un objet dagPath
component = om.MObject() # creation d'un objet
mSel.getDagPath(0, dagPath, component) 
print("mSel      ", dir(mSel))
print("dagPath   ", dir(dagPath))
print("component ", dir(component))

# Get positions of all vertices on the mesh
meshFn = om.MFnMesh(dagPath)
positions = om.MPointArray()
meshFn.getPoints(positions, om.MSpace.kWorld)

# Iterate and calculate vectors based on connected vertices
iter = om.MItMeshVertex(dagPath, component)
connectedVertices = om.MIntArray()
listVtx = []
while not iter.isDone():
    iter.getConnectedVertices(connectedVertices) 
    # print(connectedVertices)
    iter.next()