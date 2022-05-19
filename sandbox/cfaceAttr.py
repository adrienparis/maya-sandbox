from maya import cmds

def createAttr(ctrl, name):
    cmds.addAttr(ctrl, longName=name + 'L', defaultValue=0, minValue=0, maxValue=10, k=True)
    cmds.addAttr(ctrl, longName=name + 'R', defaultValue=0, minValue=0, maxValue=10, k=True)


c = "c_faceDn"
# cmds.addAttr(c, longName='mPinch', attributeType='enum', en=" : ", k=True)
# createAttr(c, "mPinch")
# createAttr(c, "mPinchMid")

cmds.addAttr(c, longName='mBasic', attributeType='enum', en=" : ", k=True)
createAttr(c, "mNarrow")
createAttr(c, "mSmile")
createAttr(c, "mStretch")
createAttr(c, "mSad")

cmds.addAttr(c, longName='mLiftAndSlide', attributeType='enum', en=" : ", k=True)
createAttr(c, "mLiftUpUp")
createAttr(c, "mLiftUpDn")
createAttr(c, "mLiftDnUp")
createAttr(c, "mLiftDnDn")
createAttr(c, "mSlide")

cmds.addAttr(c, longName='mLipInAndOut', attributeType='enum', en=" : ", k=True)
createAttr(c, "mLipInUp")
createAttr(c, "mLipInDn")
createAttr(c, "mLipOutUp")
createAttr(c, "mLipOutDn")

cmds.addAttr(c, longName='mGrunt', attributeType='enum', en=" : ", k=True)
createAttr(c, "mGruntUp")
createAttr(c, "mGruntDn")

# cmds.addAttr(c, longName='mBackAndForeward', attributeType='enum', en=" : ", k=True)
# createAttr(c, "mStretchL")

cmds.addAttr(c, longName='cPuffInandOut', attributeType='enum', en=" : ", k=True)
createAttr(c, "cPuffOut")
createAttr(c, "cPuffOutLips")
createAttr(c, "cPuffIn")

c = "c_faceUp"
createAttr(c, "ebUp")
createAttr(c, "ebDn")
createAttr(c, "ebAngry")
createAttr(c, "ebSad")
createAttr(c, "ebSqueeze")


mesh = "msh_body"
ctrlUp = "c_faceUp"
ctrlDn = "c_faceDn"
history = cmds.listHistory(mesh)        
blendshapes = cmds.ls(history, type='blendShape')

weights = cmds.listAttr(blendshapes[0] + '.w' , m=True)
for i, w in enumerate(weights):
	attr = w.replace("_","")
	print(attr, w)
	md = cmds.createNode("multiplyDivide", n="md_{}".format(w))
	ctrl = ctrlUp if attr in cmds.listAttr(ctrlUp) else ctrlDn
	cmds.setAttr("{}.input2X".format(md), 0.1)
	if attr not in cmds.listAttr(ctrl):
		continue
	cmds.connectAttr("{}.{}".format(ctrl, attr), "{}.input1X".format(md))
	cmds.connectAttr("{}.outputX".format(md), "{}.{}".format(blendshapes[0], w))
	