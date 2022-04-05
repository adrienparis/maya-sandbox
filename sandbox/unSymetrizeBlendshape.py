import math
from maya import cmds


def getVtxPos(shapeNode) :
 
	vtxWorldPosition = []
 
	vtxIndexList = cmds.getAttr( shapeNode+".vrts", multiIndices=True )
	for i in vtxIndexList :
		curPointPosition = cmds.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, objectSpace=True ) 
		vtxWorldPosition.append(curPointPosition)
 
	return vtxWorldPosition

# def assignweight(blendshapes, vtxs, index, weight):
# 	for v in vtxs:
# 		cmds.setAttr("{}.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]".format(blendshapes, index, v), weight)

def assignweight(blendshapes, vtxs, index, weight, f, t):
	minW = min(f, t)
	maxW = max(f, t)
	for v, pos in enumerate(vtxs):
		if pos[0] >= minW and pos[0] <= maxW:
			cmds.setAttr("{}.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]".format(blendshapes, index, v), weight)

def assignWeightLinear(blendshapes, vtxs, index, fromWeight, toWeight):

	minW = min(fromWeight, toWeight)
	maxW = max(fromWeight, toWeight)

	for v, pos in enumerate(vtxs):
		if pos[0] >= minW and pos[0] <= maxW:
			weight = abs(pos[0] - fromWeight) / abs(toWeight - fromWeight) 
			cmds.setAttr("{}.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]".format(blendshapes, index, v), weight)

def assignWeightSmooth(blendshapes, vtxs, index, fromWeight, toWeight):

	minW = min(fromWeight, toWeight)
	maxW = max(fromWeight, toWeight)

	total = abs(toWeight - fromWeight) 
	for v, pos in enumerate(vtxs):
		if pos[0] >= minW and pos[0] <= maxW:
			value = abs(pos[0] - fromWeight) / total
			weight = (-1 * math.cos(value * math.pi) + 1) / 2
			cmds.setAttr("{}.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]".format(blendshapes, index, v), weight)

sel = cmds.ls(sl=True)
mesh = sel[0]
history = cmds.listHistory( mesh )
blendshapes = cmds.ls( history, type='blendShape')
weights = cmds.listAttr( blendshapes[0] + '.w' , m=True )

gap = 0.15
vtxs = getVtxPos(mesh)
vtxs_L = [i for i, v in enumerate(vtxs) if v[0] <= -1 * gap]
vtxs_R = [i for i, v in enumerate(vtxs) if v[0] >= gap]
vtxs_C = [i for i, v in enumerate(vtxs) if v[0] <= -1 * gap and v[0] >= gap]

# cmds.select(mshVtx)
# assignweight(vtxs, 0, 0)

for j, side in enumerate([("_L", vtxs_L), ("_R", vtxs_R)]):
	for i, _ in enumerate(sorted(weights)):
		name = cmds.listConnections("{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputGeomTarget".format(blendshapes[0], i) )[0]
		print(name)

		cmds.setAttr(blendshapes[0] + "." + name, 1)
		if side[0] == "_L":
			assignweight(blendshapes[0], vtxs, i, 1, 0, 50)
			assignweight(blendshapes[0], vtxs, i, 0, 0, -50)
		elif side[0] == "_R":
			assignweight(blendshapes[0], vtxs, i, 0, 0, 50)
			assignweight(blendshapes[0], vtxs, i, 1, 0, -50)
		# assignweight(blendshapes[0], side[1], i, 0)
		# assignweight(blendshapes[0], vtxs_C, i, 0.5)
		assignWeightSmooth(blendshapes[0], vtxs, i, -1 * gap, gap)
		dup = cmds.duplicate(mesh, n=name + side[0])[0]
		cmds.setAttr("{}.tx".format(dup), i * 3 + 4)
		cmds.setAttr("{}.ty".format(dup), j * 4 + 4)
		cmds.setAttr(blendshapes[0] + "." + name, 0)
		assignweight(blendshapes[0], vtxs, i, 1, -50, 50)
	gap = gap * -1

