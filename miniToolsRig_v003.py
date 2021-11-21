#!/usr/bin/env python

"""miniToolRig.py: A little tool to help rigging character."""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.1rc1.dev1"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
import math
import maya.cmds as cmds
import maya.mel as mel
from pymel.all import *
# define the global local scale of the name object


__cbFuncNum_miniToolRig = 0
__cbFunc_miniToolRig = {}
def Callback_miniToolRig(func, *args, **kwargs):
    global __cbFuncNum_miniToolRig
    global __cbFunc_miniToolRig
    if callable(func):
        __cbFuncNum_miniToolRig += 1
        __cbFunc_miniToolRig[__cbFuncNum_miniToolRig - 1] = [func, args, kwargs]
        return "Callback_miniToolRig(" + str(__cbFuncNum_miniToolRig)  + ")"
    __cbFunc_miniToolRig[func - 1][0](*__cbFunc_miniToolRig[func - 1][1], **__cbFunc_miniToolRig[func - 1][2])

# define the global local scale of the name object
def setLocalScale(name, size):
    size = float('%.3f'%(size))
    cmds.setAttr(name + ".localScaleX", size)
    cmds.setAttr(name + ".localScaleY", size)
    cmds.setAttr(name + ".localScaleZ", size)

#Will open a textbox asking for a name. If the action is canceled, it will return [None]
def createTmpName():
    name = "TMP_"

    result = cmds.promptDialog(
                    title='Name the articulation',
                    message='Enter name:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')
    if result == 'OK':
        name += cmds.promptDialog(query=True, text=True)
    else:
        return None
    return name

def getSide(center):
    if center[0] > 0.0000001:
        return "_L"
    elif center[0] < -0.0000001:
        return "_R"
    return ""

def getColor(name):
    if name[-2:] == "_L":
        return 13
    elif name[-2:] == "_R":
        return 6
    else:
        return 17

def createLocator(name, pos=[0,0,0], size=1):
    name = cmds.spaceLocator(r=True, p=[0,0,0], n=name)[0]
    cmds.move(pos[0], pos[1], pos[2], name, a=True)
    setLocalScale(name, size * 0.6)
    cmds.setAttr(name + ".overrideEnabled",1)
    cmds.setAttr(name + ".overrideColor", getColor(name))

def createTMPs(TMPtextField, TMPcheckBox):
    sel = cmds.ls(sl=True)
    if len(sel) == 0:
        cmds.error("No selection")
    sel = sel[0]
    bb = cmds.exactWorldBoundingBox(sel)
    gap =  [abs(bb[i + 3] - bb[i]) for i in range(len(bb) / 2)]
    center = [bb[i] + gap[i] / 2 for i in range(len(gap))]
    size = max(gap) / 2

    
    name = "TMP_" + cmds.textField(TMPtextField, q=True, text=True)
    if name == "TMP_":
        name = createTmpName()
    if cmds.checkBox(TMPcheckBox, q=True, v=True):
        cL = center[:]
        cR = [center[0] * -1] + center[1:]
        L = name + getSide(cL)
        R = name + getSide(cR)
        createLocator(L, pos=cL, size=size)
        createLocator(R, pos=cR, size=size)
    else:
        createLocator(name, pos=center, size=max(size,0.1))

    cmds.textField(TMPtextField, e=True, text="")
    cmds.select(sel)
    if "[" in sel:
        cmds.selectMode(co=True)
    try:
        cmds.repeatLast(ac='''python("createTMPs('{}', '{}')")'''.format(TMPtextField, TMPcheckBox))
    except:
        return






def prompt(name):
    result = cmds.promptDialog(
                    title='Name the PLAN/ORIENT',
                    message='Enter name [' + name + ']:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')
    if result == 'OK':
        return cmds.promptDialog(query=True, text=True)
    else:
        return None

def setLocalScale(name, size):
    size = float('%.3f'%(size))
    cmds.setAttr(name + ".localScaleX", size)
    cmds.setAttr(name + ".localScaleY", size)
    cmds.setAttr(name + ".localScaleZ", size)

#Create plan and orient

def createPLAN():
    sel = cmds.ls(sl=True)
    for s in sel:
        n = prompt(s)
        plan = "PLAN_" + n + s[-2:]
        orient = "ORIENT_" + n + s[-2:]
        print(orient, plan)
        cmds.duplicate(s, n=plan)
        cmds.duplicate(s, n=orient)
        cmds.parent(orient, plan)
        cmds.parent(s, orient)


worldUpAxe = [[1,0,0],[-1,0,0]]
upAxe = [1,0,0]

def orientPlanAxe(item):
    global upAxe
    if item == "X":
        upAxe = [1,0,0]
    elif item == "Z":
        upAxe = [0,0,1]

def orientPlanWordAxeX( item ):
        global worldUpAxe
        worldUpAxe = [[1,0,0],[-1,0,0]]
def orientPlanWordAxeY( item):
        global worldUpAxe
        worldUpAxe = [[0,1,0],[0,-1,0]]
def orientPlanWordAxeZ( item ):
        global worldUpAxe
        worldUpAxe = [[0,0,1],[0,0,-1]]
def orientPlanWordAxemX( item ):
        global worldUpAxe
        worldUpAxe = [[-1,0,0],[1,0,0]]
def orientPlanWordAxemY( item):
        global worldUpAxe
        worldUpAxe = [[0,-1,0],[0,1,0]]
def orientPlanWordAxemZ( item ):
        global worldUpAxe
        worldUpAxe = [[0,0,-1],[0,0,1]]

#orient plan to wrist/ankle
def orientPLAN():
    sel = cmds.ls(sl=True)
    for i in range(0, len(sel) - 1):
        print(upAxe, worldUpAxe)
        if sel[i].endswith("_L"):
            print("left")
            todelete = cmds.aimConstraint(sel[i + 1], sel[i], aim=[0,1,0], u=upAxe, wu=worldUpAxe[0])
        else:
            print("right")
            todelete = cmds.aimConstraint(sel[i + 1], sel[i], aim=[0,-1,0], u=upAxe, wu=worldUpAxe[1])
        cmds.delete(todelete)
    
#Orient with up
def orientInsidePLAN():
    sel = cmds.ls(sl=True)
    for i in range(0, len(sel) - 1):
        orient = cmds.listRelatives(sel[i], p=True)[0]
        up = "U" + sel[i][2:]
        if sel[i].endswith("_L"):
            todelete = cmds.aimConstraint(sel[i + 1], sel[i], aim=[0,1,0], u=[1,0,0], wu=[1,0,0], wut="objectrotation", wuo=orient)
        else:
            todelete = cmds.aimConstraint(sel[i + 1], sel[i], aim=[0,-1,0], u=[1,0,0], wu=[1,0,0], wut="objectrotation", wuo=orient)
        cmds.delete(todelete)
        #cmds.setAttr(sel[i] + ".rx", 0)
        #cmds.setAttr(sel[i] + ".ry", 0)
    cmds.parent(sel[i + 1], sel[i])
    cmds.setAttr(sel[i + 1] + ".rx", 0)
    cmds.setAttr(sel[i + 1] + ".ry", 0)
    cmds.setAttr(sel[i + 1] + ".rz", 0)
    orient = cmds.listRelatives(sel[i], p=True)[0]
    cmds.parent(sel[i + 1], orient)
    
def resetTMP():
    sel = cmds.ls(sl=True)
    for s in sel:
        try:
            cmds.parent(s, world=True)
        except:
            print("lol")
    for s in sel:
        cmds.setAttr(s + ".rx", 0)
        cmds.setAttr(s + ".ry", 0)
        cmds.setAttr(s + ".rz", 0)
        if s.startswith("TMP_"):
            continue
        cmds.delete(s)

def setJoint(obj):
    pos = cmds.xform(obj, q=True, t=True, ws=True)    
    rot = cmds.xform(obj, q=True, ro=True, ws=True)    
    cmds.select(clear=True)
#	cmds.joint(p=pos[0:3])
    #tx = cmds.getAttr(obj + '.translateX')
    #ty = cmds.getAttr(obj + '.translateY')
    #tz = cmds.getAttr(obj + '.translateZ')
    rx = cmds.getAttr(obj + '.rotateX')
    ry = cmds.getAttr(obj + '.rotateY')
    rz = cmds.getAttr(obj + '.rotateZ')
    size = cmds.getAttr(obj + '.localScaleZ') * 1.2
    print(obj + " " + "%.30f" %pos[0] + " " + "%.30f" %pos[1] + " " + "%.30f" %pos[2] + " " + "%.15f" %rx + " " + "%.15f" %ry + " " + "%.15f" %rz)
    cmds.joint(p=pos[0:3], orientation=rot[0:3], name=obj.replace("TMP_", "sk_").replace("pose_", "sk_"), radius=size)


def createAllJoints():
    objects = cmds.ls(type="transform", sl=True)

    for obj in objects:
        if obj.startswith("TMP_"):
            if obj[-1] == "L":
                setJoint(obj)
    for obj in objects:
        if obj.startswith("TMP_"):
            if obj[-1] == "R":
                setJoint(obj)

    for obj in objects:
        if obj.startswith("pose_") or obj.startswith("TMP_"):
            if not (obj[-1] == "R" or obj[-1] == "L"):
                setJoint(obj)

def goDownJointsHierachy(name, function, filterJump=None, filterStop=None, type_=[]):
    if filterStop is not None and filterStop(name):
        return
    _childrens = cmds.listRelatives(name, type=type_)
    if filterJump is None or not filterJump(name):
        function(name)
    if _childrens is None:
        return
    for child in _childrens:
        goDownJointsHierachy(child, function, filterJump, filterStop, type_=type_)

def createControllersHierarchy():
    ctrls = cmds.ls(sl=True)

    for sk in ctrls:
        goDownJointsHierachy(sk, createControllerFromSK, filterStop = lambda a : "End" in a, type_="joint")

def createControllerFromSK(sk):
    if not cmds.getAttr(sk + ".v"):
        return
    #get name
    ctrl = sk.replace("sk_", "")
    #create controller
    cmds.circle(n="c_FK_" + ctrl, nr=[0,1,0], s=16)
    #set color
    print("c_FK_" + ctrl + ".overrideEnabled")
    cmds.setAttr("c_FK_" + ctrl + ".overrideEnabled", 1)
    cmds.setAttr("c_FK_" + ctrl + ".overrideColor", 13 if sk.endswith("_L") else 6 if sk.endswith("_R") else 17)
    #rescale
    size = cmds.getAttr(sk + '.radius') * 3
    # cmds.rotate(0, 0, 90, "c_FK_" + ctrl)
    cmds.scale(size, size, size, "c_FK_" + ctrl)
    cmds.makeIdentity("c_FK_" + ctrl, apply=True, s=1)
    #create hierachy
    cmds.group("c_FK_" + ctrl, n="pose_FK_" + ctrl)
    cmds.group("pose_FK_" + ctrl, n="inf_FK_" + ctrl)
    cmds.group("inf_FK_" + ctrl, n="root_FK_" + ctrl)
    #place to right coordinates
    cmds.parentConstraint(sk, "root_FK_" + ctrl, n="toBeDelete")
    cmds.delete("toBeDelete")
    parent = cmds.listRelatives(sk, parent=True)
    if parent is None:
        return
    if not cmds.objExists(parent[0].replace("sk_", "c_FK_")):
        return None
    cmds.parentConstraint(parent[0].replace("sk_", "c_FK_"), "inf_FK_" + ctrl,mo=True)
    cmds.parentConstraint("c_FK_" + ctrl, sk, mo=True)


def printFunc(p):
    print(p)

def grpCtrls():
    print(cmds)
    ctrls = cmds.ls(sl=True)
    for c in ctrls:
        if not c.startswith("c_"):
            name = prompt(c).replace(" ", "_")
        else:
            name = c.replace("c_", "")
        cmds.rename(c, "c_" + name)
        cmds.group(em=True, n="pose_" + name, a=True)
        cmds.parent("c_" + name, "pose_" + name)
        cmds.group(em=True, n="inf_" + name, a=True)
        cmds.parent("pose_" + name, "inf_" + name)
        cmds.group(em=True, n="root_" + name, a=True)
        cmds.parent("inf_" + name, "root_" + name)
        cmds.setAttr("c_" + name + ".overrideEnabled",1)
        cmds.setAttr("c_" + name + ".overrideColor", 13 if name.endswith("_L") else 6 if name.endswith("_R") else 17)


CONTRAINT = [cmds.parentConstraint, cmds.pointConstraint, cmds.orientConstraint, cmds.scaleConstraint]
def contraintPlacement(con=0):
    '''con: 0 -> parent constraint
    con: 1 -> point constraint
    con: 2 -> orient constraint
    con: 3 -> scale constraint
    '''
    ctrls = cmds.ls(sl=True)
    if len(ctrls) < 2:
        return
    parent = ctrls.pop(0)
    for c in ctrls:
        CONTRAINT[con](parent, c, n="toBeDelete")
        cmds.delete("toBeDelete")
    try:
        cmds.repeatLast(ac='''python("contraintPlacement(''' + str(con) + ''')")''')
    except:
        return

def contraint(con=0):
    '''con: 0 -> parent constraint
    con: 1 -> point constraint
    con: 2 -> orient constraint
    con: 3 -> scale constraint
    '''
    ctrls = cmds.ls(sl=True)
    if len(ctrls) < 2:
        return
    parent = ctrls.pop(0)
    for c in ctrls:
        CONTRAINT[con](parent, c, mo=True)
    try:
        cmds.repeatLast(ac='''python("contraint(''' + str(con) + ''')")''')
    except:
        return

def createCtrlSet():
    sl = cmds.ls(sl=True)
    if len(sl) >= 1:
        for s in sl:
            if s == "CTRLS":
                cmds.sets(createCtrlSetRec(sl[0]),  n="ctrlsSet")
            else:
                createCtrlSetRec(s)
    else:
        cmds.warning("Please select at least one group")

def createCtrlSetRec(parent):
    child = cmds.listRelatives(parent)
    if child is None:
        return None
    ctrls = []
    for c in child:
        if c is not None and not c.endswith("Shape"):
            ret = createCtrlSetRec(c)
            if ret is not None:
                ctrls += ret
        if c.startswith("c_"):
            return [c]
    if parent.startswith("grp_"):
        grpName = parent.replace("grp_", "")
        grpNameWs = grpName.split("_")
        grpNameWs = [x[0].upper() + x[1:] for x in grpNameWs]
        if grpNameWs[0] == "IK" or grpNameWs[0] == "FK":
            grpNameWs[0], grpNameWs[1] = grpNameWs[1], grpNameWs[0]
        grpNameWs[0] = grpNameWs[0].lower()
        grpName = "".join(grpNameWs)
        return([cmds.sets(ctrls,  n=grpName)])
    return ctrls


def miniToolRigWin():
    name = u"Mini-Tool-Rig"
    if cmds.workspaceControl(name, exists=1):
        cmds.deleteUI(name)
    win = cmds.workspaceControl(name, ih=100, iw=150, retain=False, floating=True)
    fLayTMP = cmds.formLayout(p=win)
    TMPtextField = cmds.textField(parent=fLayTMP)
    TMPcheckBox = cmds.checkBox(parent=fLayTMP, label="Sym")
    b = cmds.button(parent=fLayTMP, label="Create TMP", c=Callback(createTMPs, TMPtextField, TMPcheckBox))
    cmds.textField(TMPtextField, e=True, ec=Callback(createTMPs, TMPtextField, TMPcheckBox))

    cmds.formLayout(fLayTMP, e=True, af=[(b, "top", 0), (b, "right", 0), (TMPtextField, "top", 0), (TMPtextField, "left", 0), (TMPcheckBox, "top", 0)],
                                     ac=[(TMPtextField, "right", 0, TMPcheckBox), (TMPcheckBox, "right", 0, b)])

    cmds.button(parent=win, label="Reset TMPs", c=Callback_miniToolRig(resetTMP))

    cmds.button(parent=win, label="Create PLAN", c=Callback_miniToolRig(createPLAN))
    cmds.optionMenu(parent=win, label='Secondary Axe', changeCommand=orientPlanAxe )
    cmds.menuItem( label='X' )
    cmds.menuItem( label='Z' )
    worldAxeUpRdioGrp = cmds.radioButtonGrp(parent=win, sl=1, label='World ', labelArray3=['x', 'y', 'z'], numberOfRadioButtons=3, cc1=orientPlanWordAxeX, cc2=orientPlanWordAxeY, cc3=orientPlanWordAxeZ)
    cmds.radioButtonGrp(parent=win, numberOfRadioButtons=3, shareCollection=worldAxeUpRdioGrp, label='', labelArray3=['-x', '-y', '-z'], cc1=orientPlanWordAxemX, cc2=orientPlanWordAxemY, cc3=orientPlanWordAxemZ)
    cmds.button(parent=win, label="Orient PLAN", c=Callback_miniToolRig(orientPLAN))

    cmds.button(parent=win, label="Orient inside", c=Callback_miniToolRig(orientInsidePLAN))
    cmds.button(parent=win, label="Create Joints", c=Callback_miniToolRig(createAllJoints))
    cmds.button(parent=win, label="Create CTRLs from sk", c=Callback_miniToolRig(createControllersHierarchy))
    cmds.button(parent=win, label="Groupe CTRL", c=Callback_miniToolRig(grpCtrls))
    cmds.text(parent=win, label="Contrainte")
    row = cmds.rowLayout(parent=win, numberOfColumns=4, bgc=[0.32, 0.52, 0.65])
    cmds.button(parent=row, label="Parent", c=Callback_miniToolRig(contraint, 0))
    cmds.button(parent=row, label="Point", c=Callback_miniToolRig(contraint, 1))
    cmds.button(parent=row, label="Scale", c=Callback_miniToolRig(contraint, 3))
    cmds.button(parent=row, label="Orient", c=Callback_miniToolRig(contraint, 2))
    cmds.text(parent=win, label="Contrainte placement")
    row = cmds.rowLayout(parent=win, numberOfColumns=4, bgc=[0.32, 0.52, 0.65])
    cmds.button(parent=row, label="Parent", c=Callback_miniToolRig(contraintPlacement, 0))
    cmds.button(parent=row, label="Point", c=Callback_miniToolRig(contraintPlacement, 1))
    cmds.button(parent=row, label="Scale", c=Callback_miniToolRig(contraintPlacement, 3))
    cmds.button(parent=row, label="Orient", c=Callback_miniToolRig(contraintPlacement, 2))
    cmds.button(parent=win, label="Create ctrlsSet", c=Callback_miniToolRig(createCtrlSet))

def onMayaDroppedPythonFile(*args):
    current_path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    sys.path.append(current_path)
    cmd = '''string $cmd = "from ''' + __name__ + ''' import *"; python($cmd);'''
    mel.eval(cmd)
    miniToolRigWin()


if __name__ == "__main__":
    miniToolRigWin()