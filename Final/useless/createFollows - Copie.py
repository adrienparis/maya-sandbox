import maya.cmds as cmds
from pymel.all import Callback

CONSTRAINT = ["parentConstraint", "pointConstraint"]

def addListTarget(l):
    global targets
    for s in l:
        if s.startswith("c_"):
            print(s.split("_", 1)[-1].lower().replace("ik_", "").replace("fk_", ""))
            if len(targets) == 0:
                cmds.text(parent=targetElems, label=s, bgc=[1,0,0])
            else:
                cmds.text(parent=targetElems, label=s)
            targets.append(s)

def addTarget():
    global targets
    sel = cmds.ls(sl=True)
    addListTarget(sel)
def clearTarget():
    global targets
    targets = []
    delChildLayout(targetElems)
    
    
def resetTarget():
    delChildLayout(targetElems)
    addListTarget(["c_FLY", "c_FK_head", "c_IK_chest", "c_IK_pelvis", "c_WORLD"])
            
def delChildLayout(lay):
    childrens = cmds.layout(lay, q=True, ca=True)
    if childrens is None:
        return
    for c in childrens:
        cmds.deleteUI(c)

def addCtrl():
    global ctrls
    sel = cmds.ls(sl=True)
    for s in sel:
        if s.startswith("c_"):
            ctrls.append(s)
            cmds.text(parent=ctrlElems, label=s)
def clearCtrl():
    global ctrls
    ctrls = []
    delChildLayout(ctrlElems)

def getInfParent(e):
    p = cmds.listRelatives(e, p=True)
    if p is None or len(p) < 1:
        return None
    if p[0].startswith("inf_"):
        return p[0]
    return getInfParent(p[0])

def removeTarget(ctrl, target):
    pass

def createMainTarget(ctrl, target, const=0):
    pass

def addTargets(ctrl, targets, const=0):
    pass

def applyFollows(const):
    for c in ctrls:
        print(c)
        inf = getInfParent(c)
        if inf is None:
            continue
        cmds.addAttr(c, longName='parent', attributeType='enum', en=" ", k=True)
        print(targets)
        for i, t in enumerate([t for t in targets if cmds.objExists(t)]):
            #
            #TODO do something if it's a target Right or Left ctrl
            if t.endswith("_L") or t.endswith("_R"):
                name = t.split("_")[-2]
            else:
                name = t.split("_")[-1]
            tName = inf.replace("inf_", "tgt_") + "_" + name
            name = name.lower()
            Wname = tName + "W" + str(i)
            #dupliquer les infs renomer par tName
            cmds.duplicate(inf, n=tName, parentOnly=True)
            #t contrainte maintain offset tName
            getattr(cmds, CONSTRAINT[const])(t, tName, mo=True)
            getattr(cmds, CONSTRAINT[const])(tName, inf, mo=True)
            # si c'est le premier controller
            if i == 0:
                # creation de la reverseroot
                cmds.addAttr(inf + "_" + CONSTRAINT[const] + "1", longName='reverseroot', defaultValue=0.0, k=True)
                # drive and key
                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 0)
                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1."  + Wname, 1)
                cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1." + Wname, cd=inf + "_" + CONSTRAINT[const] + "1.reverseroot")

                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 1)
                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1."  + Wname, 0)
                cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1." + Wname, cd=inf + "_" + CONSTRAINT[const] + "1.reverseroot")
            
            else:
                print(c + '.follow' + name.capitalize())
                cmds.addAttr(c, longName='follow' + name.capitalize(), defaultValue=0, minValue=0, maxValue=1, k=True)
                
                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1." + Wname, 1)
                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 1)
                cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1.reverseroot", cd=inf + "_" + CONSTRAINT[const] + "1." + Wname)

                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1." + Wname, 0)
                cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 0)
                cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1.reverseroot", cd=inf + "_" + CONSTRAINT[const] + "1." + Wname)
                cmds.connectAttr( c + '.follow' + name.capitalize(), inf + "_" + CONSTRAINT[const] + "1." + Wname)
                # reinitialisation de precaution 
                print(c + '.follow' + name.capitalize())
                cmds.setAttr(c + '.follow' + name.capitalize(), 1)
                cmds.setAttr(c + '.follow' + name.capitalize(), 0)

targets = []
ctrls = []

#Create window
name = u"Creation de follow"
if cmds.workspaceControl(name, exists=1):
    cmds.deleteUI(name)
win = cmds.workspaceControl(name, ih=100, iw=300, retain=False, floating=True)
mainForm = cmds.columnLayout(parent=win, columnAttach=('left',0), rowSpacing=10, adj=1)

targetForm = cmds.formLayout(parent=mainForm, bgc=[0.45,0.45,0.45])
ctrlForm = cmds.formLayout(parent=mainForm, bgc=[0.45,0.45,0.45])

#targetForm
tl = cmds.text(parent=targetForm, label="targets : ")
targetButtons = cmds.columnLayout(parent=targetForm, bgc=[0.4,0.4,0.4], columnAttach=('both', 5), rowSpacing=5)
targetElems = cmds.columnLayout(parent=targetForm, bgc=[0.5,0.5,0.5], columnAttach=('left', 5), rowSpacing=5)
cmds.button(parent=targetButtons, label="add", c=Callback(addTarget))
cmds.button(parent=targetButtons, label="reset", c=Callback(resetTarget))
cmds.button(parent=targetButtons, label="clear", c=Callback(clearTarget))
resetTarget()
cmds.formLayout(targetForm, e=True, 
                attachForm=[(tl, "top", 5), (tl, "left", 5),
                            (targetElems, "left", 5), (targetButtons, "right", 5)],
                attachControl=[(targetElems, "top", 5, tl),(targetElems, "right", 5, targetButtons),
                               (targetButtons, "top", 5, tl)],
                attachNone=[(targetButtons, "bottom"), (targetButtons, "left")])

# ctrlForm
cl = cmds.text(parent=ctrlForm, label="controls : ")
ctrlButtons = cmds.columnLayout(parent=ctrlForm, bgc=[0.4,0.4,0.4], columnAttach=('both', 5), rowSpacing=5)
ctrlElems = cmds.columnLayout(parent=ctrlForm, bgc=[0.5,0.5,0.5], columnAttach=('left', 5), rowSpacing=5)
cmds.button(parent=ctrlButtons, label="add", c=Callback(addCtrl))
cmds.button(parent=ctrlButtons, label="clear", c=Callback(clearCtrl))
for t in ctrls:
    cmds.text(parent=ctrlElems, label=t)
cmds.formLayout(ctrlForm, e=True, 
                attachForm=[(cl, "top", 5), (cl, "left", 5),
                            (ctrlElems, "left", 5), (ctrlButtons, "right", 5)],
                attachControl=[(ctrlElems, "top", 5, cl),(ctrlElems, "right", 5, ctrlButtons),
                               (ctrlButtons, "top", 5, cl)],
                attachNone=[(ctrlButtons, "bottom"), (ctrlButtons, "left")])
#apply form
al = cmds.text(parent=mainForm, label="Apply by", align='left')
applyButtonsRow = cmds.rowLayout(parent=mainForm, numberOfColumns=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'left', 0)])
cmds.button(parent=applyButtonsRow, label="parent", c=Callback(applyFollows, 0))
cmds.button(parent=applyButtonsRow, label="point", c=Callback(applyFollows, 1))