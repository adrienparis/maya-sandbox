#!/usr/bin/env python

"""miniToolRig.py: A little tool to help rigging character."""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.3.3-alpha"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
from datetime import date
import ctypes
import sys
import math
try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

# define the global local scale of the name object

class Callback():
    __author__ = "Adrien PARIS"
    __email__ = "a.paris.cs@gmail.com"
    __version__     = "3.1.0"
    __copyright__   = "Copyright 2021, Creative Seeds"
    
    def __init__(self, func, *args, **kwargs):
        '''Use for maya interface event, because it send you back your argument as strings
        func : the function you want to call
        *args : your arguments
        '''
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.repeatable_value = False
        self.getCommandArgument_value = False

    def repeatable(self):
        ''' Call this methode to make the function repeatable with 'g'
        '''
        self.repeatable_value = True
        return self

    def getCommandArgument(self):
        ''' Call this methode to receive the argument of the event
        '''
        self.getCommandArgument_value = True
        return self
        

    def __call__(self, cb_repeatLast=False, *args):

        ag = self.args + args if self.getCommandArgument_value else self.args

        if self.repeatable_value and not cb_repeatLast:
            import ctypes; print(ctypes.cast(id(self), ctypes.py_object).value)
            import __main__
            __main__.cb_repeatLast = self
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast(cb_repeatLast=True)"); ''')

        return self.func(*ag, **self.kwargs)

    
if __name__ == "__main__":
    ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "Info of {}".format(__file__), 0)


def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''   
    miniToolRigWin()
 

class RigTab():
    CONTRAINT = [cmds.parentConstraint, cmds.pointConstraint, cmds.orientConstraint, cmds.scaleConstraint, cmds.aimConstraint]

    def __init__(self, parent):
        self.parentLayout = parent
        self.UI_Layouts = {}
        self.UI_Controls = {}

        pass

    def load(self):
        # TMP creation
        fLayTMP = cmds.formLayout(p=self.parentLayout, bgc=[0.35, 0.4, 0.5])
        TMPtextField = cmds.textField(parent=fLayTMP)
        TMPcheckBox = cmds.checkBox(parent=fLayTMP, label="Sym")
        b = cmds.button(parent=fLayTMP, label="Create TMP", c=Callback(RigTab.createTMPs, TMPtextField, TMPcheckBox).repeatable())
        cmds.textField(TMPtextField, e=True, cc=Callback(RigTab.createTMPs, TMPtextField, TMPcheckBox).repeatable())

        cmds.formLayout(fLayTMP, e=True, af=[(b, "top", 0), (b, "right", 0), (TMPtextField, "top", 0), (TMPtextField, "left", 0), (TMPcheckBox, "top", 0)],
                                        ac=[(TMPtextField, "right", 0, TMPcheckBox), (TMPcheckBox, "right", 0, b)])

        # TMP reset
        cmds.button(parent=self.parentLayout, label="Reset TMPs", c=Callback(RigTab.resetTMP))

        # PLAN + ORIENT creation
        cmds.button(parent=self.parentLayout, label="Create PLAN", c=Callback(RigTab.createPLAN).repeatable())
        # Orientation by world
        cmds.optionMenu(parent=self.parentLayout, label='Secondary Axe', changeCommand=RigTab.orientPlanAxe )
        cmds.menuItem( label='X' )
        cmds.menuItem( label='Z' )
        worldAxeUpRdioGrp = cmds.radioButtonGrp(parent=self.parentLayout, sl=1, label='World ', labelArray3=['x', 'y', 'z'], numberOfRadioButtons=3, cc1=RigTab.orientPlanWordAxeX, cc2=RigTab.orientPlanWordAxeY, cc3=RigTab.orientPlanWordAxeZ)
        cmds.radioButtonGrp(parent=self.parentLayout, numberOfRadioButtons=3, shareCollection=worldAxeUpRdioGrp, label='', labelArray3=['-x', '-y', '-z'], cc1=RigTab.orientPlanWordAxemX, cc2=RigTab.orientPlanWordAxemY, cc3=RigTab.orientPlanWordAxemZ)
        cmds.button(parent=self.parentLayout, label="Orient PLAN", c=Callback(RigTab.orientPLAN).repeatable())

        # Orient one to the other in list
        cmds.button(parent=self.parentLayout, label="Orient inside", c=Callback(RigTab.orientInsidePLAN).repeatable())
        # Create joint on TMP
        cmds.button(parent=self.parentLayout, label="Create Joints", c=Callback(RigTab.createAllJoints))
        cmds.button(parent=self.parentLayout, label="Parent Joints", c=Callback(RigTab.parentJoints).repeatable())
        
        # Ori & Zero creation
        fLayOriZero = cmds.formLayout(p=self.parentLayout, bgc=[0.35, 0.4, 0.5])
        ffOri = cmds.floatField(p=fLayOriZero, pre=3, v=0)
        cmds.floatField(ffOri, e=True, ec=Callback(RigTab.generateAdditionalJoint, "Ori", ffOri).repeatable())
        bOri = cmds.button(p=fLayOriZero, label="Create Ori", en=True, c=Callback(RigTab.generateAdditionalJoint, "Ori", ffOri).repeatable())
        ffZero = cmds.floatField(p=fLayOriZero, pre=3, v=0.5)
        cmds.floatField(ffZero, e=True, ec=Callback(RigTab.generateAdditionalJoint, "0", ffZero).repeatable())
        bZero = cmds.button(p=fLayOriZero, label="Create 0", en=True, c=Callback(RigTab.generateAdditionalJoint, "0", ffZero).repeatable())
        cmds.formLayout(fLayOriZero, e=True, af=[(ffOri, "top", 1), (bOri, "top", 1),
                                                (ffOri, "left", 1), (ffZero, "left", 1),
                                                (bZero, "right", 1), (bOri, "right", 1),
                                                (ffZero, "bottom", 1), (bZero, "bottom", 1)],
                                            ap=[(bOri, "left", 0, 66), (bZero, "left", 0, 66),
                                                (ffOri, "right", 0, 66), (ffZero, "right", 0, 66)])



        cmds.button(parent=self.parentLayout, label="Create CTRLs from top sk", c=Callback(RigTab.createControllersHierarchy))
        cmds.button(parent=self.parentLayout, label="Create CTRLs from sk", c=Callback(RigTab.createControllers))
        cmds.button(parent=self.parentLayout, label="Transfert Ctrl's shape to side", c=Callback(RigTab.transfertCtrlShape))
        cmds.button(parent=self.parentLayout, label="connect CTRLs' scales (fingers)", c=Callback(RigTab.connectScaleCtrl))
        cmds.button(parent=self.parentLayout, label="Groupe CTRL", c=Callback(RigTab.grpCtrls))

        cmds.text(parent=self.parentLayout, label="Constraint")
        row = cmds.rowLayout(parent=self.parentLayout, numberOfColumns=5, bgc=[0.32, 0.52, 0.65])
        cmds.iconTextButton(parent=row, style="textOnly", label="Parent", c=Callback(RigTab.contraint, 0), dcc=Callback(cmds.ParentConstraintOptions).repeatable(), bgc=[0.37, 0.57, 0.7])
        cmds.iconTextButton(parent=row, style="textOnly", label="Point", c=Callback(RigTab.contraint, 1), dcc=Callback(cmds.PointConstraintOptions).repeatable(), bgc=[0.37, 0.57, 0.7])
        cmds.iconTextButton(parent=row, style="textOnly", label="Scale", c=Callback(RigTab.contraint, 3), dcc=Callback(cmds.ScaleConstraintOptions).repeatable(), bgc=[0.37, 0.57, 0.7])
        cmds.iconTextButton(parent=row, style="textOnly", label="Orient", c=Callback(RigTab.contraint, 2), dcc=Callback(cmds.OrientConstraintOptions).repeatable(), bgc=[0.37, 0.57, 0.7])
        cmds.iconTextButton(parent=row, style="textOnly", label="Aim", c=Callback(RigTab.contraint, 4), dcc=Callback(cmds.AimConstraintOptions).repeatable(), bgc=[0.37, 0.57, 0.7])


        # Hide/Unhide constraint
        cmds.button(parent=self.parentLayout, label="Hide constraint", c=Callback(RigTab.hideConstraints, True))
        cmds.button(parent=self.parentLayout, label="Unhide constraint", c=Callback(RigTab.hideConstraints, False))

        # Contrainte placement
        cmds.text(parent=self.parentLayout, label="Copy transform by constraint")
        row = cmds.rowLayout(parent=self.parentLayout, numberOfColumns=4, bgc=[0.32, 0.52, 0.65])
        cmds.button(parent=row, label="Parent", c=Callback(RigTab.contraintPlacement, 0).repeatable())
        cmds.button(parent=row, label="Point", c=Callback(RigTab.contraintPlacement, 1).repeatable())
        cmds.button(parent=row, label="Scale", c=Callback(RigTab.contraintPlacement, 3).repeatable())
        cmds.button(parent=row, label="Orient", c=Callback(RigTab.contraintPlacement, 2).repeatable())

        # freezing Transform
        cmds.text(parent=self.parentLayout, label="Freeze transforms")
        row = cmds.rowLayout(parent=self.parentLayout, numberOfColumns=3, bgc=[0.32, 0.52, 0.65])
        cmds.button(parent=row, label="Translate", c=Callback(RigTab.freezeTransform, t=True).repeatable())
        cmds.button(parent=row, label="Rotate", c=Callback(RigTab.freezeTransform, r=True).repeatable())
        cmds.button(parent=row, label="Scale", c=Callback(RigTab.freezeTransform, s=True).repeatable())

        # freezing Transform
        cmds.text(parent=self.parentLayout, label="Reset transforms")
        row = cmds.rowLayout(parent=self.parentLayout, numberOfColumns=3, bgc=[0.32, 0.52, 0.65])
        cmds.button(parent=row, label="Translate", c=Callback(RigTab.resetTransform, t=True).repeatable())
        cmds.button(parent=row, label="Rotate", c=Callback(RigTab.resetTransform, r=True).repeatable())
        cmds.button(parent=row, label="Scale", c=Callback(RigTab.resetTransform, s=True).repeatable())

        cmds.button(parent=self.parentLayout, label="Create ctrlsSet", c=Callback(RigTab.createCtrlSet))

        

        # Creating Nurb Spine
        self.UI_Layouts["LC_Spine"] = cmds.columnLayout(p=self.parentLayout, bgc=[0.28, 0.66, 0.70], adj=True)
        self.UI_Controls["LT_Spine"] = cmds.text(parent=self.UI_Layouts["LC_Spine"], label="Creation Nurb spine")

        self.UI_Layouts["LF_Up"] = cmds.formLayout(p=self.UI_Layouts["LC_Spine"])
        
        self.UI_Controls["LT_Up"] = cmds.text(parent=self.UI_Layouts["LF_Up"], label="Up")
        self.UI_Controls["LTF_Up"] = cmds.textField(parent=self.UI_Layouts["LF_Up"], ed=False)
        self.UI_Controls["LB_UpSet"] = cmds.button(p=self.UI_Layouts["LF_Up"], label="Set", en=True, c=Callback(self.setNurbsSel, "LTF_Up"))
        cmds.formLayout(self.UI_Layouts["LF_Up"], e=True, af=[(self.UI_Controls["LT_Up"], "top", 1), (self.UI_Controls["LT_Up"], "left", 1),
                                           (self.UI_Controls["LB_UpSet"], "top", 1), (self.UI_Controls["LB_UpSet"], "right", 1),
                                           (self.UI_Controls["LT_Up"], "top", 1)],
                                       ac=[(self.UI_Controls["LTF_Up"], "left", 1, self.UI_Controls["LT_Up"]), (self.UI_Controls["LTF_Up"], "right", 1, self.UI_Controls["LB_UpSet"])])
        self.UI_Controls["LF_Dn"] = cmds.formLayout(p=self.UI_Layouts["LC_Spine"])
        self.UI_Controls["LT_Dn"] = cmds.text(parent=self.UI_Controls["LF_Dn"], label="Down")
        self.UI_Controls["LTF_Dn"] = cmds.textField(parent=self.UI_Controls["LF_Dn"], ed=False)
        self.UI_Controls["LB_DnSet"] = cmds.button(p=self.UI_Controls["LF_Dn"], label="Set", en=True, c=Callback(self.setNurbsSel, "LTF_Dn"))
        cmds.formLayout(self.UI_Controls["LF_Dn"], e=True, af=[(self.UI_Controls["LT_Dn"], "top", 1), (self.UI_Controls["LT_Dn"], "left", 1),
                                           (self.UI_Controls["LB_DnSet"], "top", 1), (self.UI_Controls["LB_DnSet"], "right", 1),
                                           (self.UI_Controls["LTF_Dn"], "top", 1)],
                                       ac=[(self.UI_Controls["LTF_Dn"], "left", 1, self.UI_Controls["LT_Dn"]), (self.UI_Controls["LTF_Dn"], "right", 1, self.UI_Controls["LB_DnSet"])])
        

        self.UI_Layouts["LR_SpineName"] = cmds.rowLayout(parent=self.UI_Layouts["LC_Spine"], numberOfColumns=2, bgc=[0.3, 0.5, 0.6], ad1=True, ad2=True)
        self.UI_Controls["LT_SpineName"] = cmds.text(parent=self.UI_Layouts["LR_SpineName"], label="Name")
        self.UI_Controls["LTF_SpineName"] = cmds.textField(parent=self.UI_Layouts["LR_SpineName"], tx="spine")

        self.UI_Layouts["LR_SpineNbDisc"] = cmds.rowLayout(parent=self.UI_Layouts["LC_Spine"], numberOfColumns=2, bgc=[0.31, 0.51, 0.61], ad1=True, ad2=True)
        self.UI_Controls["LT_SpineNbDisc"] = cmds.text(parent=self.UI_Layouts["LR_SpineNbDisc"], label="Nb")
        self.UI_Controls["LIF_SpineNbDisc"] = cmds.intField(parent=self.UI_Layouts["LR_SpineNbDisc"], v = 3)

        LB_CreateNurbs = cmds.button(p=self.UI_Layouts["LC_Spine"], label="Create Nurbs", en=True, c=Callback(self.CreateNurbSpine))
        LB_CreateJointCtrls = cmds.button(p=self.UI_Layouts["LC_Spine"], label="Create Joints", en=True, c=Callback(self.CreateNurbSpineGrpCtrls))



    # define the global local scale of the name object
    @staticmethod
    def setLocalScale(name, size):
        size = float('%.3f'%(size))
        cmds.setAttr(name + ".localScaleX", size)
        cmds.setAttr(name + ".localScaleY", size)
        cmds.setAttr(name + ".localScaleZ", size)

    #Will open a textbox asking for a name. If the action is canceled, it will return [None]
    @staticmethod
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
    
    @staticmethod
    def getSide(center):
        if center[0] > 0.0000001:
            return "_L"
        elif center[0] < -0.0000001:
            return "_R"
        return ""

    @staticmethod
    def getColor(name):
        if name[-2:] == "_L":
            return 13
        elif name[-2:] == "_R":
            return 6
        else:
            return 17

    @staticmethod
    def createLocator(name, pos=[0,0,0], size=1):
        name = cmds.spaceLocator(r=True, p=[0,0,0], n=name)[0]
        cmds.move(pos[0], pos[1], pos[2], name, a=True)
        RigTab.setLocalScale(name, size * 0.6)
        cmds.setAttr(name + ".overrideEnabled",1)
        cmds.setAttr(name + ".overrideColor", RigTab.getColor(name))

    @staticmethod
    def createTMPs(TMPtextField, TMPcheckBox, *_):
        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            cmds.error("No selection")
        # sel = sel[0]
        bb = cmds.exactWorldBoundingBox(sel)
        gap =  [abs(bb[i + 3] - bb[i]) for i in range(len(bb) / 2)]
        center = [bb[i] + gap[i] / 2 for i in range(len(gap))]
        size = max(gap) / 2

        
        name = "TMP_" + cmds.textField(TMPtextField, q=True, text=True)
        if name == "TMP_":
            name = RigTab.createTmpName()
        if cmds.checkBox(TMPcheckBox, q=True, v=True):
            cL = center[:]
            cR = [center[0] * -1] + center[1:]
            L = name + RigTab.getSide(cL)
            R = name + RigTab.getSide(cR)
            RigTab.createLocator(L, pos=cL, size=size)
            RigTab.createLocator(R, pos=cR, size=size)
        else:
            RigTab.createLocator(name, pos=center, size=max(size,0.1))

        cmds.textField(TMPtextField, e=True, text="")
        cmds.select(sel)
        if "[" in sel:
            cmds.selectMode(co=True)


    @staticmethod
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

    @staticmethod
    def setLocalScale(name, size):
        size = float('%.3f'%(size))
        cmds.setAttr(name + ".localScaleX", size)
        cmds.setAttr(name + ".localScaleY", size)
        cmds.setAttr(name + ".localScaleZ", size)

    #Create plan and orient

    @staticmethod
    def createPLAN(*_):
        sel = cmds.ls(sl=True)
        for s in sel:
            n = RigTab.prompt(s)
            plan = "PLAN_" + n + s[-2:]
            orient = "ORIENT_" + n + s[-2:]
            print(orient, plan)
            cmds.duplicate(s, n=plan)
            cmds.duplicate(s, n=orient)
            cmds.parent(orient, plan)
            cmds.parent(s, orient)


    worldUpAxe = [[1,0,0],[-1,0,0]]
    upAxe = [1,0,0]

    @staticmethod
    def orientPlanAxe(item):
        global upAxe
        if item == "X":
            upAxe = [1,0,0]
        elif item == "Z":
            upAxe = [0,0,1]

    @staticmethod
    def orientPlanWordAxeX( item ):
            global worldUpAxe
            worldUpAxe = [[1,0,0],[-1,0,0]]
    @staticmethod
    def orientPlanWordAxeY( item):
            global worldUpAxe
            worldUpAxe = [[0,1,0],[0,-1,0]]
    @staticmethod
    def orientPlanWordAxeZ( item ):
            global worldUpAxe
            worldUpAxe = [[0,0,1],[0,0,-1]]
    @staticmethod
    def orientPlanWordAxemX( item ):
            global worldUpAxe
            worldUpAxe = [[-1,0,0],[1,0,0]]
    @staticmethod
    def orientPlanWordAxemY( item):
            global worldUpAxe
            worldUpAxe = [[0,-1,0],[0,1,0]]
    @staticmethod
    def orientPlanWordAxemZ( item ):
            global worldUpAxe
            worldUpAxe = [[0,0,-1],[0,0,1]]

    #orient plan to wrist/ankle
    @staticmethod
    def orientPLAN(*_):
        sel = cmds.ls(sl=True)
        for i in range(0, len(sel) - 1):
            print(upAxe, worldUpAxe)
            if sel[i].endswith("_L"):
                print("left")
                todelete = cmds.aimConstraint(sel[i], sel[i + 1], aim=[0,1,0], u=upAxe, wu=worldUpAxe[0])
            else:
                print("right")
                todelete = cmds.aimConstraint(sel[i], sel[i + 1], aim=[0,-1,0], u=upAxe, wu=worldUpAxe[1])
            cmds.delete(todelete)
        
    #Orient with up
    @staticmethod
    def orientInsidePLAN(*_):
        sel = cmds.ls(sl=True)
        for i in range(0, len(sel) - 1):
            orient = cmds.listRelatives(sel[i], p=True)
            if orient != None:
                orient = orient[0]
            up = "U" + sel[i][2:]
            direction = -1 if sel[i].endswith("_R") else 1
            todelete = cmds.aimConstraint(sel[i + 1], sel[i], aim=[0,direction,0], u=[1,0,0], wu=[1,0,0], wut="objectrotation", wuo=orient)
            cmds.delete(todelete)
            #cmds.setAttr(sel[i] + ".rx", 0)
            #cmds.setAttr(sel[i] + ".ry", 0)
        cmds.parent(sel[i + 1], sel[i])
        cmds.setAttr(sel[i + 1] + ".rx", 0)
        cmds.setAttr(sel[i + 1] + ".ry", 0)
        cmds.setAttr(sel[i + 1] + ".rz", 0)
        orient = cmds.listRelatives(sel[i], p=True)[0]
        cmds.parent(sel[i + 1], orient)
        
    @staticmethod
    def resetTMP(*_):
        sel = cmds.ls(sl=True)
        for s in sel:
            try:
                cmds.parent(s, world=True)
            except:
                print("lol " + s)
        for s in sel:
            cmds.setAttr(s + ".rx", 0)
            cmds.setAttr(s + ".ry", 0)
            cmds.setAttr(s + ".rz", 0)
            if s.startswith("TMP_"):
                continue
            cmds.delete(s)

    @staticmethod
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

    @staticmethod
    def parentJoints(*_):
        sel = cmds.ls(sl=True)[::-1]
        p = sel.pop(0)
        while sel:
            s = sel.pop(0)
            cmds.parent(p, s)
            print("{} -> {}".format(p, s))
            p = s


    # joint Ori Zero
    @staticmethod
    def createZero(joint, value):
            sideGap = -0.001 if joint.endswith("_R") else 0.001

            l = len(joint) - 2 if joint.endswith("_L") or joint.endswith("_R") else len(joint)
            i = "_0" if joint[l - 1].isnumeric() else "0"
            name0 = joint[:l] + i + joint[l:]
            if cmds.objExists(name0):
                cmds.warning("The additional joint [{}] already exist".format(name0))
                return
            
            cmds.duplicate(joint, n=name0, po=True)
            
            p = cmds.listRelatives(joint, p=True)
            if p is None or p == []:
                return
            try:
                cmds.parent(name0, joint)
            except:
                print("lol " + joint)

            cmds.setAttr(name0 + ".tz", sideGap)
            
            cmds.parent(name0, p)
            cmds.pointConstraint( joint, name0, mo=True)[0]

            cmds.setAttr(name0 + ".visibility", False)
            cmds.setAttr(name0 + ".rotateOrder", cmds.getAttr(joint + ".rotateOrder"))
            nameMd = name0.replace("sk_","md_")
            cmds.createNode("multiplyDivide", name=nameMd)

            cmds.connectAttr(joint + ".rotate", nameMd + ".input1")
            cmds.connectAttr(nameMd + ".output", name0 + ".rotate")

            cmds.setAttr(nameMd + ".input2X", 0.5)
            cmds.setAttr(nameMd + ".input2Y", value)
            cmds.setAttr(nameMd + ".input2Z", 0.5)

    @staticmethod
    def createOri(joint, value):
            sideGap = 0.001 if joint.endswith("_R") else -0.001
            
            l = len(joint) - 2 if (joint.endswith("_L") or joint.endswith("_R")) else len(joint)
            nameOri = joint[:l] + 'Ori' + joint[l:]
            if cmds.objExists(nameOri):
                cmds.warning("The additional joint [{}] already exist".format(nameOri))
                return
            
            cmds.duplicate(joint, n=nameOri, po=True)


            p = cmds.listRelatives(joint, p=True)
            if p is None or p == []:
                return
            try:
                cmds.parent(nameOri, joint)
            except:
                print("lol " + joint)

            cmds.setAttr(nameOri + ".tz", sideGap)
            cmds.parent(nameOri, p)
            cmds.pointConstraint( joint, nameOri, mo=True)[0]
            
            
            cmds.setAttr(nameOri + ".visibility", False)
            cmds.setAttr(nameOri + ".rotateOrder", cmds.getAttr(joint + ".rotateOrder"))
            nameMd = nameOri.replace("sk_","md_")
            cmds.createNode("multiplyDivide", name=nameMd)

            cmds.connectAttr(joint + ".rotate", nameMd + ".input1")
            cmds.connectAttr(nameMd + ".output", nameOri + ".rotate")

            cmds.setAttr(nameMd + ".input2X", 0)
            cmds.setAttr(nameMd + ".input2Y", value)
            cmds.setAttr(nameMd + ".input2Z", 0)
    
    @staticmethod
    def generateAdditionalJoint(type_, ff):
        sl = cmds.ls(sl=True)
        v = float(cmds.floatField(ff, q=True, v=True))
        if v == None:
            return
        for s in sl:
            if type_ == "0":
                RigTab.createZero(s, v)
            elif type_ == "Ori":
                RigTab.createOri(s, v)
        cmds.select(sl)

    # Create pma connection between c_FK scale and sk_ scale
    # works on fingers
    @staticmethod
    def connectScaleCtrl(*_):
        sel = cmds.ls(sl=True)
        switch = [x for x in sel if "switch" in x]
        switch = switch[0] if len(switch) == 1 else None
        for ctrl in sel:
            if not ctrl.startswith("c_"):
                continue
            skin = ctrl.replace("c_FK_", "sk_")
            skin_wds = skin.split("_")
            zero = "_0" if skin[-3].isnumeric() else "0"
            skin0 = "_".join([skin_wds[0], skin_wds[1] + zero] + skin_wds[2:])
            skinOri = "_".join([skin_wds[0], skin_wds[1] + "Ori"] + skin_wds[2:])
            ik = skin.replace("sk_", "ik_")

            pSkin = cmds.listRelatives(skin, p=True)[0]
            if cmds.objExists(skin):
                if cmds.listConnections(skin + ".scale", d=False, s=True) is None:
                    if cmds.objExists(ik):
                        node = cmds.createNode("blendColors", n=skin0.replace("sk_", "bc_scale_"))
                        cmds.connectAttr(ctrl + ".scale", node + ".color0")
                        cmds.connectAttr(ik + ".scale", node + ".color1")
                        cmds.connectAttr(node + ".output", skin + ".scale")
                    else:
                        cmds.connectAttr(ctrl + ".scale", skin + ".scale")
                prev = pSkin
                if cmds.objExists(skinOri):
                    cmds.connectAttr(skin + ".scale", skinOri + ".scale")
                    prev = skinOri
                if cmds.objExists(skin0):
                    node = cmds.createNode("plusMinusAverage", n=skin0.replace("sk_", "pma_scale_"))
                    cmds.setAttr(node + ".operation", 3)
                    cmds.connectAttr(skin + ".scale", node + ".input3D[0]")
                    cmds.connectAttr(prev + ".scale", node + ".input3D[1]")
                    cmds.connectAttr(node + ".output3D", skin0 + ".scale")

    @staticmethod
    def transfertCtrlShape():        
        sel = cmds.ls(sl=True)
        for s in sel:
            if s.endswith("_L"):
                other = s.replace("_L", "_R")
            elif s.endswith("_L"):
                other = s.replace("_L", "_R")
            else:
                continue
            if other in sel:
                continue
            
            d = cmds.duplicate(s)[0]    
            cmds.parent(d, w=True)
            g = cmds.group(d)
            cmds.setAttr(g + ".sx", -1)
            cmds.parent(d, other)
            cmds.delete(g)
            
            cmds.setAttr(d + ".tx", 0)
            cmds.setAttr(d + ".ty", 0)
            cmds.setAttr(d + ".tz", 0)
            cmds.makeIdentity(d, apply=True, s=1, r=1)
            shape = cmds.listRelatives(d, c=True)
            otherShape = cmds.listRelatives(other, c=True)
            cmds.parent(shape, other, r=True, s=True)
            cmds.delete(otherShape)
            shapeNameOrigin = cmds.listRelatives(s, c=True)[0]
            if "_L" in shapeNameOrigin:
                newName = shapeNameOrigin.replace("_L", "_R")
            elif "_R" in shapeNameOrigin:
                newName = shapeNameOrigin.replace("_R", "_L")
            cmds.rename(shape, newName)
            otherShape = cmds.listRelatives(other, c=True)
            for os in otherShape:
                cmds.setAttr(os + ".ihi", 0)

    @staticmethod
    def createAllJoints(*_):
        objects = cmds.ls(type="transform", sl=True)

        for obj in objects:
            if obj.startswith("TMP_"):
                if obj[-1] == "L":
                    RigTab.setJoint(obj)
        for obj in objects:
            if obj.startswith("TMP_"):
                if obj[-1] == "R":
                    RigTab.setJoint(obj)

        for obj in objects:
            if obj.startswith("pose_") or obj.startswith("TMP_"):
                if not (obj[-1] == "R" or obj[-1] == "L"):
                    RigTab.setJoint(obj)

    @staticmethod
    def goDownJointsHierachy(name, function, filterJump=None, filterStop=None, type_=[], *args, **kwargs):
        if filterStop is not None and filterStop(name):
            return
        _childrens = cmds.listRelatives(name, type=type_)
        if filterJump is None or not filterJump(name):
            function(name, *args, **kwargs)
        if _childrens is None:
            return
        for child in _childrens:
            RigTab.goDownJointsHierachy(child, function, filterJump, filterStop, type_=type_, *args, **kwargs)

    @staticmethod
    def createControllersHierarchy(*_):
        ctrls = cmds.ls(sl=True)

        for sk in ctrls:
            RigTab.goDownJointsHierachy(sk, RigTab.createControllerFromSK, filterStop = lambda a : "End" in a, type_="joint")

    @staticmethod
    def createControllers(*_):
        ctrls = cmds.ls(sl=True)

        for sk in ctrls:
            RigTab.createControllerFromSK(sk)

    @staticmethod
    def createControllerFromSK(sk, constraint=0):
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
        print(cmds.getAttr(sk + ".rotateOrder"), sk)
        cmds.setAttr("c_FK_" + ctrl + ".rotateOrder", cmds.getAttr(sk + ".rotateOrder"))
        #rescale
        size = cmds.getAttr(sk + '.radius') * 3
        # cmds.rotate(0, 0, 90, "c_FK_" + ctrl)
        cmds.scale(size, size, size, "c_FK_" + ctrl)
        cmds.makeIdentity("c_FK_" + ctrl, apply=True, s=1)
        cmds.delete("c_FK_" + ctrl, constructionHistory = True)
        #create hierachy
        cmds.group("c_FK_" + ctrl, n="pose_FK_" + ctrl)
        cmds.group("pose_FK_" + ctrl, n="inf_FK_" + ctrl)
        cmds.group("inf_FK_" + ctrl, n="root_FK_" + ctrl)
        
        cmds.setAttr("pose_FK_" + ctrl + ".rotateOrder", cmds.getAttr(sk + ".rotateOrder"))
        cmds.setAttr("inf_FK_" + ctrl + ".rotateOrder", cmds.getAttr(sk + ".rotateOrder"))
        cmds.setAttr("root_FK_" + ctrl + ".rotateOrder", cmds.getAttr(sk + ".rotateOrder"))


        #place to right coordinates
        toBeDelete = RigTab.CONTRAINT[constraint](sk, "root_FK_" + ctrl, n="toBeDelete")
        cmds.delete(toBeDelete)
        parent = cmds.listRelatives(sk, parent=True)
        if parent is None:
            return
        if not cmds.objExists(parent[0].replace("sk_", "c_FK_")):
            return None
        cmds.parentConstraint(parent[0].replace("sk_", "c_FK_"), "inf_FK_" + ctrl,mo=True)
        cmds.parentConstraint("c_FK_" + ctrl, sk, mo=True)

    @staticmethod
    def printFunc(p):
        print(p)

    @staticmethod
    def grpCtrls():
        ctrls = cmds.ls(sl=True)
        for c in ctrls:
            if not c.startswith("c_"):
                name = RigTab.prompt(c).replace(" ", "_")
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

    @staticmethod
    def createStarCtrl(name, pointed=8):
        nb = max(3,pointed) * 2
        
        ctrl = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=360, r=1, d=3, ut=0, tol=0.01, s=nb, ch=1, n=name)[0]
        vtx = ["{}.cv[{}]".format(ctrl, x) for x in range(0, nb, 2)]
        cmds.scale(0.0988827, 0.0988827, 0.0988827, *vtx, r=True, ocp=True)
        cmds.delete(ctrl, constructionHistory = True)
        return ctrl


    @staticmethod
    def contraintPlacement(con=0, *_):
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
            RigTab.CONTRAINT[con](parent, c, n="toBeDelete")
            cmds.delete("toBeDelete")

    @staticmethod
    def contraint(con=0, *_):
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
            RigTab.CONTRAINT[con](parent, c, mo=True)


    @staticmethod
    def freezeTransform(t=False, r=False, s=False, *_):
        cmds.makeIdentity(apply=True, t=t, r=r, s=s)


    @staticmethod
    def resetTransform(t=False, r=False, s=False):
        for s in cmds.ls(sl=True):
            if t:
                cmds.setAttr(s + ".tx", 0)
                cmds.setAttr(s + ".ty", 0)
                cmds.setAttr(s + ".tz", 0)
            if r:
                cmds.setAttr(s + ".rx", 0)
                cmds.setAttr(s + ".ry", 0)
                cmds.setAttr(s + ".rz", 0)
            if s:
                cmds.setAttr(s + ".sx", 1)
                cmds.setAttr(s + ".sy", 1)
                cmds.setAttr(s + ".sz", 1)



    @staticmethod
    def createCtrlSet(*_):
        sl = cmds.ls(sl=True)
        if len(sl) >= 1:
            for s in sl:
                if s == "CTRLS":
                    cmds.sets(RigTab.createCtrlSetRec(sl[0]),  n="ctrlsSet")
                else:
                    RigTab.createCtrlSetRec(s)
        else:
            cmds.warning("Please select at least one group")

    @staticmethod
    def createCtrlSetRec(parent):
        child = cmds.listRelatives(parent)
        if child is None:
            return None
        ctrls = []
        for c in child:
            if c is not None and not c.endswith("Shape"):
                ret = RigTab.createCtrlSetRec(c)
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

    @staticmethod
    def selectHierarchyByType(node, t):
        if cmds.objectType(node, isType=t):
            cmds.select(node, add=True)
        child = cmds.listRelatives(node)
        if child == None:
            return
        for c in child:
            RigTab.selectHierarchyByType(c, t)

    @staticmethod
    def hideConstraints(v, *_):
        sel = cmds.ls()[:]
        cmds.select(cl=True)
        
        for s in sel:
            if s.split(':')[-1].startswith("sk_"):
                RigTab.selectHierarchyByType(s, "parentConstraint")
                RigTab.selectHierarchyByType(s, "pointConstraint")

        mel.eval("doHideInOutliner {};".format(int(v)))
        cmds.select(cl=True)

    def setNurbsSel(self, t):
        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            return
        cmds.textField(self.UI_Controls[t], e=True, tx=str(sel[0]))

    def CreateNurbSpine(self):
        
        name = cmds.textField(self.UI_Controls["LTF_SpineName"], q=True, tx=True)
        up = cmds.textField(self.UI_Controls["LTF_Up"], q=True, tx=True)
        dn = cmds.textField(self.UI_Controls["LTF_Dn"], q=True, tx=True)
        nb_disc = cmds.intField(self.UI_Controls["LIF_SpineNbDisc"], q=True, v=True) + 1
        nurb = "nrb_" + name

        n = cmds.nurbsPlane(p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=1, u=1, v=1, ch=1, n=nurb)[0]

        t_p = cmds.xform(up,q=1,ws=1,rp=1)
        d_p = cmds.xform(dn,q=1,ws=1,rp=1)

        cmds.move(0, 0, -0.5, n + ".cv[0:1][0]",r=True, os=True, ws=True)
        cmds.move(0, 0, 0.5, n + ".cv[0:1][1]",r=True, os=True, ws=True)
        cmds.move(d_p[0], d_p[1], d_p[2], n + ".cv[0:1][0]",r=True, os=True, ws=True)
        cmds.move(t_p[0], t_p[1], t_p[2], n + ".cv[0:1][1]",r=True, os=True, ws=True)

        cmds.rebuildSurface(n, sv=nb_disc, su=1, dv=3, du=1)

    
    def CreateNurbSpineGrpCtrls(self):

        name = cmds.textField(self.UI_Controls["LTF_SpineName"], q=True, tx=True)
        nurb = "nrb_" + name
        nb_disc = cmds.intField(self.UI_Controls["LIF_SpineNbDisc"], q=True, v=True) + 2

        # Create and Place Grps
        discs = []
        for i in range(1, nb_disc + 1):
            inf_grp  = cmds.group(em=True, n="inf_{}{}".format(name, i))
            pose_grp = cmds.group(em=True, n="pose_{}{}".format(name, i))
            up_grp = cmds.group(em=True, n="up_{}{}".format(name, i))
            discs.append((inf_grp, pose_grp, up_grp))
            cmds.parent(pose_grp, inf_grp)
            
            posi = cmds.createNode("pointOnSurfaceInfo", n="posi_{}{}".format(name, i))
            posi_up = cmds.createNode("pointOnSurfaceInfo", n="posi_up_{}{}".format(name, i))
            
            #TODO find nurb shape
            cmds.connectAttr("{}Shape.worldSpace[0]".format(nurb), "{}.inputSurface".format(posi))
            cmds.connectAttr("{}Shape.worldSpace[0]".format(nurb), "{}.inputSurface".format(posi_up))
            
            cmds.connectAttr("{}.position".format(posi), "{}.translate".format(inf_grp))
            cmds.connectAttr("{}.position".format(posi_up), "{}.translate".format(up_grp))
            perct = 1.0/(nb_disc - 1) * (i - 1)
            print(perct)
            cmds.setAttr("{}.u".format(posi), 0.5)
            cmds.setAttr("{}.v".format(posi), perct)
            cmds.setAttr("{}.u".format(posi_up), 1)
            cmds.setAttr("{}.v".format(posi_up), perct)
        
        tmp = discs[:]
        
        # Orient Grps
        f = tmp.pop()
        while tmp:
            print(tmp)
            c = tmp[-1]
            print(f[1], c[0])
            cmds.aimConstraint(f[1], c[0], u=[1, 0, 0], aim=[0, 1, 0], wut="object", wuo=c[2])
            f = tmp.pop()

        # Ranger
        folder = cmds.group(em=True, n="grp_{}_noScale".format(name))
        i = 1
        jntP = None
        for g in discs[:]:
            cmds.parent(g[0], folder)
            cmds.parent(g[2], folder)
            jnt = cmds.joint(g[1], n="sk_{}{}".format(name, i))
            if jntP is not None:
                cmds.parent(jnt, jntP)
            else:
                cmds.parent(jnt, w=True)
            jntP= jnt
            i += 1
        
        # Creation des CTRLS
        # RigTab.goDownJointsHierachy("sk_{}1".format(name), RigTab.createControllerFromSK, filterStop = lambda a : "End" in a, type_="joint", constraint=1)






   
def defModTab(parentTab):
    def mirrorCut(*_):
        sel = cmds.ls(sl=True)

        for s in sel:
            s = s.split(".")[0]
            l = cmds.polyEvaluate(s, f=True)
            f_ro_delete = []
            for i in range(0, l):
                f = "{}.f[{}]".format(s, i)
                bbs = cmds.exactWorldBoundingBox(f)
                if bbs[0] <= 0.001 and bbs[3] <= 0.001:
                    f_ro_delete.append(f)
            cmds.delete(f_ro_delete)
            cmds.delete(s, constructionHistory = True)

    def mirror(*_):
        sel = cmds.ls(sl=True)

        for s in sel:
            s = s.split(".")[0]
            cmds.polyMirrorFace(s, cutMesh=1, axis=0, axisDirection=1, mergeMode=1, mergeThresholdType=1, mergeThreshold=0.001, mirrorAxis=2, mirrorPosition=0, smoothingAngle=30, flipUVs=0, ch=1)
            cmds.delete(s, constructionHistory = True)

    def relax(reflexion=False, *_):
        cmds.selectMode( co=True )
        cmds.selectMode( object=True )
        cmds.SculptGeometryTool()
        cmds.artPuttyCtx('artPuttyContext', e=True, mtm='relax', op=0.1, rn=reflexion)

    def edgeSlide(itb, *_):
        t = cmds.xformConstraint(query=True, type=True)
        if t == "edge":
            cmds.xformConstraint(type="none")
            cmds.iconTextButton(itb, e=True, ebg=False)
        else:
            cmds.xformConstraint(type="edge")
            cmds.iconTextButton(itb, e=True, ebg=True)

    def symMod(itb, *_):
        t = cmds.symmetricModelling(query=True, symmetry=True)
        if t == 1:
            cmds.symmetricModelling(symmetry=0, ps=0)
            cmds.iconTextButton(itb, e=True, ebg=False)
        else:
            cmds.symmetricModelling(symmetry=1, ps=0)
            cmds.iconTextButton(itb, e=True, ebg=True)


    mirrorLay = cmds.rowColumnLayout(p=parentTab, numberOfColumns=2)

    cmds.iconTextButton(i="polyMirrorGeometry", p=mirrorLay, c=Callback(mirror), h=40)
    cmds.iconTextButton(i="polyMirrorCut", p=mirrorLay, c=Callback(mirrorCut), h=40)
    itb = cmds.iconTextButton(i="polyMoveVertex", p=parentTab, bgc=[0.32, 0.52, 0.65], ebg=False)
    cmds.iconTextButton(itb, e=True, c=Callback(symMod, itb))
    if cmds.symmetricModelling(query=True, symmetry=True) == 1:
        cmds.iconTextButton(itb, e=True, ebg=True)

    itb = cmds.iconTextButton(i="NEX_pickDrag", p=parentTab, bgc=[0.32, 0.52, 0.65], ebg=False, h=40)
    cmds.iconTextButton(itb, e=True, c=Callback(edgeSlide, itb))
    if cmds.xformConstraint(query=True, type=True) == "edge":
        cmds.iconTextButton(itb, e=True, ebg=True)

    cmds.iconTextButton(i="putty", p=parentTab, c=Callback(relax), dcc=Callback(relax, True), h=40)
    cmds.iconTextButton(i="polyMerge", p=parentTab, en=False, h=40)
    cmds.iconTextButton(i="Relax", p=parentTab, en=False, h=40)

def defSnapTab(parentTab):
    class ImgName():
        i = 0
        def __call__(self, name):
            self.i += 1
            return '{:02}_{}'.format(self.i, name)

    def switch_light(on=True):
        currentPanel = cmds.getPanel(withFocus=True)

        if cmds.getPanel(to=currentPanel) == "modelPanel":
            if on:
                cmds.modelEditor(currentPanel, e=True, dl="default")
            else:
                cmds.modelEditor(currentPanel, e=True, dl="none")

    def zoom(v):
        currentPanel = cmds.getPanel(withFocus=True)

        if cmds.getPanel(to=currentPanel) == "modelPanel":
            curCamera=cmds.modelEditor(currentPanel,q=1,av=1,cam=1)
            cmds.xform(curCamera, rt=[0, 0, v], r=True, os=True)

    def fit():
        if cmds.ls("GEO"):
            cmds.select(cmds.ls("GEO"), r=True)
        else:
            cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)
        cmds.viewFit()
        cmds.select(cl=True)

    def isolateSelected(state):
        viewport = cmds.getPanel( withFocus = True)
        if cmds.ls("GEO"):
            cmds.select(cmds.ls("GEO"), r=True)
        else:
            cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)
        if 'modelPanel' in viewport:
            if state:
                cmds.isolateSelect( viewport, addSelected=True )
                cmds.isolateSelect( viewport, s=True )
                cmds.isolateSelect( viewport, addSelected=True )
                cmds.isolateSelect( viewport, s=True )
            else:
                cmds.isolateSelect( viewport, s=False )
        cmds.select(cl=True)

    def wireframe_switcher(state=None):
        viewport = cmds.getPanel( withFocus = True)
        if 'modelPanel' in viewport:
            
            currentState = cmds.modelEditor( viewport, q = True, wireframeOnShaded = True) if state == None else not state
            if currentState:
                cmds.modelEditor( viewport, edit = True, wireframeOnShaded = False)
            else:
                cmds.modelEditor( viewport, edit = True, wireframeOnShaded = True)

    def TakeAllSnapShot(*_):
        In = ImgName()
        today = date.today()
        ws = cmds.workspace( q=True, rootDirectory=True )
        current_date = today.strftime("%Y%m%d")
        file_path_abs = cmds.file(q=True, sn=True)
        file_path_rlt = file_path_abs.replace(ws, "")
        asset_name = file_path_rlt.split("/")[-1].split("_")[1]
        print(asset_name)
        full_path = "/".join([ws, "images", "dailyScreenShot", asset_name, current_date])
        print(full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)


        def take_screenShot(name, width=1920, height=1080):
            img_path = "/".join([full_path, name + ".jpg"])
            cmds.playblast(fr=0, v=False, fmt="image", c="jpg", orn=False, cf=img_path, wh=[width,height], p=100)


        old_sl = cmds.ls(sl=True)
        current_view = cmds.lookThru(q=True)
        cmds.lookThru('persp')
        isolateSelected(True)

        # fit()
        # zoom(-20)
        wireframe_switcher(False)
        switch_light(True)

        take_screenShot(In("default"))

        switch_light(False)
        take_screenShot(In("shadow"))
        switch_light(True)

        wireframe_switcher(True)
        take_screenShot(In("wireframe"))
        wireframe_switcher(False)

        # zoom(20)

        cmds.lookThru('front')
        fit()
        # cmds.dolly( 'front', os=0.6666 )
        take_screenShot(In("front"))
        # cmds.dolly( 'front', os=1.5 )
        cmds.hotkey( 'z', query=True, alt=True )

        cmds.lookThru('side')
        fit()

        # cmds.dolly( 'side', os=0.6666 )
        take_screenShot(In("side"))
        cmds.hotkey( 'z', query=True, alt=True )

        # cmds.dolly( 'side', os=1.5 )
        cmds.lookThru(current_view)
        cmds.select(old_sl)
        isolateSelected(False)



    cmds.iconTextButton(i="rvExposureControlIcon", p=parentTab, c=Callback(TakeAllSnapShot))

def miniToolRigWin():
    name = u"Mini-Tool-Rig " + __version__
    if cmds.workspaceControl(name, exists=1):
        cmds.deleteUI(name)
    win = cmds.workspaceControl(name, ih=100, iw=150, retain=False, floating=True)
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    t_mod = cmds.columnLayout("Mod", p=tabs, adj=True)
    t_rig = cmds.columnLayout("Rig", p=tabs, adj=True)
    t_snapshot = cmds.columnLayout("Snapshot", p=tabs, adj=True)

    defModTab(t_mod)
    RigTab(t_rig).load()
    defSnapTab(t_snapshot)
    
