from maya import cmds

ctrl = "MASTER_BS_Node_cnt"
attr = "eyeBlinkRight"
attr = "eyeWideRight"

for s in cmds.ls(sl=True):
    
    for axe in ["rx", "ry", "rz"]:
        cmds.setDrivenKeyframe(s + "." + axe, cd=ctrl + "." + attr, itt="linear", ott="linear")
        
cmds.setAttr(ctrl + "." + attr, 0)

for s in cmds.ls(sl=True):
    for axe in ["rx", "ry", "rz"]:
        cmds.setAttr(s + "." + axe, 0)
    for axe in ["rx", "ry", "rz"]:
        cmds.setDrivenKeyframe(s + "." + axe, cd=ctrl + "." + attr, itt="linear", ott="linear")
#===================

for s in cmds.ls(sl=True):
    for axe in ["rx", "ry", "rz"]:
        sign = 1 - 2 * (axe != "rx")
        cmds.setAttr(s + "." + axe, cmds.getAttr(s.replace("_R", "_L") + "." + axe) * sign)