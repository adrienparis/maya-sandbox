import maya.OpenMaya as OpenMaya


sourceVtxs = [123,808,2336,426,2036,2106,2275,1671,456,405,357,466,2191,64,1184,1020,2498,2579,1972,1310,2488,2557,1384,2581,2563,2531,2525,199,1633,207,1612,1587,2477,1272,2483,2537,2464,2576,2451,2707,3392,4920,3010,4620,4690,4859,4255,3040,2989,2941,3050,4775,2648,3604,3768,4556,3894,3968,2783,4217,2791,4196,4171,3856]
targetVtxs = [7475,16986,18575,19042,18965,19188,19145,11355,18908,4679,18177,4632,11424,2168,3206,13590,2990,2570,8027,13640,2913,12398,14528,8082,7878,6476,278,706,7106,6903,6039,354,3052,17435,17702,16136,4278,18310,15099,9162,10133,16849,17623,18494,20151,18790,14161,16402,4524,16570,3937,9900,1676,12635,2512,12488,12740,12471,551,7209,6559,7277,293,16357]


sourceMesh = "head_preDeform_geo"
targetMesh = "Head"


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

vtxPos = particleFillSelection()
for v in sourceVtxs:
    pos = 
