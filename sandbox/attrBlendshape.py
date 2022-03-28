import maya.cmds as cmds
import random

blendShapes = ["mStretch", "mNarrow", "mSmile", "mSad", "mLiftUpUp", "mLiftUpDn", "mLiftDnUp", "mLiftDnDn","mSlide",
               "mLipInUp", "mLipInDn", "mLipOutUp", "mLipOutDn", "mGruntUp", "mGruntDn", "cPuffOut", "cPuffOutLips", "cPuffIn"]
for bs in blendShapes:
    r = (random.randrange(1,1000) ** 2) / 100000
    for side in ("L", "R"):
        if side == "R" and random.randrange(1,3) != 1:
            r = (random.randrange(1,1000) ** 2) / 100000
        try:
            cmds.setAttr("c_faceDn." + bs + side, r)
        except:
            print("no " + bs + " atribute")

blendShapes = ["ebUp", "ebDn", "ebAngry", "ebSad", "ebSqueeze"]

for bs in blendShapes:
    for side in ("L", "R"):
        r = (random.randrange(1,1000) ** 2) / 100000
        try:
            cmds.setAttr("c_faceUp." + bs + side, r)
        except:
            print("no " + bs + " atribute")