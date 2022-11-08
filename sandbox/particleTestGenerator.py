import sys, random
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "dmmEmitter"
kPluginNodeId = OpenMaya.MTypeId(0x8700C)#0x0010D495)

class dmmEmitter(OpenMayaMPx.MPxEmitterNode):

	inTetFlags = None
	inTetNodes = None#OpenMaya.MObject()
	lastTetFlags = None
	speedRange = None
	particlesPerFracture = None
	dmmTetFaceMagic = (1, 2, 3, 0, 3, 2, 0, 1, 3, 0, 2, 1)

	def __init__(self):
		OpenMayaMPx.MPxEmitterNode.__init__(self)

	@staticmethod
	def getTetFaceCentroid(tetNodes, tetId, faceId):
		tv1 = [0, 0, 0]
		tv2 = [0, 0, 0]
		tv3 = [0, 0, 0]
		index = 12 * tetId + 3 * dmmEmitter.dmmTetFaceMagic[3 * faceId + 0]
		for i in range(0, 3):
			tv1[i] = tetNodes[index + i]
		index = 12 * tetId + 3 * dmmEmitter.dmmTetFaceMagic[3 * faceId + 1]
		for i in range(0, 3):
			tv2[i] = tetNodes[index + i]
		index = 12 * tetId + 3 * dmmEmitter.dmmTetFaceMagic[3 * faceId + 2]
		for i in range(0, 3):
			tv3[i] = tetNodes[index + i]
		return ((tv1[0] + tv2[0] + tv3[0]) / 3,
				(tv1[1] + tv2[1] + tv3[1]) / 3,
				(tv1[2] + tv2[2] + tv3[2]) / 3)

	@staticmethod
	def doParticles(pos, maxSpeed, ppf, fnOutPos, fnOutVel):
		newPos = OpenMaya.MVector()
		newVel = OpenMaya.MVector()
		for i in range(0, ppf):
			newPos.x = pos[0]
			newPos.y = pos[1]
			newPos.z = pos[2]
			newVel.x = random.uniform(-maxSpeed, maxSpeed)
			newVel.y = random.uniform(-maxSpeed, maxSpeed)
			newVel.z = random.uniform(-maxSpeed, maxSpeed)
			fnOutPos.append(newPos)
			fnOutVel.append(newVel)


	def compute(self, plug, data):
		if plug == self.mOutput:
			# Get the logical index of the element this plug refers to,
			# because the node can be emitting particles into more
			# than one particle shape.
			multiIndex = plug.logicalIndex()
			hOutArray = data.outputArrayValue(self.mOutput)
			# Create a builder to aid in the array construction efficiently.
			bOutArray = hOutArray.builder()
			hOut = bOutArray.addElement(multiIndex)
			# Create the data
			fnOutput = OpenMaya.MFnArrayAttrsData()
			dOutput = fnOutput.create()
			# if full return
			fnOutPos = fnOutput.vectorArray("position")
			fnOutVel = fnOutput.vectorArray("velocity")
			# newPos = OpenMaya.MVector()
			# newVel = OpenMaya.MVector()
			# newVel.x = 5
			# fnOutPos.append(newPos)
			# fnOutVel.append(newVel)
			# newPos.x = 5
			# fnOutPos.append(newPos)
			# newVel.x = -5
			# fnOutVel.append(newVel)

			hTetFlags = data.inputValue(dmmEmitter.inTetFlags)
			tetFlagsData = OpenMaya.MFnIntArrayData(hTetFlags.data())
			tetFlagsArray = tetFlagsData.array()
			numTets = tetFlagsArray.length()

			# Current time
			cT = data.inputValue(self.mCurrentTime).asTime().value()

			# Start time
			mhValue = data.inputArrayValue(self.mStartTime)
			mhValue.jumpToElement(multiIndex)
			hValue = mhValue.inputValue()
			sT = hValue.asTime().value()

			# Delta time
			mhValue = data.inputArrayValue(self.mDeltaTime)
			mhValue.jumpToElement(multiIndex)
			hValue = mhValue.inputValue()
			dT = hValue.asTime().value()

			# Do not emit particles before the start time,
			# and do not emit particles when moving backwards in time.
			hLastTetFlags = data.inputValue(dmmEmitter.lastTetFlags)
			if (cT > sT) and (dT > 0.0) and (not hLastTetFlags.data().isNull()):
				lastTetFlagsData = OpenMaya.MFnIntArrayData(hLastTetFlags.data())
				lastTetFlagArray = lastTetFlagsData.array()
				if lastTetFlagArray.length() == tetFlagsArray.length():
					tetNodesArray = None
					for tet in xrange(0, numTets):
						visFaces = tetFlagsArray[tet]
						lastVisFaces = lastTetFlagArray[tet]
						if visFaces != lastVisFaces:
							if not tetNodesArray:
								hTetNodes = data.inputValue(dmmEmitter.inTetNodes)
								tetNodesData = OpenMaya.MFnDoubleArrayData(hTetNodes.data())
								tetNodesArray = tetNodesData.array()
								hSpeedRange = data.inputValue(dmmEmitter.speedRange)
								maxSpeed = hSpeedRange.asDouble()
								hPPF = data.inputValue(dmmEmitter.particlesPerFracture)
								ppf = hPPF.asDouble()
							for face in range(0, 3):
								if (visFaces % 2) != (lastVisFaces % 2):
									pos = dmmEmitter.getTetFaceCentroid(tetNodesArray, tet, face)
									dmmEmitter.doParticles(pos, maxSpeed, ppf, fnOutPos, fnOutVel)
								visFaces /= 2
								lastVisFaces /= 2

			lastTetFlagsData = OpenMaya.MFnIntArrayData()
			lastTetFlagsObject = lastTetFlagsData.create(tetFlagsArray)
			hLastTetFlags.setMObject(lastTetFlagsObject);

			hOut.setMObject(dOutput)
			data.setClean(plug)

		else:
			return OpenMaya.kUnknownParameter

def nodeCreator():
	return OpenMayaMPx.asMPxPtr(dmmEmitter())

def nodeInitializer():
	typedAttr = OpenMaya.MFnTypedAttribute()
	numAttr = OpenMaya.MFnNumericAttribute()

	dmmEmitter.inTetFlags = typedAttr.create("inTetFlags", "itf", OpenMaya.MFnData.kIntArray)
	dmmEmitter.inTetNodes = typedAttr.create("inTetNodes", "itn", OpenMaya.MFnData.kDoubleArray)
	dmmEmitter.lastTetFlags = typedAttr.create("lastTetFlags", "ltf", OpenMaya.MFnData.kIntArray)
	typedAttr.setStorable(False)
	dmmEmitter.speedRange = numAttr.create("speedRange", "sr", OpenMaya.MFnNumericData.kDouble)
	numAttr.setKeyable(True)
	numAttr.setMin(0)
	dmmEmitter.particlesPerFracture = numAttr.create("particlesPerFracture", "ppf", OpenMaya.MFnNumericData.kDouble)
	numAttr.setKeyable(True)
	numAttr.setMin(0)

	#attributeAffects
	dmmEmitter.addAttribute(dmmEmitter.inTetFlags)
	dmmEmitter.addAttribute(dmmEmitter.inTetNodes)
	dmmEmitter.addAttribute(dmmEmitter.lastTetFlags)
	dmmEmitter.addAttribute(dmmEmitter.speedRange)
	dmmEmitter.addAttribute(dmmEmitter.particlesPerFracture)

# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerNode(kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kEmitterNode)
	except:
		sys.stderr.write("Failed to register node: %s" % kPluginNodeName)
		raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode(kPluginNodeId)
	except:
		sys.stderr.write("Failed to deregister node: %s" % kPluginNodeName)
		raise