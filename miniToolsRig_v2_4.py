#!/usr/bin/env python
# -- coding: utf-8 --

"""miniToolRig.py: A little tool-box to help rigging character."""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "2.4.9-BETA"
__copyright__   = "Copyright 2021, Creative Seeds"

import ctypes
import getpass
import os
import sys
from math import *
import webbrowser
import inspect
import datetime
import urllib

try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

class Callback():
    '''Use for maya interface event, because it send you back your argument as strings
    func : the function you want to call
    *args : your arguments
    **kwargs : your keywords arguments

    Example:
    cmds.button(c=Callback(myFunc, arg1, arg2))
    cmds.button(c=Callback(myFunc, arg1, arg2).repeatable())
    '''
    __author__ = "Adrien PARIS"
    __email__ = "a.paris.cs@gmail.com"
    __version__     = "3.1.0"
    __copyright__   = "Copyright 2021, Creative Seeds"
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.repeatArgs = args
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
        
    def _repeatCall(self):
        return self.func(*self.repeatArgs, **self.kwargs)

    def __call__(self, *args):
        ag = self.args + args if self.getCommandArgument_value else self.args
        if self.repeatable_value:
            import __main__
            __main__.cb_repeatLast = self
            self.repeatArgs = ag
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast._repeatCall()"); ''')
        return self.func(*ag, **self.kwargs)

class Module(object):
    '''Little bloc to encapsulate the UI's maya's system
    The parent must be either a Module, either a string that has the name of a maya's layout
    (cmds.layout, cmds.formLayout, cmds.columnLayout, ...)

    When converting this object to str, it print the layout to store his childrens
    like that, even if whe call it has a parent, it still return a maya's layout
    
    You must create a load function.
    
    Name your class starting by
    M_  if it's a simple module
    MG_ if it's a group of module
    MT_ if it's for a specific tools
    MC_ if it's for a control
    MGT_ if it's a group that contain tools
    '''
    BLUE = [0.32, 0.52, 0.65]
    TURQUOISE = [0.28, 0.66, 0.70]
    ORANGE = [0.86, 0.58, 0.34]

    increment = 0
    drag = None

    def __init__(self, parent, name=None):
        
        if name is None:
            name = self.__class__.__name__ + str(Module.increment)
            Module.increment += 1
        self.name = name
        self.childrens = []
        self.parent = None
        self.setParent(parent)
        self.command = {}
        self._scriptJobIndex = []
        self.childrenLayout = None
        self.layout = None
        self.bgc = None
        self.bgc = False
        self.dragged = False
        self.af = []
        self.ac = []
        self.ap = []

    def __str__(self):
        return str(self.childrenLayout)

    def __getattribute__(self, name):
        if name == 'load':
            return object.__getattribute__(self, "_load")
        if name == "height":
            return cmds.layout(self.layout, q=True, h=True)
        if name == "width":
            return cmds.layout(self.layout, q=True, w=True)
        return object.__getattribute__(self, name)

    def setParent(self, parent):
        if self.parent is not None:
            if isinstance(self.parent, Module):
                self.parent.childrens.remove(self)
        self.parent = parent
        if isinstance(self.parent, Module):
            self.parent.childrens.append(self)

    def attach(self, elem, top=None, bottom=None, left=None, right=None, margin=(0,0,0,0)):
        '''For formLayout
            Register the attach information of your elem 
            attach "FORM": string
                    elem : layout/control
                    pos : float
                    None
            return elem
            Use applyAttach() to attach the layout to your parent
        '''
        if isinstance(elem, Module):
            e = elem.layout
        else:
            e = elem
        for s, n, m in [(top, "top", margin[0]), (bottom, "bottom", margin[1]), (left, "left", margin[2]), (right, "right", margin[3])]: 
            if s == None:
                continue
            if isinstance(s, (str, unicode)):
                if s.upper() == "FORM":
                    self.af.append((e, n, m))
                else:
                    self.ac.append((e, n, m, s))
            if isinstance(s, Module):
                self.ac.append((e, n, m, s.layout))
            if isinstance(s, (float, int)):
                self.ap.append((e, n, m, float(s)))
        return elem

    def clearAttach(self):
        self.af = []
        self.ac = []
        self.ap = []
    
    @staticmethod
    def _getParentLayout(attachList):
        parLayout = {}
        for af in attachList:
            e = af[0]
            if isinstance(e, Module):
                parLayout[e.parent] = [af] if e.parent not in parLayout else parLayout[e.parent] + [af]
            else:
                if cmds.layout(e, exists=True):
                    parent = cmds.layout(e, q=True, p=True)
                elif cmds.control(e, exists=True):
                    parent = cmds.control(e, q=True, p=True)
                else:
                    continue
                parLayout[parent] = [af] if parent not in parLayout else parLayout[parent] + [af] 
        return parLayout

    def applyAttach(self):
        parLayoutAf = Module._getParentLayout(self.af)
        parLayoutAc = Module._getParentLayout(self.ac)
        parLayoutAp = Module._getParentLayout(self.ap)
        parentlayouts = parLayoutAf.keys() + parLayoutAc.keys() + parLayoutAp.keys()
        parentlayouts = list(dict.fromkeys(parentlayouts))
        for pl in parentlayouts:
            af = parLayoutAf[pl] if pl in parLayoutAf else []
            ac = parLayoutAc[pl] if pl in parLayoutAc else []
            ap = parLayoutAp[pl] if pl in parLayoutAp else []
            cmds.formLayout(pl, e=True, af=af, ac=ac, ap=ap)

    def _load(self):
        object.__getattribute__(self, "load")()
        return self

    def load(self):
        ''' Put your main layout in the self.layout
        If you use a formeLayout use self.attach()
        Put the layout where the childrens will go in self.childrenLayout
        '''
        raise Exception('load function not implemented')

    def reload(self):
        self.unload()
        self.load()

    def unload(self):
        if self.layout == None:
            return self
        cmds.deleteUI(self.layout)
        return self

    def refresh(self):
        pass

    def move(self, other):
        parent = self.parent
        pos = parent.childrens.index(other)
        parent.childrens.remove(self)
        parent.childrens.insert(pos, self)
        parent.refresh()
        # tmp = cmds.formLayout(p=parent.layout)
        # for c in parent.childrens:
        #     cmds.layout(c.layout, e=True, p=tmp)
        # for c in parent.childrens:
        #     cmds.layout(c.layout, e=True, p=parent.childrenLayout)
        #     # c.reload()
        # cmds.deleteUI(tmp)

    # Jobs
    def _loadJobs(self):
        '''Load all jobs
        '''
        # Example : 
        # self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))
        raise Exception('_loadJobs function not implemented')
    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)
        self._scriptJobIndex = []

    # drag&Drop
    def _dragCb(self, dragControl, x, y, modifiers):
        Module.drag = self
        
        if not self.dragged:
            self.bgc = cmds.layout(self.layout, q=True, bgc=True)
            self.ebg = cmds.layout(self.layout, q=True, ebg=True)
        self.dragged = True
        cmds.layout(self.layout, e=True, ebg=True)
        cmds.layout(self.layout, e=True, bgc=Module.BLUE)
    def _dropCb(self, dragControl, dropControl, messages, x, y, dragType):
        cmds.layout(Module.drag.layout, e=True, bgc=Module.drag.bgc)
        cmds.layout(Module.drag.layout, e=True, ebg=Module.drag.ebg)
        Module.drag.dragged = False
        Module.drag.move(self)
        Module.drag = None

    # Events
    def eventHandler(self, event, c, *args):
        if not event in self.command:
            self.command[event] = []
        self.command[event].append((c, args))
    def runEvent(self, event, *args):
        if not event in self.command:
            return
        for c in self.command[event]:
            if c[0] is None:
                # cmds.error("Event \"" + event + "\" call a function not implemented yet -WIP-")
                log.warning("Event \"" + event + "\" call a function not implemented yet -WIP-")
                continue
            a = c[1] + args
            c[0](*a)


def singleton(class_):
    class class_w(class_):
        __doc__ = class_.__doc__
        _instance = None
        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w,
                                    class_).__new__(class_,
                                                    *args,
                                                    **kwargs)
                class_w._instance._sealed = False
            return class_w._instance
        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
    class_w.__name__ = class_.__name__
    return class_w

def info(message):
    print(" ")
    mel.eval('trace -where ""; print "{}"; trace -where "";'.format(message))

class Vector:
    @staticmethod
    def distance(A, B):
        return sqrt(pow(A[0]-B[0],2) + pow(A[1]-B[1],2) + pow(A[2]-B[2],2))

    def __init__(self, A, B):
        self.A = A[:]
        self.B = B[:]
        #vecteur AB
        self.AB = [self.B[i] - self.A[i] for i in range(len(self.A))]
        #norme du vecteur AB
        self.normeAB = sqrt((self.AB[0]*self.AB[0]) + (self.AB[1]*self.AB[1]) + (self.AB[2]*self.AB[2]))
        #vecteur AB normalise
        self.u = [self.AB[i] / self.normeAB for i in range(len(self.AB))]

        #distance AB
        self.distaAB = Vector.distance(A, B)
        # direction vecteur AB
        self.direction = [(x - y) / self.distaAB for x, y in zip(A, B)]
        
    def isPointBetween(self, M):
        #vecteur AM
        AM = [x - y for x, y in zip(M, self.A)]
        #produit scalaire p=u.AM
        p = self.u[0] * AM[0] + self.u[1] * AM[1] + self.u[2] * AM[2]
        return 0<= p + 0.01 and p - 0.01 <=self.normeAB

    def getRatio(self, M):
        #vecteur AM
        AM = [x - y for x, y in zip(M, self.A)]
        #produit scalaire p=u.AM
        p = sum([x * y for x, y in zip(self.u, AM)])
        return p / self.normeAB

    def distPointToLine(self, M):
        # vecteur Ap
        v = [x - y for x, y in zip(M, self.A)]

        # produit scalaire v.d
        t = sum([x * y for x, y in zip(v, self.direction)])

        projection = [x + t * y for x, y in zip(self.A, self.direction)]
        return Vector.distance(M, projection)

@singleton
class MiniToolRig(Module):
    Singleton = None

    ################################
    #    list of little modules    #
    ################################

    class MG_construction(Module):
        def load(self):
            self.layout = cmds.formLayout(self.name, p=self.parent, bgc=[0.2, 0.2, 0.2], w=5)
            
            self.M_tmp = MiniToolRig.MT_tmp(self.layout).load().layout
            self.M_aim = MiniToolRig.MT_aim(self.layout).load().layout
            self.M_misc = MiniToolRig.MT_constructionMisc(self.layout).load().layout

            self.attach(self.M_tmp, top="FORM", left="FORM", right="FORM", margin=(4,4,4,4))
            self.attach(self.M_aim, top=self.M_tmp, left="FORM", right=50.0, bottom="FORM", margin=(4,4,4,4))
            self.attach(self.M_misc, top=self.M_tmp, left=50.0, right="FORM", bottom="FORM", margin=(4,4,4,4))

            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MT_tmp(Module):
        def __init__(self, parent):
            Module.__init__(self, parent)
            self.sym = False

        @staticmethod
        def prompt():
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
        def createLocator(name, pos=[0,0,0], size=1):
            name = cmds.spaceLocator(r=True, p=[0,0,0], n=name)[0]
            cmds.move(pos[0], pos[1], pos[2], name, a=True)
            MiniToolRig.MT_tmp.setLocalScale(name, size * 1.1)
            cmds.setAttr(name + ".overrideEnabled",1)
            cmds.setAttr(name + ".overrideColor", MiniToolRig.MT_tmp.getColor(name))

        @staticmethod
        def getColor(name):
            if name[-2:] == "_L":
                return 13
            elif name[-2:] == "_R":
                return 6
            else:
                return 17

        @staticmethod
        def setLocalScale(name, size):
            size = float('%.3f'%(size))
            cmds.setAttr(name + ".localScaleX", size)
            cmds.setAttr(name + ".localScaleY", size)
            cmds.setAttr(name + ".localScaleZ", size)

        @staticmethod
        def getSide(center):
            if center[0] > 0.0000001:
                return "_L"
            elif center[0] < -0.0000001:
                return "_R"
            return ""

        def createTMPs(self):
            sel = cmds.ls(sl=True)
            if len(sel) == 0:
                center = [0,0,0]
                size = 1
            else:
                bb = cmds.exactWorldBoundingBox(sel)
                gap =  [abs(bb[i + 3] - bb[i]) for i in range(len(bb) / 2)]
                center = [bb[i] + gap[i] / 2 for i in range(len(gap))]
                size = max(gap) / 2

            
            name = "TMP_" + cmds.textField(self.textField, q=True, text=True)
            if name == "TMP_":
                name = MiniToolRig.MT_tmp.prompt()
            if self.sym:
                cL = center[:]
                cR = [center[0] * -1] + center[1:]
                L = name + MiniToolRig.MT_tmp.getSide(cL)
                R = name + MiniToolRig.MT_tmp.getSide(cR)
                MiniToolRig.MT_tmp.createLocator(L, pos=cL, size=size)
                MiniToolRig.MT_tmp.createLocator(R, pos=cR, size=size)
            else:
                MiniToolRig.MT_tmp.createLocator(name, pos=center, size=max(size,0.1))

            cmds.textField(self.textField, e=True, text="")
            cmds.select(sel)
            print(sel)
            if "[" in sel[0]:
                cmds.selectMode(co=True)

        def changeSymetryState(self):
            self.sym = not self.sym
            if self.sym:
                cmds.iconTextButton(self.btn_sym, e=True, image1="cursor_loop.png", ann="De-activate Symetry")
            else:
                cmds.iconTextButton(self.btn_sym, e=True, image1="dot.png", ann="Activate Symetry")

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, bgc=[0.25, 0.25, 0.25])
            self.btn_go = self.attach(cmds.iconTextButton(style='iconOnly', w=30, h=30, p=self.layout, image1="play_S_100.png", c=Callback(self.createTMPs).repeatable(), ann="Create TMP locator at selection"), top="FORM", right="FORM")
            self.btn_sym = self.attach(cmds.iconTextButton(style='iconOnly', w=30, h=30, p=self.layout, image1="dot.png", c=Callback(self.changeSymetryState), ann="Activate Symetry"), top="FORM", right=self.btn_go)
            self.textField = self.attach(cmds.textField(parent=self.layout, ec=Callback(self.createTMPs).repeatable(), aie=True , pht="Name"), top="FORM", left="FORM", right=self.btn_sym)


            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MT_aim(Module):
        def __init__(self, parent):
            Module.__init__(self, parent)
            self.positif = True

        def changePositifState(self):
            self.positif = not self.positif
            if self.positif:
                cmds.iconTextButton(self.btn_positif, e=True, image1="setEdAddCmd.png", ann="Set world axe to negatif")
            else:
                cmds.iconTextButton(self.btn_positif, e=True, image1="setEdRemoveCmd.png", ann="Set world axe to positif")

        def orientPLAN(self):
            uav = cmds.optionMenu(self.option, q=True, v=True)
            wav = cmds.radioButtonGrp(self.worldAxeUpRdioGrp, q=True, sl=True)
            upAxe = [1, 0, 0] if uav == 'X' else [0, 0, 1] if uav == 'Z' else [0, 0, 0] 
            worldUpAxe = [int(wav == 1), int(wav == 2), int(wav == 3)]
            if not self.positif:
                worldUpAxe = [x * -1 for x in worldUpAxe]
            sel = cmds.ls(sl=True)
            for i in range(0, len(sel) - 1):
                aim = [0, 1, 0]
                if sel[i].endswith("_R"):
                    aim = [x * -1 for x in aim]
                todelete = cmds.aimConstraint(sel[i], sel[i + 1], aim=aim, u=upAxe, wu=worldUpAxe)
                cmds.delete(todelete)

        def load(self):
            self.layout = cmds.columnLayout(p=self.parent, w=85, bgc=[0.25, 0.25, 0.25])
            self._layout = cmds.formLayout(p=self.layout, w=83)
            self.title = self.attach(cmds.text(p=self._layout, l="Aim"), top="FORM", left="FORM", right="FORM")
            self.option = self.attach(cmds.optionMenu(parent=self._layout, ann="Secondary axe"), top=self.title, left="FORM")
            cmds.menuItem( label='X' )
            cmds.menuItem( label='Z' )
            self.btn_positif = self.attach(cmds.iconTextButton(style='iconOnly', ann="Set world axe to negatif", w=30, h=30, p=self._layout, image1="setEdAddCmd.png", c=Callback(self.changePositifState)), top=self.option, left="FORM")
            self.worldAxeUpRdioGrp = self.attach(cmds.radioButtonGrp(parent=self._layout, sl=1, ann="World axe", labelArray3=['x', 'y', 'z'], numberOfRadioButtons=3, vr=True), top=self.title, left=self.option)
            self.btn_orient = self.attach(cmds.button(parent=self._layout, label="Orient", c=Callback(self.orientPLAN)), top=self.worldAxeUpRdioGrp, left="FORM", right="FORM")

            cmds.formLayout(self._layout, e=True, af=self.af, ac=self.ac, ap=self.ap)
            # self.af = []
            # self.attach(self._layout, "FORM", "FORM", "FORM", "FORM")
            # cmds.formLayout(self.layout, e=True, af=self.af)

    class MT_constructionMisc(Module):

        def prompt(self, name):
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

        def orientInsidePLAN(self):
            sel = cmds.ls(sl=True)
            for i in range(0, len(sel) - 1):
                orient = cmds.listRelatives(sel[i], p=True)
                if orient != None:
                    orient = orient[0]
                direction = -1 if sel[i].endswith("_R") else 1
                todelete = cmds.aimConstraint(sel[i + 1], sel[i], aim=[0,direction,0], u=[1,0,0], wu=[1,0,0], wut="objectrotation", wuo=orient)
                cmds.delete(todelete)
            cmds.parent(sel[i + 1], sel[i])
            cmds.setAttr(sel[i + 1] + ".rx", 0)
            cmds.setAttr(sel[i + 1] + ".ry", 0)
            cmds.setAttr(sel[i + 1] + ".rz", 0)
            orient = cmds.listRelatives(sel[i], p=True)[0]
            cmds.parent(sel[i + 1], orient)

        def resetTMP(self):
            sel = cmds.ls(sl=True)
            for s in sel:
                try:
                    cmds.parent(s, world=True)
                except:
                    cmds.warning("lol " + s)
            for s in sel:
                cmds.setAttr(s + ".rx", 0)
                cmds.setAttr(s + ".ry", 0)
                cmds.setAttr(s + ".rz", 0)
                if s.startswith("TMP_"):
                    continue
                cmds.delete(s)

        def createPLAN(self):
            sel = cmds.ls(sl=True)
            for s in sel:
                n = self.prompt(s)
                plan = "PLAN_" + n + s[-2:]
                orient = "ORIENT_" + n + s[-2:]
                cmds.duplicate(s, n=plan)
                cmds.duplicate(s, n=orient)
                cmds.parent(orient, plan)
                cmds.parent(s, orient)


        def squashOnAxe(self, axe):
            sel = cmds.ls(sl=True)
            axe = ".t{}".format(axe.lower())
            moy = cmds.getAttr(sel[0] + axe)
            for s in sel[1:]:
                moy += cmds.getAttr(s + axe)
            moy = moy / float(len(sel))
            
            for s in sel:
                cmds.setAttr(s + axe, moy)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=100, bgc=[0.25, 0.25, 0.25])
            self.childrenLayout = self.attach(cmds.columnLayout(p=self.layout, adj=True, w=1), top="FORM", left="FORM", right="FORM")
            
            self.axeAvgLay = cmds.formLayout(p=self)
            btn_X = cmds.button(p=self.axeAvgLay, l="X", ann="Align selection to the Average of the X axe", c=Callback(self.squashOnAxe, "X").repeatable())
            btn_Y = cmds.button(p=self.axeAvgLay, l="Y", ann="Align selection to the Average of the Y axe", c=Callback(self.squashOnAxe, "Y").repeatable())
            btn_Z = cmds.button(p=self.axeAvgLay, l="Z", ann="Align selection to the Average of the Z axe", c=Callback(self.squashOnAxe, "Z").repeatable())
            cmds.formLayout(self.axeAvgLay, e=True, af=[(btn_X, "top", 0), (btn_Y, "top", 0), (btn_Z, "top", 0), (btn_X, "left", 0), (btn_Z, "right", 0)],
                                                    ap=[(btn_X, "right", 1, 33), (btn_Y, "left", 1, 33), (btn_Y, "right", 1, 66), (btn_Z, "left", 1, 66),])

            cmds.button(p=self, l="Reset Ori/Par", ann="Unparent TMPs & reset rotations", c=Callback(self.resetTMP))
            cmds.button(p=self, l="PLAN/ORIENT", c=Callback(self.createPLAN).repeatable())
            cmds.button(p=self, l="Orient inside", c=Callback(self.orientInsidePLAN).repeatable())

            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MG_transformGroup(Module):
        def freezeTransform(self, t=False, r=False, s=False):
            cmds.makeIdentity(apply=True, t=t, r=r, s=s)

        def resetTransform(self, t=False, r=False, s=False):
            for o in cmds.ls(sl=True):
                try:
                    if t:
                        cmds.setAttr(o + ".tx", 0)
                        cmds.setAttr(o + ".ty", 0)
                        cmds.setAttr(o + ".tz", 0)
                    if r:
                        cmds.setAttr(o + ".rx", 0)
                        cmds.setAttr(o + ".ry", 0)
                        cmds.setAttr(o + ".rz", 0)
                    if s:
                        cmds.setAttr(o + ".sx", 1)
                        cmds.setAttr(o + ".sy", 1)
                        cmds.setAttr(o + ".sz", 1)
                except:
                    pass
        
        def load(self):
            self.layout = cmds.formLayout(self.name, p=self.parent)
            
            self.attach(MiniToolRig.MC_transform(self.layout, "Reset", Module.ORANGE, func=self.resetTransform).load(), top="FORM", bottom="FORM", left="FORM", right=50.0)
            self.attach(MiniToolRig.MC_transform(self.layout, "Freeze", func=self.freezeTransform).load(), top="FORM", bottom="FORM", left=50.0, right="FORM")
            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MC_transform(Module):
        def __init__(self, parent, name=None, bgc=Module.BLUE, func=lambda x: x):
            Module.__init__(self, parent, name=name)
            self.bgc = bgc
            self.func = func

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, bgc=self.bgc)
            self.childrenLayout = self.attach(cmds.columnLayout(p=self.layout, adj=True, w=1), top="FORM", bottom="FORM", left="FORM", right="FORM")
            self.title = cmds.text(p=self.childrenLayout, l=self.name)
            # self.btn_Translate = cmds.button(parent=self.childrenLayout, label="Translate")
            # self.btn_Rotate = cmds.button(parent=self.childrenLayout, label="Rotate")
            # self.btn_Scale = cmds.button(parent=self.childrenLayout, label="Scale")
            w = 20
            h = 30
            self.btn_Translate = cmds.iconTextButton(parent=self.childrenLayout, style='iconOnly', c=Callback(self.func, t=True).repeatable(), ann="Translate", w=w, h=h, image1="move_M.png")
            self.btn_Rotate = cmds.iconTextButton(parent=self.childrenLayout, style='iconOnly', c=Callback(self.func, r=True).repeatable(), ann="Rotate", w=w, h=h, image1="rotate_M.png")
            self.btn_Scale = cmds.iconTextButton(parent=self.childrenLayout, style='iconOnly', c=Callback(self.func, s=True).repeatable(), ann="Scale", w=w, h=h, image1="scale_M.png")

            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MT_additional(Module):

        def createZero(self):
            sl = cmds.ls(sl=True)
            value = float(cmds.floatField(self.ff_zero, q=True, v=True))
            if value == None:
                return
            for joint in sl:
                sideGap = -0.001 if joint.endswith("_R") else 0.001

                l = len(joint) - 2 if joint.endswith("_L") or joint.endswith("_R") else len(joint)
                i = "_0" if joint[l - 1].isnumeric() else "0"
                name0 = joint[:l] + i + joint[l:]
                if cmds.objExists(name0):
                    cmds.warning("The additional joint [{}] already exist".format(name0))
                    return
                
                cmds.duplicate(joint, n=name0, po=True)
                
                parentJoint = cmds.listRelatives(joint, p=True)
                try:
                    cmds.parent(name0, joint)
                except:
                    cmds.warning("lol " + joint)

                cmds.setAttr(name0 + ".tz", sideGap)
                
                if parentJoint is None or parentJoint == []:
                    cmds.parent(name0, w=True)
                else:
                    cmds.parent(name0, parentJoint)
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

                # cmds.connectAttr(joint + ".scale", name0 + ".scale")

            cmds.select(sl)

        def createOri(self):
            sl = cmds.ls(sl=True)
            value = float(cmds.floatField(self.ff_ori, q=True, v=True))
            if value == None:
                return
            for joint in sl:
                sideGap = 0.001 if joint.endswith("_R") else -0.001
                
                l = len(joint) - 2 if (joint.endswith("_L") or joint.endswith("_R")) else len(joint)
                nameOri = joint[:l] + 'Ori' + joint[l:]
                if cmds.objExists(nameOri):
                    cmds.warning("The additional joint [{}] already exist".format(nameOri))
                    return
                
                cmds.duplicate(joint, n=nameOri, po=True)


                parentJoint = cmds.listRelatives(joint, p=True)
                try:
                    cmds.parent(nameOri, joint)
                except:
                    cmds.warning("lol " + joint)

                cmds.setAttr(nameOri + ".tz", sideGap)
                
                if parentJoint is None or parentJoint == []:
                    cmds.parent(nameOri, w=True)
                else:
                    cmds.parent(nameOri, parentJoint)
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

                # cmds.connectAttr(joint + ".scale", nameOri + ".scale")
            cmds.select(sl)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent)
            
            self.bn_ori = self.attach(cmds.button(p=self.layout, label="Create Ori", w = 60, c=Callback(self.createOri)), top="FORM", right="FORM")
            self.ff_ori = self.attach(cmds.floatField(p=self.layout, pre=3, v=0, ann="Y value, between 0.0 and 1.0"), top="FORM", left="FORM", right=self.bn_ori)
            self.bn_zero = self.attach(cmds.button(p=self.layout, label="Create 0", w = 60, c=Callback(self.createZero)), top=self.bn_ori, right="FORM")
            self.ff_zero = self.attach(cmds.floatField(p=self.layout, pre=3, v=0.5, ann="Y value, between 0.0 and 1.0"), top=self.bn_ori, left="FORM", right=self.bn_zero)
            
            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MT_squeletton(Module):
        
        @staticmethod
        def setJoint(obj):
            pos = cmds.xform(obj, q=True, t=True, ws=True)    
            rot = cmds.xform(obj, q=True, ro=True, ws=True)    
            cmds.select(clear=True)
            rx = cmds.getAttr(obj + '.rotateX')
            ry = cmds.getAttr(obj + '.rotateY')
            rz = cmds.getAttr(obj + '.rotateZ')
            size = cmds.getAttr(obj + '.localScaleZ') * 1.2
            cmds.joint(p=pos[0:3], orientation=rot[0:3], name=obj.replace("TMP_", "sk_").replace("pose_", "sk_"), radius=size)

        
        def createAllJoints(self):
            objects = cmds.ls(type="transform", sl=True)
            objects = [x for x in objects if x.split("|")[-1].startswith("TMP_")]
            sel = sorted(objects, key=lambda x : int(x.endswith("_L")) * -2 + int(x.endswith("_R")) * -1 )
            for s in sel:
                MiniToolRig.MT_squeletton.setJoint(s)

        def parentJoints(self):
            sel = cmds.ls(sl=True)[::-1]
            p = sel.pop(0)
            while sel:
                s = sel.pop(0)
                cmds.parent(p, s)
                p = s

        def load(self):
            self.layout = cmds.formLayout(p=self.parent)

            w = 20
            h = 30
            self.bn_generate = self.attach(cmds.iconTextButton(parent=self.layout, c=Callback(self.createAllJoints).repeatable(), style='iconOnly', ann="Generate joint from TMP", w=w, h=h, image1="kinInsert.png"), top="FORM", left="FORM", right=50.0)
            self.bn_parent = self.attach(cmds.iconTextButton(parent=self.layout, c=Callback(self.parentJoints).repeatable(), style='iconOnly', ann="Parent selected Joint in order", w=w, h=h, image1="kinAssumeAngle.png"), top="FORM", left=50.0, right="FORM")


            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MGT_constraintGroup(Module):
        try:
            CONSTRAINTS = {"parent" : cmds.parentConstraint,
                        "point" : cmds.pointConstraint,
                        "orient" : cmds.orientConstraint,
                        "scale" : cmds.scaleConstraint,
                        "aim" : cmds.aimConstraint,
                        "poleVector" : cmds.PoleVectorConstraint}
        except:
            pass

        def hideConstraints(self, v):
            constraints = ["{}Constraint".format(k) for k in MiniToolRig.MGT_constraintGroup.CONSTRAINTS.keys()]
            oldSel = cmds.ls(sl=True)
            cmds.select(cl=True)
            sel = []
            for c in constraints:
                sel += cmds.ls(type=c)
            cmds.select(sel, add=True)

            mel.eval("doHideInOutliner {};".format(int(v)))
            cmds.select(cl=True)
            cmds.select(oldSel)

        def ctrlVis(self):
            img = cmds.iconTextButton(self.visibility_lay, q=True, image1=True)
            if img == 'visible.png':
                cmds.iconTextButton(self.visibility_lay, e=True, image1='hidden.png', ann="Show constraints in outliner")
                self.hideConstraints(True)
            elif img == 'hidden.png':
                cmds.iconTextButton(self.visibility_lay, e=True, image1='visible.png', ann="Hide constraints in outliner")
                self.hideConstraints(False)
        
        def applyConstraint(self, constraint):
            ctrls = cmds.ls(sl=True)
            if len(ctrls) < 2:
                return
            parent = ctrls.pop(0)
            for c in ctrls:
                MiniToolRig.MGT_constraintGroup.CONSTRAINTS[constraint](parent, c, mo=True)

        def copyConstraint(self, constraint):
            ctrls = cmds.ls(sl=True)
            if len(ctrls) < 2:
                return
            parent = ctrls.pop(0)
            for c in ctrls:
                toBeDelete = MiniToolRig.MGT_constraintGroup.CONSTRAINTS[constraint](parent, c)
                cmds.delete(toBeDelete)

        def openConstraint(self, constraint):
            optCons = "{}ConstraintOptions".format(constraint.capitalize())
            f = getattr(cmds, optCons)
            f()

        def load(self):
            self.layout = cmds.formLayout(self.name, p=self.parent, w=5)
            
            m = self.attach(MiniToolRig.MC_constraint(self.layout, "Copy by Constraint", Module.ORANGE, func=self.copyConstraint, dcc_func=self.openConstraint).load(), top="FORM", left="FORM", right=50.0)
            self.attach(MiniToolRig.MC_constraint(self.layout, "Constraint", func=self.applyConstraint, dcc_func=self.openConstraint).load(), top="FORM", left=50.0, right="FORM")
            self.visibility_lay = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', w=30, h=30, image1="visible.png", ann="Hide constraints in outliner", c=Callback(self.ctrlVis)), top=m, left="FORM")
            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MC_constraint(Module):

        def __init__(self, parent, name=None, bgc=Module.BLUE, func=lambda x: x, dcc_func=lambda x: x):
            Module.__init__(self, parent, name=name)
            self.bgc = bgc
            self.func = func
            self.dcc_func = dcc_func

        @staticmethod
        def createIcon(name, parent, func, dcc_func):
            w, h = 30, 30
            _layout_tmp = cmds.columnLayout(p=parent, w=w, h=h, cal="center")
            cmds.iconTextButton(parent=_layout_tmp, style='iconOnly', 
                                ann=name.capitalize(), w=w, h=h, image1=name + "Constraint.svg", 
                                c=Callback(func, name).repeatable().getCommandArgument(), 
                                dcc=Callback(dcc_func, name).getCommandArgument())
            return _layout_tmp
           

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, bgc=self.bgc, w=5)
            # self.childrenLayout = self.attach(cmds.columnLayout(p=self.layout, cal="center", adj=True), top="FORM", bottom="FORM", left="FORM", right="FORM")
            self.childrenLayout = self.attach(cmds.formLayout(p=self.layout), top="FORM", bottom="FORM", left="FORM", right="FORM")
            self.title = cmds.text(p=self.childrenLayout, l=self.name)
            layers = []
            for n in MiniToolRig.MGT_constraintGroup.CONSTRAINTS.keys():
                layers.append(MiniToolRig.MC_constraint.createIcon(n, self.childrenLayout, self.func, self.dcc_func))

            self.applyAttach()
            self.clearAttach()
            self.attach(self.title, top="FORM")
            self.attach(layers[0], top=self.title, left="FORM")
            self.attach(layers[1], top=self.title, left=layers[0])
            self.attach(layers[2], top=self.title, left=layers[1])
            self.attach(layers[3], top=layers[2], left="FORM")
            self.attach(layers[4], top=layers[2], left=layers[3])
            self.attach(layers[5], top=layers[2], left=layers[4])
            self.applyAttach()

    class MT_naming(Module):
        def searchNreplace(self):
            sel = cmds.ls(sl=True)
            sel = sorted(sel, key=lambda x : x.count("|") * -1)
            search_str = cmds.textField(self.CTF_search, q=True, text=True)
            replace_str = cmds.textField(self.CTF_replace, q=True, text=True)
            for s in sel:
                cmds.rename(s, s.split("|")[-1].replace(search_str, replace_str))

        @staticmethod
        def replaceSide(name, side):
            if name.endswith("_L") or name.endswith("_R"):
                return name[:-2] + side
            tmpName = name.replace("_L", "#separator#").replace("_R", "#separator#").replace("_M", "#separator#")
            tmpName = tmpName.split("#separator#")
            l = tmpName[1:]
            r = [not x[0].isalpha() for x in l]
            newName = tmpName[0]
            if r.count(True) == 0:
                return name + side
            if side == "":
                side = "_M"
            if r.count(True) != 1:
                return name
            for i, n in enumerate(tmpName[1:]):
                if r[i]:
                    newName += side + n
                else:
                    lnn = len(newName)
                    newName += str(name[lnn:lnn + 2]) + n
            return newName        
                
        def setNameToSide(self, side):
            sel = cmds.ls(sl=True)
            sel = sorted(sel, key=lambda x : x.count("|") * -1)
            for s in sel:
                if side != "" and s.endswith(side):
                    continue
                ns = s.split("|")[-1]
                ns = ns[:-1] if ns.endswith("_L1") else ns[:-1] if ns.endswith("_R1") else ns
                ns = MiniToolRig.MT_naming.replaceSide(ns, side)
                cmds.rename(s, ns)

        def enterEvent(self, t=False):
            print(self, self.CTF_replace)
            if not t:
                cmds.setFocus(self.CTF_replace)
            else:
                self.searchNreplace()

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            self.C_button = self.attach(cmds.button(p=self.layout, l="replace", c=Callback(self.searchNreplace).repeatable()), top="FORM", left=80, right="FORM", margin=(0, 0, 2, 0))
            self.CTF_search = self.attach(cmds.textField(p=self.layout, w=5, pht="Search", ann="search the words", ec=Callback(self.enterEvent), alwaysInvokeEnterCommandOnReturn=True), top="FORM", left="FORM", right=40, margin=(0, 0, 0, 0))
            self.CTF_replace = self.attach(cmds.textField(p=self.layout, w=5, pht="Replace", ann="replace to the words", ec=Callback(self.enterEvent, True), alwaysInvokeEnterCommandOnReturn=True), top="FORM", left=40, right=80, margin=(0, 0, 0, 2))
            h, w = 30, 30
            self.btn_center = self.attach(cmds.iconTextButton(parent=self.layout, c=Callback(self.setNameToSide, "").repeatable(), style='iconOnly', ann="Name the node to Center", w=w, h=h, image1="UVAlignMiddleU.png"), top=self.C_button, left=self.CTF_search, margin=(0, 0, -15, 0))
            self.btn_left = self.attach(cmds.iconTextButton(parent=self.layout, c=Callback(self.setNameToSide, "_L").repeatable(), style='iconOnly', ann="Name the node to Left", w=w, h=h, image1="UVAlignRight.png"), top=self.C_button, right=self.btn_center)
            self.btn_right = self.attach(cmds.iconTextButton(parent=self.layout, c=Callback(self.setNameToSide, "_R").repeatable(), style='iconOnly', ann="Name the node to Right", w=w, h=h, image1="UVAlignLeft.png"), top=self.C_button, left=self.btn_center)

            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MT_coloring(Module):
        COLOR = [
            0x000101,
            0x3d4147,
            0x7f7d83,
            0x9c0222,
            0x00035e,
            0x0003f4,
            0x044217,
            0x240148,
            0xc005c0,
            0x874430,
            0x411e1f,
            0x952500,
            0xfc0104,
            0x00fd04,
            0x023f9a,
            0xfeffff,
            0xfbfc06,
            0x65d9f7,
            0x40fca2,
            0xf8ada8,
            0xe5a975,
            0xfafb64,
            0x029552,
            0xa06632,
            0x9e9c2d,
            0x689f2f,
            0x2f9e5b,
            0x309f9d,
            0x2b659d,
            0x732aa0,
            0xa12c68,
            ]

        COLORSNAMES = [
            "black",
            "darkGrey",
            "lightGrey",
            "plum",
            "darkBlue",
            "blue",
            "darkGreen",
            "darkPurple",
            "fushia",
            "lightBrown",
            "darkBrown",
            "brown",
            "red",
            "green",
            "royaleBlue",
            "white",
            "yellow",
            "cyan",
            "seaGreen",
            "plum",
            "rosyBrown",
            "lemon",
            "emerald",
            "bronze",
            "lightOlive",
            "olive",
            "turquoise",
            "mediumTurquoise",
            "indigo",
            "purple",
            "magenta",
            ]

        @staticmethod
        def hexToRGB(hexa):
            """
            :hexa:
            """
            rgb = []
            rgb.append((round(hexa / 0x10000) % 0x100) / 0x100)
            rgb.append((round(hexa / 0x100) % 0x100) / 0x100)
            rgb.append(float(hexa % 0x100) / 0x100)
            return rgb

        @staticmethod
        def colorWindow():
            layout = cmds.setParent(q=True)
            cmds.formLayout(layout, e=True, width=190)
            w, h = 20, 20

            ac = []
            af = []

            left_itb = None
            top_itb = None
            for i in range(0, len(MiniToolRig.MT_coloring.COLOR)):
                color = MiniToolRig.MT_coloring.hexToRGB(MiniToolRig.MT_coloring.COLOR[i])
                colorName = MiniToolRig.MT_coloring.COLORSNAMES[i]
                itb = cmds.iconTextButton(parent=layout, c='cmds.layoutDialog( dismiss="{}" )'.format(str(i)), bgc=color, style='iconOnly', ann=colorName, w=w, h=h)
                if top_itb == None:
                    af.append((itb, "top", 1))
                else:
                    ac.append((itb, "top", 1, top_itb))
                if left_itb == None:
                    af.append((itb, "left", 1))
                else:
                    ac.append((itb, "left", 1, left_itb))
                left_itb = itb
                if (i + 1) % 9.0 == 0.0:
                    top_itb = itb
                    left_itb = None
            itb = cmds.button(p=layout, l="remove", c='cmds.layoutDialog( dismiss="remove" )')
            if top_itb == None:
                af.append((itb, "top", 1))
            else:
                ac.append((itb, "top", 1, top_itb))
            if left_itb == None:
                af.append((itb, "left", 1))
            else:
                ac.append((itb, "left", 1, left_itb))

            cmds.formLayout(layout, e=True, af=af, ac=ac)

        def AssignColor(self, location):
            value = cmds.layoutDialog(ui=Callback(MiniToolRig.MT_coloring.colorWindow))
            sel = cmds.ls(sl=True, r=(location == "viewport"))
            if value == "dismiss":
                return
            if value == "remove":
                if location == "viewport":
                    for s in sel:
                        cmds.setAttr("{}.overrideEnabled".format(s), False)
                        cmds.setAttr("{}.overrideColor".format(s), 0)

                if location == "outliner":
                    for s in sel:
                        cmds.setAttr("{}.useOutlinerColor".format(s), False)
                        cmds.setAttr("{}.outlinerColor".format(s), 0, 0, 0)
                return
            value = int(value)
            if location == "viewport":
                for s in sel:
                    cmds.setAttr("{}.overrideEnabled".format(s), True)
                    cmds.setAttr("{}.overrideColor".format(s), value + 1)

            if location == "outliner":
                color = MiniToolRig.MT_coloring.hexToRGB(MiniToolRig.MT_coloring.COLOR[value])
                for s in sel:
                    cmds.setAttr("{}.useOutlinerColor".format(s), True)
                    cmds.setAttr("{}.outlinerColor".format(s), color[0], color[1], color[2])

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            h, w = 30, 30
            self.btn_center = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', c=Callback(self.AssignColor, "outliner"), ann="Color in the outliner", w=w, h=h, image1="outliner.png"), top="FORM", left=50)
            self.btn_left = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', c=Callback(self.AssignColor, "viewport"), ann="Color in the viewport", w=w, h=h, image1="singlePerspLayout.png"), top="FORM", right=50)

            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    class MC_slider(Module):
        switchColor = False
        def __init__(self, parent, name=None, attr=None, defaultValue=1.0, minMax=None, changeFunc=None, type_=float):
            Module.__init__(self, parent, name=name)
            self.attr = attr
            self.step = 1.0
            self.max = self.step * 2
            self.changeFunc = changeFunc
            self.minMax = minMax
            self.defaultValue = defaultValue
            self.type = type_
            self._cmdsSlider = cmds.floatSlider if self.type == float else cmds.intSlider
            self._cmdsInputField = cmds.floatField if self.type == float else cmds.intField

        def sliderChangeEvent(self):
            v = self._cmdsSlider(self.slider, q=True, v=True)
            self._cmdsInputField(self.field, e=True, v=v)
            if self.changeFunc != None:
                self.changeFunc(self.attr, v)

        def inputFieldChangeEvent(self, diff=None):
            v = self._cmdsInputField(self.field, q=True, v=True)
            minV = self._cmdsSlider(self.slider, q=True, min=True)
            maxV = self._cmdsSlider(self.slider, q=True, max=True)
            gap = maxV - minV
            if diff is not None:
                if diff == "add":
                    v = self.type(v + gap * 0.1)
                if diff == "sub":
                    v = self.type(v - gap * 0.1)
            self._cmdsInputField(self.field, e=True, v=v)
            if self.changeFunc != None:
                self.changeFunc(self.attr, v)
            if minV <= v and v <= maxV:
                self._cmdsSlider(self.slider, e=True, v=v)

        def load(self):
            w, h = 20, 20
            bgc = [0.2, 0.2, 0.2,] if MiniToolRig.MC_slider.switchColor else [0.25, 0.25, 0.25]
            MiniToolRig.MC_slider.switchColor = not MiniToolRig.MC_slider.switchColor
            self.layout = cmds.formLayout(p=self.parent, w=5, h=40, bgc=bgc)
            self.title = self.attach(cmds.text(l=self.name, p=self.layout), top="FORM", left="FORM", margin=(2, 2, 2, 2))
            self.btn_add = self.attach(cmds.iconTextButton(p=self.layout,
                                                        style='iconOnly',
                                                        ann="add", w=w, h=h,
                                                        image1="moveUVRight.png",
                                                        c=Callback(self.inputFieldChangeEvent, "add")),
                                    top="FORM", right="FORM", margin=(2, 2, 2, 2))
            self.field = self.attach(self._cmdsInputField(p=self.layout, 
                                                        w=60,
                                                        v=self.type(self.defaultValue),
                                                        ec=Callback(self.inputFieldChangeEvent)),
                                    top="FORM", right=self.btn_add, margin=(2, 2, 2, 2))
            if self.type is float:
                self._cmdsInputField(self.field, e=True, pre=1)
            self.btn_sub = self.attach(cmds.iconTextButton(p=self.layout,
                                                        style='iconOnly',
                                                        ann="sub", w=w, h=h,
                                                        image1="moveUVLeft.png",
                                                        c=Callback(self.inputFieldChangeEvent, "sub")),
                                    top="FORM", right=self.field, margin=(2, 2, 2, 2))

            if self.minMax is None:
                self.slider = self.attach(self._cmdsSlider(p=self.layout, v=self.type(self.defaultValue), dc=Callback(self.sliderChangeEvent)), top=self.field, left="FORM", right="FORM", margin=(2, 2, 20, 2))
            else:
                self.slider = self.attach(self._cmdsSlider(p=self.layout, v=self.type(self.defaultValue), min=self.type(self.minMax[0]), max=self.type(self.minMax[1]), dc=Callback(self.sliderChangeEvent)), top=self.field, left="FORM", right="FORM", margin=(2, 2, 20, 2))

            self.applyAttach()

    class MT_controlerShape(Module):
        class Shape(object):
            size = 10.0

            def __init__(self, joint=None, cnx=True):
                object.__init__(self)
                self.created = False
                self.cnx = cnx
                self.object = None
                self.joint = joint if cmds.objExists(joint) else None
                self.name = joint if self.joint is None else joint.replace("sk_", "FK_")

                self.ctrlName = "c_" + self.name
                self.create()
                attributes = inspect.getmembers(self.__class__, lambda a:not(inspect.isroutine(a)))
                self.attributes = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
                self.attributesName = [a[0] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
                self.created = True
                if self.object is None:
                    raise Exception('The create function  must set the value of self.object')
                self.grp_pose = cmds.group(self.object, n="pose_" + self.name)
                self.grp_inf = cmds.group(self.grp_pose, n="inf_" + self.name)
                self.grp_root = cmds.group(self.grp_inf, n="root_" + self.name)
                if self.joint is not None and cmds.objExists(self.joint):
                    toDelete = cmds.parentConstraint(self.joint, self.grp_root)
                    cmds.delete(toDelete)
                self.shape = cmds.listRelatives(self.object)
                h = cmds.listConnections(self.shape, s=True)
                self.history = h[0] if h is not None else None
                self.refresh()

            def create(self):
                raise Exception('create function not implemented')

            def connectParentCtrl(self):
                parJoint = cmds.listRelatives(self.joint, p=True, type="joint")
                if parJoint is None:
                    return
                ctrl = cmds.parentConstraint(self.joint, q=True, tl=True)
                parCtrl = cmds.parentConstraint(parJoint, q=True, tl=True)
                if parCtrl is None:
                    return
                par = cmds.listRelatives(ctrl, p=True)
                inf = None
                for _ in range(0, 50):
                    if par == None:
                        break
                    if par[0].startswith("inf_"):
                        inf = par
                        break
                    par = cmds.listRelatives(par, p=True)
                if cmds.parentConstraint(inf, q=True, tl=True) != parCtrl:
                    cmds.parentConstraint(parCtrl, inf, mo=True)
                
            def connectChildCtrl(self):
                ctrl = cmds.parentConstraint(self.joint, q=True, tl=True)
                childJoint = cmds.listRelatives(self.joint, c=True, type="joint")
                if childJoint is None:
                    return
                for c in childJoint:
                    childCtrl = cmds.parentConstraint(c, q=True, tl=True)
                    if childCtrl is None:
                        continue
                    childPar = cmds.listRelatives(childCtrl, p=True)
                    infChild = None
                    for _ in range(0, 50):
                        if childPar == None:
                            break
                        if childPar[0].startswith("inf_"):
                            infChild = childPar
                            break
                        childPar = cmds.listRelatives(childPar, p=True)
                    if cmds.parentConstraint(infChild, q=True, tl=True) != ctrl:
                        cmds.parentConstraint(ctrl, infChild, mo=True)

            def apply(self):
                cmds.delete(self.object, constructionHistory = True)
                cmds.makeIdentity(self.object, apply=True, t=True, r=True, s=True)
                if self.joint is not None and self.cnx:
                    cmds.parentConstraint(self.object, self.joint, mo=True)
                    # cmds.scaleConstraint(self.object, self.joint, mo=True)
                    self.connectChildCtrl()
                    self.connectParentCtrl()

            def refresh(self):
                if not self.created:
                    return
                cmds.undoInfo( swf=False)
                
                for attr in self.attributes:
                    updateFunc = "update_" + attr[0]
                    if hasattr(self, updateFunc) and callable(getattr(self, updateFunc)):
                        object.__getattribute__(self, updateFunc)(attr[1])
                cmds.undoInfo( swf=True)

            @classmethod
            def getListAttr(cls, *args):
                '''return a dict
                {"name of the attribut" : ["pretty name", type, value, "name of the attr that must be above", [min, max]]}
                '''
                if len(args) >= 1:
                    if issubclass(args[0], cls):
                        cls = args[0]
                
                attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
                l = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
                l = {a[0] : [a[0].capitalize(), type(a[1]), a[1], None, None] for a in l}
                return l

            def __setattr__(self, name, value):
                object.__setattr__(self, name, value)
                vars()[name] = value
                # setattr(self.__class__, name, value)
                if self.created:
                    if name not in self.attributesName:
                        return
                    updateFunc = "update_" + name
                    if hasattr(self, updateFunc) and callable(getattr(self, updateFunc)):
                        cmds.undoInfo( swf=False)
                        object.__getattribute__(self, updateFunc)(value)
                        cmds.undoInfo( swf=True)
                    else:
                        cmds.warning("the function {} is not implemented".format(updateFunc))
            
            def update_size(self, value):
                if self.joint is not None:
                    value = value * cmds.getAttr(self.joint + ".radius")
                cmds.setAttr(self.object + ".sx", value * 0.1)
                cmds.setAttr(self.object + ".sy", value * 0.1)
                cmds.setAttr(self.object + ".sz", value * 0.1)

        class ShapeCircle(Shape):
            sweep = 360.0
            sweepOffset = 0.0

            def create(self):
                self.object = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=self.__class__.sweep, r=self.__class__.size * 0.1,
                                        d=3, ut=0, tol=0.01, s=8, ch=1, n=self.ctrlName)[0]

            def update_sweep(self, value):
                cmds.setAttr(self.history + ".sweep", value)

            @classmethod
            def getListAttr(cls):
                attrs = MiniToolRig.MT_controlerShape.Shape.getListAttr(cls)

                attrs["sweepOffset"][0] = "Sweep offset"

                attrs["sweepOffset"][3] = "sweep"
                
                attrs["sweep"][4] = [0, 360]
                attrs["sweepOffset"][4] = [0, 360]

                return attrs

        class ShapeStar(Shape):
            hardness = 60.0
            section = 4
            def create(self):
                self.object = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=360.0, r=self.__class__.size,
                                        d=3, ut=0, tol=0.01, s=self.__class__.section * 2, ch=1, n=self.ctrlName)[0]

            @classmethod
            def getListAttr(cls):
                attrs = MiniToolRig.MT_controlerShape.Shape.getListAttr(cls)

                attrs["section"][0] = "Number of point"
                attrs["hardness"][0] = "Hardness %"

                attrs["hardness"][3] = "section"
                
                attrs["section"][4] = [3, 16]

                return attrs

            def update_hardness(self, value):
                vtx = ["{}.cv[{}]".format(self.object, x) for x in range(0, self.section * 2)]
                segment = 360 / float(self.section * 2)
                for i in range(0, self.section * 2):
                    r = (segment * i * 2 * pi) / float(360)
                    s = 1 if  i % 2 == 0 else 1 - value * 0.01
                    cmds.xform(vtx[i], a=True, os=True, translation=(cos(r) * s, 0, sin(r) * s))

            def update_section(self, value):
                cmds.setAttr(self.history + ".sections", value * 2)
                self.hardness = self.hardness

        class ShapeCross(Shape):
            width = 20.0

            def create(self):
                close = 0.2
                far = 1.0
                
                pointPos = []
                for i in range(0, 13):
                    i = i % 12
                    j = (i + 2) % 12
                    x = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))
                    i = (i + 3) % 12
                    j = (j + 3) % 12
                    y = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))
                    pointPos.append((x, 0, y))
                self.object = cmds.curve(d=1, p=pointPos, k=range(0, 13), n=self.ctrlName)

            @classmethod
            def getListAttr(cls):
                attrs = MiniToolRig.MT_controlerShape.Shape.getListAttr(cls)

                attrs["width"][0] = "Width %"

                attrs["width"][4] = [0, 100]
                return attrs

            def update_width(self, value):
                close = value * 0.01
                far = 1.0

                for i in range(0, 13):
                    cv = "{}.cv[{}]".format(self.object, i)
                    i = i % 12
                    j = (i + 2) % 12
                    x = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))

                    i = (i + 3) % 12
                    j = (j + 3) % 12
                    y = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))
                    cmds.xform(cv, a=True, os=True, translation=(x, 0, y))

        class ShapeArrow(Shape):
            height = 10.0
            width = 10.0
            thickness = 50.0
            pointiness = 20.0
            def create(self):
                pointPos = [
                            [0, 0, 1],
                            [4, 0, 1],
                            [4, 0, 2],
                            [8, 0, 0],
                            ]
                pointPos = pointPos + [[x[0], x[1], x[2] * -1] for x in pointPos[::-1]] + [pointPos[0]]
                self.pointPos = pointPos
                self.object = cmds.curve(d=1, p=pointPos, k=range(0, len(pointPos)), os=True, n=self.ctrlName)
                cmds.setAttr("{}.tx".format(self.object), -4)
                cmds.makeIdentity(self.object, t=True)

            @classmethod
            def getListAttr(cls):
                attrs = MiniToolRig.MT_controlerShape.Shape.getListAttr(cls)
                
                attrs["height"][0] = "Height"
                attrs["width"][0] = "Width"
                attrs["thickness"][0] = "Thickness %"
                attrs["pointiness"][0] = "Pointiness"

                attrs["thickness"][2] = 33.333333

                
                attrs["height"][3] = "size"
                attrs["width"][3] = "height"
                attrs["thickness"][3] = "width"
                attrs["pointiness"][3] = "thickness"

                attrs["thickness"][4] = [0, 100]

                return attrs

            def _refreshPointPosition(self):
                for i, p in enumerate(self.pointPos):
                    cmds.xform("{}.cv[{}]".format(self.object, i), a=True, os=True, translation=p)
                # cmds.setAttr("{}.tx".format(self.object), 0)

            def update_thickness(self, value):
                y = (value * 0.01) * self.pointPos[2][2]
                self.pointPos[8][2] = y
                self.pointPos[0][2] = y
                self.pointPos[1][2] = y
                self.pointPos[6][2] = -y
                self.pointPos[7][2] = -y
                self._refreshPointPosition()

            def update_width(self, value):
                y = value * 0.1
                thickness = y - (self.pointPos[2][2] - self.pointPos[1][2])

                self.pointPos[2][2] = y
                self.pointPos[5][2] = -y

                self.pointPos[0][2] = thickness
                self.pointPos[1][2] = thickness                
                self.pointPos[8][2] = thickness

                self.pointPos[6][2] = -thickness
                self.pointPos[7][2] = -thickness
                self._refreshPointPosition()

            def update_pointiness(self, value):
                y = value * 0.1 + self.pointPos[1][0]
                self.pointPos[3][0] = y
                self.pointPos[4][0] = y
                self._refreshPointPosition()

            def update_height(self, value):
                ptns = self.pointPos[3][0] - self.pointPos[1][0] + value * 0.1
                y = value * 0.1
                self.pointPos[1][0] = y
                self.pointPos[2][0] = y
                self.pointPos[5][0] = y
                self.pointPos[6][0] = y

                self.pointPos[3][0] = ptns
                self.pointPos[4][0] = ptns
                self._refreshPointPosition()

        class ShapeDart(Shape):
            width = 50.0
            pointiness = 1.0
            def create(self):
                pointPos = [
                            (-2, 0, 0),
                            (0, 0, 4),
                            (0, 0, 4),
                            (2, 0, 4),
                            (0, 0, 0),
                            ]
                pointPos = pointPos + [(x[0], x[1], x[2] * -1) for x in pointPos[::-1]] + [pointPos[0]]
                self.object = cmds.curve(d=1, p=pointPos, k=range(0, len(pointPos)), os=True, n=self.ctrlName)

        class ShapePin(Shape):
            width = 50.0
            pointiness = 1.0
            def create(self):
                pointPos = [
                            (0, 0, 0),
                            (0, 0, 2),
                            (-1, 0, 3),
                            (0, 0, 4),
                            (1, 0, 3),
                            (0, 0, 2),
                            ]
                self.object = cmds.curve(d=1, p=pointPos, k=range(0, len(pointPos)), os=True, n=self.ctrlName)
        
        class ShapeText(Shape):
            pass
        

        def __init__(self, parent, name=None):
            Module.__init__(self, parent, name=name)
            self.winName = "Controller Adjustement"
            self.shapeNameIndex = {"circle" : MiniToolRig.MT_controlerShape.ShapeCircle,
                                   "star" : MiniToolRig.MT_controlerShape.ShapeStar,
                                   "cross" : MiniToolRig.MT_controlerShape.ShapeCross,
                                   "arrow" : MiniToolRig.MT_controlerShape.ShapeArrow,
                                   "dart" : MiniToolRig.MT_controlerShape.ShapeDart,
                                   "pin" : MiniToolRig.MT_controlerShape.ShapePin,
                                  }

        def _loadJobs(self):
            self._scriptJobIndex.append(cmds.scriptJob(event=["SelectionChanged", Callback(self.selectionChangeEvent)]))

        def selectionChangeEvent(self):
            sel = cmds.ls(sl=True)
            if len(sel) == 0:
                self.closeWin()
            
        def closeWin(self):
            if cmds.workspaceControl(self.winName, exists=True):
                cmds.deleteUI(self.winName)
            for s in self.shapes:
                s.apply()
            cmds.select(cl=True)
            cmds.undoInfo(cck=True)
            cmds.select([s.ctrlName for s in self.shapes], add=True)
            
        def update(self, name, value):
            for s in self.shapes:
                setattr(s, name, value)

        @staticmethod
        def sorteAttrs(attrs):
            newAttrs = []
            for k, v in attrs:
                index = newAttrs.index(v[3]) if v[3] in newAttrs else -1
                print(index)
                if index > 0:
                    newAttrs.insert(index, (k, v))
                else:
                    newAttrs.append((k, v))
            print(newAttrs)
            return newAttrs

        def window(self, shapeType):
            cmds.undoInfo(ock=True)

            self.winName 
            if cmds.workspaceControl(self.winName, exists=True):
                cmds.deleteUI(self.winName)
            self.win = cmds.workspaceControl(self.winName)

            cmds.scriptJob(ro=True, uid=[self.win, Callback(self._killJobs)])   
            self._loadJobs()

            cLay = cmds.columnLayout(p=self.win, w=200, adj=True)
            attrs = shapeType.getListAttr().items()[:]
            attrs = MiniToolRig.MT_controlerShape.sorteAttrs(attrs)
            for k, v in attrs:
                MiniToolRig.MC_slider(cLay, name=v[0], attr=k, changeFunc=self.update, type_=v[1], defaultValue=v[2], minMax=v[4]).load()
            cmds.showWindow(self.win)

        @staticmethod
        def prompt():
            name = ""

            result = cmds.promptDialog(
                            title='Name the ctrl',
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

        def createShape(self, shape, cnx=False):
            sel = cmds.ls(sl=True)
            sel = [x for x in sel if cmds.objectType(x) == "joint" and cmds.getAttr(x + ".v")]
            if len(sel) <= 0:
                #TODO ask for name and create ctrl in center of the world
                name = self.prompt()
                if name is None:
                    return
                self.shapes = [self.shapeNameIndex[shape[0]](name)]
                self.window(type(self.shapes[0]))
                return
            self.shapes = []
            shapeClass = MiniToolRig.MT_controlerShape.Shape
            if shape[0] == "circle":
                shapeClass = MiniToolRig.MT_controlerShape.ShapeCircle
            if shape[0] == "star":
                shapeClass = MiniToolRig.MT_controlerShape.ShapeStar
            if shape[0] == "cross":
                shapeClass = MiniToolRig.MT_controlerShape.ShapeCross
            if shape[0] == "arrow":
                shapeClass = MiniToolRig.MT_controlerShape.ShapeArrow
            if shape[0] == "dart":
                shapeClass = MiniToolRig.MT_controlerShape.ShapeDart
            if shape[0] == "pin":
                shapeClass = MiniToolRig.MT_controlerShape.ShapePin

            for s in sel:
                self.shapes.append(shapeClass(s, cnx=cnx))

            cmds.select([x.object for x in self.shapes])
            self.window(type(self.shapes[0]))

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5, bgc=[0.25, 0.25, 0.25], en=True)
            h, w = 30, 30
            shapeButton = [["circle", "circle.png"],
                            ["star", "polyUltraShape.png"],
                            ["cross", "QR_add.png"],
                            ["arrow", "UVTkNudgeRight.png"],
                            ["dart", "nodeGrapherNext.png"],
                            ["pin", "pinItem.png"],
                            ["text", "text.png"]]
                            
            lastSb = "FORM"
            for sb in shapeButton:
                annotation = "| simple clic:\tCreate a FK ctrl with a {} shape along selecteds joints\n| double clic:\tCreate a FK ctrl with a {} shape along selecteds joints and do the connections".format(sb[0], sb[0])
                lastSb = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann=annotation, w=w, h=h, image1=sb[1], c=Callback(self.createShape, sb), dcc=Callback(self.createShape, sb, True)), top="FORM", left=lastSb)
            lastSb = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="Open Library", w=w, h=h, image1="Objects.png", en=False), top="FORM", right="FORM")

            self.applyAttach()
            return self

    class MGT_controller(Module):
        
        def transfertCtrlShape(self):
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

        def grpCtrls(self):
            ctrls = cmds.ls(sl=True)
            nameTF = cmds.textField(self.tf_parentRIP, q=True, tx=True)
            for c in ctrls:
                if not c.startswith("c_"):
                    if nameTF == "":
                        cmds.error("Name the ctrl starting by 'c_' or put a name in the field next to the button")
                    name = nameTF.replace(" ", "_")
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

        def fuseShapes(self):
            sel = cmds.ls(sl=True, l=True)
            parent = sel.pop()
            for s in sel:    
                cmds.makeIdentity(s, apply=True, t=True, r=True, s=True)
            shapes = cmds.listRelatives(sel, c=True, f=True)
            cmds.parent(shapes, parent, r=True, s=True)

            for s in cmds.listRelatives(parent, c=True, f=True):
                cmds.setAttr(s + ".ihi", 0)

            cmds.delete(sel)

        def createCtrlSet(self):
            sl = cmds.ls(sl=True)
            if len(sl) >= 1:
                for s in sl:
                    if s == "CTRLS":
                        cmds.sets(self.createCtrlSetRec(sl[0]),  n="ctrlsSet")
                    else:
                        self.createCtrlSetRec(s)
            else:
                cmds.warning("Please select at least one group")

        def createCtrlSetRec(self, parent):
            child = cmds.listRelatives(parent)
            if child is None:
                return None
            ctrls = []
            for c in child:
                if c is not None and not c.endswith("Shape"):
                    ret = self.createCtrlSetRec(c)
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

        def createCustomShape(self):
            cmds.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            h, w = 30, 30
        
            m_ctrlShape = self.attach(MiniToolRig.MT_controlerShape(self.layout).load(), top="FORM", left="FORM", right="FORM", margin=(2, 2, 2, 2))
            self.btn_transfShape = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="Transfert shape to other side", w=w, h=h, image1="syncOn.png", c=Callback(self.transfertCtrlShape)), top=m_ctrlShape, left=50)
            self.btn_fuseShape = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="Fuse shapes", w=w, h=h, image1="out_geoConnectable.png", c=Callback(self.fuseShapes).repeatable()), top=m_ctrlShape, right=50)
            self.btn_ctrlSet = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="Create CtrlsSet", w=w, h=h, image1="out_objectSet.png", c=Callback(self.createCtrlSet)), top=m_ctrlShape, left=self.btn_transfShape)
            self.btn_parentRIP = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="group root/inf/pose ctrl", w=w, h=h, image1="showDag.png", c=Callback(self.grpCtrls).repeatable()), top=self.btn_fuseShape, left="FORM")
            self.tf_parentRIP = self.attach(cmds.textField(parent=self.layout, pht="Name", ann="Name of the ctrl", ec=Callback(self.grpCtrls).repeatable(), aie=True), top=self.btn_fuseShape, left=self.btn_parentRIP, right="FORM", margin=(5, 0, 0, 0))

            # self.btn_left = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="Color in the viewport", w=w, h=h, image1="closeGeom.png"), top=self.btn_left, right=50)

            self.applyAttach()

    class MC_getChain(Module):
        def __init__(self, parent, name=None, color=Module.TURQUOISE):
            Module.__init__(self, parent, name=name)
            self.chain = []
            self.chainLay = []
            self.color = color

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5, bgc=[0.25, 0.25, 0.25])
            self.c_btn = cmds.button(p=self.layout, l="Get " + self.name, c=Callback(self._setChain))
            # self.attach(self.c_btn, top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))
            
            self.loadChain()
            self.applyAttach()

        def dragCb(self, dragControl, x, y, modifiers):
            cmds.control(dragControl, e=True, ebg=True)
            cmds.control(dragControl, e=True, bgc=Module.BLUE)


        def dropCb(self, dragControl, dropControl, messages, x, y, dragType):
            if not dragControl in self.chainLay:
                return
            cmds.control(dragControl, e=True, bgc=self.color)
            old, new = self.chainLay.index(dragControl), self.chainLay.index(dropControl)
            self.chain.insert(new, self.chain.pop(old))
            self.chainLay.insert(new, self.chainLay.pop(old))

            tmpLay = cmds.formLayout()
            for c in self.chainLay:
                cmds.control(c, e=True, p=tmpLay)
            for c in self.chainLay:
                cmds.control(c, e=True, p=self.layout)
            cmds.deleteUI(tmpLay)
            self.refresh()

        def refresh(self):
            self.attach(self.c_btn, top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))

            last = self.c_btn
            for c in self.chainLay:
                last = self.attach(c, top=last, left="FORM", right="FORM", margin=(1,1,2,2))
            self.applyAttach()

        def loadChain(self):
            for c in self.chainLay:
                cmds.deleteUI(c)
            self.chainLay = []
            self.attach(self.c_btn, top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))

            last = self.c_btn
            for c in self.chain:
                last = self.attach(cmds.text("Text" + c.capitalize(), p=self.layout, bgc=self.color, l=c,
                                             dgc=Callback(self.dragCb).getCommandArgument(), 
                                             dpc=Callback(self.dropCb).getCommandArgument()),
                                   top=last, left="FORM", right="FORM", margin=(1,1,2,2))
                self.chainLay.append(last)
        
        def _setChain(self):
            sel = cmds.ls(sl=True)
            self.setChain(sel)

        def setChain(self, sel):
            self.chain = sel
            self.clearAttach()
            self.loadChain()
            self.applyAttach()

    class MC_sideSelect(Module):
        def __init__(self, parent, name=None):
            Module.__init__(self, parent, name=name)
            self.side = "L"

        def switch(self, side):
            self.side = side
            cmds.button(self.btn_L, e=True, en=not (self.side == "L"), bgc=Module.BLUE if (self.side == "L") else [0.25,0.25,0.25])
            cmds.button(self.btn_C, e=True, en=not (self.side == "C"), bgc=Module.BLUE if (self.side == "C") else [0.25,0.25,0.25])
            cmds.button(self.btn_R, e=True, en=not (self.side == "R"), bgc=Module.BLUE if (self.side == "R") else [0.25,0.25,0.25])

        def load(self):
            self.layout = cmds.formLayout(p=self.parent)
            self.btn_L = self.attach(cmds.button(p=self.layout, c=Callback(self.switch, "L"), l="L", bgc=Module.BLUE, en=False), top="FORM", left="FORM", right=33)
            self.btn_C = self.attach(cmds.button(p=self.layout, c=Callback(self.switch, "C"), l="C", bgc=[0.25,0.25,0.25]), top="FORM", left=33, right=66)
            self.btn_R = self.attach(cmds.button(p=self.layout, c=Callback(self.switch, "R"), l="R", bgc=[0.25,0.25,0.25]), top="FORM", left=66, right="FORM")

            self.applyAttach()

    class MG_ikGroup(Module):
        @staticmethod
        def countParent(bone):
            parent = cmds.listRelatives(bone, p=True)
            if parent == None:
                return 0
            return MiniToolRig.MG_ikGroup.countParent(parent) + 1

        def duplicateIK(self):
            sel = cmds.ls(sl=True)
            dup = cmds.duplicate(sel, po=True, rc=True)
            dup = sorted(dup, key=MiniToolRig.MG_ikGroup.countParent)
            cmds.parent(dup[0], w=True)
            for d in dup:
                newName = d.split("|")[-1][:-1]
                newName = "_".join(["ik"] + newName.split("_")[1:])
                cmds.rename(d, newName)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            self.c_btnDuplicate = self.attach(cmds.button(p=self.layout, l="duplicate", c=Callback(self.duplicateIK)), top="FORM", left="FORM")

            self.ikRps = self.attach(MiniToolRig.MT_ikRPS(self.layout).load(), top=self.c_btnDuplicate, left="FORM", right="FORM", margin=(6, 2, 2, 2))
            self.applyAttach()

    class MT_ikRPS(Module):
        def __init__(self, parent, name=None):
            Module.__init__(self, parent, name=name)
            self.chain_ik = []
            self.chain_ctrls = []
            self.chainLay_ik = []
            self.chainLay_ctrls = []
            self.name = ""
            self.bck_af = []
            self.bck_ac = []
            self.bck_ap = []

        def createIk(self):
            self.chain_ik = self.c_getChainIk.chain
            self.chain_ctrls = self.c_getChainCtrls.chain

            if len(self.chain_ik) != 3:
                cmds.error("The Ik chain must be made of 3 bones")
            mName = cmds.textField(self.c_tfMemberName, q=True, tx=True)
            if mName == "" or mName == None:
                cmds.error("Please, enter a member's name")
            cName = cmds.textField(self.c_tfCtrlName, q=True, tx=True)
            if cName == "" or cName == None:
                cmds.error("Please, enter a ctrl's name")
            grpReverseName = "grp_reverse" + cName
            if not cmds.objExists(grpReverseName):
                #TODO ne pas oublier le rotateOrder
                grpReverse = cmds.group(em=True, n=grpReverseName)
                
                cmds.setAttr(grpReverse + ".rotateOrder", cmds.getAttr(self.chain_ik[-1] + ".rotateOrder"))
                toBeDelete = cmds.parentConstraint(self.chain_ik[-1], grpReverse, mo=False)
                cmds.delete(toBeDelete)
            ikh, eff = cmds.ikHandle( n="ikh_" + mName, sj=self.chain_ik[0], ee=self.chain_ik[-1], sol="ikRPsolver")
            cmds.rename(eff, "eff_" + mName)
            cmds.setAttr(ikh + ".v", False)
            cmds.parent(ikh, grpReverseName)
            pv = cmds.spaceLocator(n="pv_" + mName)[0]
            toBeDelete = cmds.parentConstraint(self.chain_ik[1], pv, mo=False)
            cmds.delete(toBeDelete)
            cmds.setAttr(pv + ".rx", 0)
            gap = max(cmds.getAttr(self.chain_ik[0] + ".ty"), cmds.getAttr(self.chain_ik[1] + ".ty")) * 1.2
            gap = gap if self.chain_ik[0].endswith("_R") else gap * -1
            cmds.setAttr(pv + ".tz", gap)
            cmds.setAttr(pv + ".v", False)
            cmds.parent(pv, self.chain_ctrls[1])
            cmds.poleVectorConstraint(pv, ikh)
            posGrp = cmds.listRelatives(self.chain_ctrls[1], p=True)[0]
            infGrp = cmds.listRelatives(posGrp, p=True)[0]
            aimName = "_".join(["aim"] + posGrp.split("|")[-1].split("_")[1:])
            pvName = "_".join(["pv"] + posGrp.split("|")[-1].split("_")[1:])
            aimGrp = cmds.group(em=True, n=aimName) #posGrp
            toBeDelete = cmds.parentConstraint(posGrp, aimGrp, mo=False)
            cmds.delete(toBeDelete)
            cmds.parent(aimGrp, infGrp)
            cmds.parent(posGrp, aimGrp)
            pvGrp = cmds.duplicate(aimGrp, po=True, n=pvName)[0]
            locBaseName = "_".join(["loc", cName.split("_")[0], "Base"] + cName.split("_")[1:])
            locMoveName = "_".join(["loc", cName.split("_")[0], "Move"] + cName.split("_")[1:])
            locBase = cmds.spaceLocator(n=locBaseName)[0]
            locMove = cmds.spaceLocator(n=locMoveName)[0]
            cmds.parent(locBase, pvGrp)
            cmds.parent(locMove, pvGrp)
            toBeDelete = cmds.parentConstraint(grpReverseName, locBase)
            cmds.delete(toBeDelete)
            cmds.parentConstraint(self.chain_ctrls[-1], grpReverseName)
            cmds.parentConstraint(grpReverseName, locMove)
            ab = cmds.createNode("angleBetween", n="ab_" + mName)
            cmds.connectAttr(locBase + ".translate", ab + ".vector1")
            cmds.connectAttr(locMove + ".translate", ab + ".vector2")
            cmds.setAttr(pvGrp + ".v", False)
            cmds.connectAttr(ab + ".euler", aimGrp + ".rotate")
            cmds.parentConstraint(self.chain_ctrls[0], infGrp)

            grpScaleName = "grp_" + mName.split("_")[0] + "s_scale"
            if not cmds.objExists(grpScaleName):
                grpReverse = cmds.group(em=True, n=grpScaleName)
            cmds.parent(grpReverseName, grpReverse)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5, bgc=[0.25, 0.25, 0.25])
            self.c_labelMemberName = self.attach(cmds.text(p=self.layout, l="Member's name : "), top="FORM", left="FORM")
            self.c_tfMemberName = self.attach(cmds.textField(p=self.layout), top="FORM", left=self.c_labelMemberName, right="FORM")
            self.c_labelCtrlName = self.attach(cmds.text(p=self.layout, l="Ctrl's name : "), top=self.c_tfMemberName, left="FORM")
            self.c_tfCtrlName = self.attach(cmds.textField(p=self.layout), top=self.c_tfMemberName, left=self.c_labelCtrlName, right="FORM")
            # self.c_btnSk = self.attach(cmds.button(p=self.layout, l="Set SK", c=Callback(self.setChain, "sk")), top=self.c_tfCtrlName, left="FORM", right=50, margin=(4,20,1,1))
            # self.c_btnIk = self.attach(cmds.button(p=self.layout, l="Set IK", c=Callback(self.setChain, "ik")), top=self.c_tfCtrlName, left="FORM", right=50, margin=(4,20,1,1))
            # self.c_btnCtrls = self.attach(cmds.button(p=self.layout, l="Set CTRLS", c=Callback(self.setChain, "ctrls")), top=self.c_tfCtrlName, left=50, right="FORM", margin=(4,20,1,1))
            self.c_getChainIk = self.attach(MiniToolRig.MC_getChain(self.layout, "IK").load(), top=self.c_tfCtrlName, left="FORM", right=50, margin=(4,20,1,1))
            self.c_getChainCtrls = self.attach(MiniToolRig.MC_getChain(self.layout, "CTRLS").load(), top=self.c_tfCtrlName, left=50, right="FORM", margin=(4,20,1,1))
            self.c_btnCreate = self.attach(cmds.button(p=self.layout, l="Create", c=Callback(self.createIk)), bottom="FORM", left=50, right="FORM", margin=(4,0,1,1))
            # self.bck_af = self.af
            # self.bck_ac = self.ac
            # self.bck_ap = self.ap

            # self.loadChains()

            self.applyAttach()

    class MT_switch(Module):
        def __init__(self, parent, name=None):
            Module.__init__(self, parent, name=name)
            self.chain_sk = ["sk_clav_L", "sk_shoulder_L", "sk_elbow_L", "sk_wrist_L", "sk_hand_L"]
            self.chain_ik = ["ik_clav_L", "ik_shoulder_L", "ik_elbow_L", "ik_wrist_L", "ik_hand_L"]
            self.chainLay_sk = []
            self.chainLay_ik = []
            self.t_switch = "c_switch_arm_L"
            self.t_FkCtrlGrp = "grp_FK_arm_ctrls_L"
            self.t_IkCtrlGrp = "grp_IK_arm_ctrls_L"
            self.name = ""
            self.bck_af = []
            self.bck_ac = []
            self.bck_ap = []

        def createSwitch(self):
            if len(self.chain_ik) != len(self.chain_sk):
                cmds.error("The two chain must be the same lenght")
            if self.t_switch == None:
                cmds.error("Please, set the switch")
            if self.t_FkCtrlGrp == None:
                cmds.error("Please, set the group of FK's ctrls")
            if self.t_IkCtrlGrp == None:
                cmds.error("Please, set the group of IK's ctrls")

            for ik, sk in zip(self.chain_ik, self.chain_sk):
                cnx = cmds.listConnections(sk, s=True)
                influenced = False
                for c in cnx:
                    if cmds.objectType(c) == "parentConstraint":
                        influenced = True
                        break
                if influenced:
                    parentConst = cmds.parentConstraint(sk, q=True, n=True)
                    pcInf = cmds.parentConstraint(parentConst, q=True, tl=True)
                    for inf in pcInf:
                        print("\t{}".format(inf))


        # TODO replace all this system with a MC_getChain
        def loadChains(self):
            for c in self.chainLay_sk:
                cmds.deleteUI(c)
            self.chainLay_sk = []

            for c in self.chainLay_ik:
                cmds.deleteUI(c)
            self.chainLay_ik = []


            self.af = self.bck_af[:]
            self.ac = self.bck_ac[:]
            self.ap = self.bck_ap[:]
            self.chainLay_sk = []
            self.chainLay_ik = []

            last = self.c_btnSk
            for c in self.chain_sk:
                last = self.attach(cmds.text(p=self.layout, bgc=Module.TURQUOISE, l=c), top=last, left="FORM", right=50, margin=(1,1,2,2))
                self.chainLay_sk.append(last)

            last = self.c_btnIk
            for c in self.chain_ik:
                last = self.attach(cmds.text(p=self.layout, bgc=Module.BLUE, l=c), top=last, left=50, right="FORM", margin=(1,1,2,2))
                self.chainLay_ik.append(last)

        def setTransform(self, t):
            sel = cmds.ls(sl=True)
            if len(sel) != 1:
                cmds.warning("Select only one!")
                return 
            if t == "switch":
                self.t_switch = sel[0]
                cmds.textField(self.c_tfswitch, e=True, tx=sel[0])
            if t == "fkCtrl":
                self.t_FkCtrlGrp = sel[0]
                cmds.textField(self.c_tfFkCtrlGrp, e=True, tx=sel[0])
            if t == "ikCtrl":
                self.t_IkCtrlGrp = sel[0]
                cmds.textField(self.c_tfIkCtrlGrp, e=True, tx=sel[0])

        def setChain(self, type_):
            sel = cmds.ls(sl=True)
            if type_ == "sk":
                self.chain_sk = sel
            if type_ == "sk":
                self.chain_sk = sel
            if type_ == "ik":
                self.chain_ik = sel
                
            self.clearAttach()

            self.loadChains()
            self.applyAttach()

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5, bgc=[0.25, 0.25, 0.25])
            self.c_btnSetSwitch = self.attach(cmds.button(p=self.layout, c=Callback(self.setTransform, "switch"), l="set Switch"), top="FORM", right="FORM")
            self.c_tfswitch = self.attach(cmds.textField(p=self.layout, ed=False, bgc=[0.2, 0.2, 0.2]), top="FORM", right=self.c_btnSetSwitch, left="FORM", margin=(2, 2, 2, 2))
            self.c_btnSetFkCtrlGrp = self.attach(cmds.button(p=self.layout, c=Callback(self.setTransform, "fkCtrl"), l="set FK ctrlGrp"), top=self.c_tfswitch, right="FORM")
            self.c_tfFkCtrlGrp = self.attach(cmds.textField(p=self.layout, ed=False, bgc=[0.2, 0.2, 0.2]), top=self.c_tfswitch, right=self.c_btnSetFkCtrlGrp, left="FORM", margin=(2, 2, 2, 2))
            self.c_btnIkCtrlGrp = self.attach(cmds.button(p=self.layout, c=Callback(self.setTransform, "ikCtrl"), l="set IK ctrlGrp"), top=self.c_tfFkCtrlGrp, right="FORM")
            self.c_tfIkCtrlGrp = self.attach(cmds.textField(p=self.layout, ed=False, bgc=[0.2, 0.2, 0.2]), top=self.c_tfFkCtrlGrp, right=self.c_btnIkCtrlGrp, left="FORM", margin=(2, 2, 2, 2))

            self.c_btnSk = self.attach(cmds.button(p=self.layout, l="Set SK", c=Callback(self.setChain, "sk")), top=self.c_tfIkCtrlGrp, left="FORM", right=50, margin=(4,20,1,1))
            self.c_btnIk = self.attach(cmds.button(p=self.layout, l="Set IK", c=Callback(self.setChain, "ik")), top=self.c_tfIkCtrlGrp, left=50, right="FORM", margin=(4,20,1,1))
            self.c_btnCreate = self.attach(cmds.button(p=self.layout, l="Create", c=Callback(self.createSwitch)), bottom="FORM", left=50, right="FORM", margin=(4,0,1,1))

            self.bck_af = self.af
            self.bck_ac = self.ac
            self.bck_ap = self.ap

            self.loadChains()

            self.applyAttach()

    class MT_arc(Module):
        
        @staticmethod
        def getVtxPos(shapeNode) :
        
            vtxWorldPosition = []
        
            vtxIndexList = cmds.getAttr( shapeNode+".vrts", multiIndices=True )
            for i in vtxIndexList :
                curPointPosition = cmds.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True ) 
                vtxWorldPosition.append(curPointPosition)
        
            return vtxWorldPosition

        @staticmethod
        def getVertexZoneName(mesh, start, end, radius=1):
            A = cmds.xform(start,q=1,ws=1,rp=1)
            B = cmds.xform(end,q=1,ws=1,rp=1)

            zone = Vector(A, B)
            vtx = MiniToolRig.MT_arc.getVtxPos(mesh)
            selection = []
            for v, p in enumerate(vtx):
                if zone.isPointBetween(p):
                    if zone.distPointToLine(p) < radius:
                        selection.append("{}.vtx[{}]".format(mesh, v))
            return selection

        @staticmethod
        def assignPercentWeigth(mesh, start, end, clst, radius=1):
            cmds.progressWindow(e=True, progress=(0), status="{} <~ {}".format(mesh, clst))
            A = cmds.xform(start,q=1,ws=1,rp=1)
            B = cmds.xform(end,q=1,ws=1,rp=1)

            zone = Vector(A, B)
            vtx = MiniToolRig.MT_arc.getVtxPos(mesh)
            
            totalVtx = len(vtx)
            for v, p in enumerate(vtx):
                if zone.isPointBetween(p):
                    if zone.distPointToLine(p) < radius:
                        r = zone.getRatio(p)
                        h = (cos(r * 6.25) * -1) / 2 + 0.5
                        mesh + ".vtx[" + str(v) + "]"
                        cmds.percent(clst, "{}.vtx[{}]".format(mesh, v), v=h)
                cmds.progressWindow(e=True, progress=((float(v) / float(totalVtx)) * 100), status="{} <~ {} [{}/{}]".format(mesh, clst, v, totalVtx))

        @staticmethod
        def CreateNurbSpine(name, side, skChain):
            nurb = "_".join(["nrb", name, side])

            n = cmds.nurbsPlane(p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=1, u=2, v=1, ch=1, n=nurb)[0]

            cmds.move(-0.5, 0, 0, n + ".cv[2][0:1]",r=True, os=True, ws=True)
            cmds.move(0.5, 0, 0, n + ".cv[0][0:1]",r=True, os=True, ws=True)

            skTop = cmds.xform(skChain[0],q=1,ws=1,ro=1)
            skLast = cmds.xform(skChain[1],q=1,ws=1,ro=1)
            skMid = [sum([skTop[0], skLast[0]]) / len([skTop[0], skLast[0]]), 
                    sum([skTop[1], skLast[1]]) / len([skTop[1], skLast[1]]), 
                    sum([skTop[2], skLast[2]]) / len([skTop[2], skLast[2]])]
            cmds.rotate(skTop[0], skTop[1], skTop[2], n + ".cv[0][0:1]",a=True, os=True, ws=True)
            cmds.rotate(skMid[0], skMid[1], skMid[2], n + ".cv[1][0:1]",a=True, os=True, ws=True)
            cmds.rotate(skLast[0], skLast[1], skLast[2], n + ".cv[2][0:1]",a=True, os=True, ws=True)

            skTop = cmds.xform(skChain[0],q=1,ws=1,rp=1)
            skMid = cmds.xform(skChain[1],q=1,ws=1,rp=1)
            skLast = cmds.xform(skChain[2],q=1,ws=1,rp=1)

            cmds.move(skTop[0], skTop[1], skTop[2], n + ".cv[0][0:1]",r=True, os=True, ws=True)
            cmds.move(skMid[0], skMid[1], skMid[2], n + ".cv[1][0:1]",r=True, os=True, ws=True)
            cmds.move(skLast[0], skLast[1], skLast[2], n + ".cv[2][0:1]",r=True, os=True, ws=True)

            cmds.rebuildSurface(n, sv=1, su=4, dv=1, du=1)

            return n

        @staticmethod
        def groupAimInfUp(name, side, nurb):
            types = ["aim", "up", "inf"]
            sections = ["mid", "fore"]
            grps = []
            for sec in sections:
                tmp = []
                for t in types:
                    n = "_".join([t, sec + name.capitalize(), side])
                    tmp.append(cmds.group(n=n, em=True))
                grps.append(tmp)
            

            nbShape = cmds.listRelatives(nurb)[0]
            
            gap = 0.25
            for sec in grps:
                for t in sec:
                    posi = cmds.createNode("pointOnSurfaceInfo", n="posi_{}".format(t))
                    cmds.connectAttr(nbShape + ".worldSpace[0]", posi + ".inputSurface")
                    cmds.connectAttr( posi + ".result.position", t + ".translate")
                    u = gap + 0.01 if t.startswith("aim_") else gap
                    v = 0.55 if t.startswith("up_") else 0.5
                    cmds.setAttr(posi + ".parameterU", u)
                    cmds.setAttr(posi + ".parameterV", v)
                gap += 0.5
                cmds.aimConstraint(sec[0], sec[2], aim=[0,1,0], u=[1,0,0], wut="object", wuo=sec[1])

            return [grps[0][2], grps[1][2]]

        @staticmethod
        def createCluster(meshs, nurb, skChain, name, side, radius=1):
            clstPnt = [(skChain[0], skChain[1], "mid{}_{}".format(name.capitalize(), side)),
                    (skChain[1], skChain[2], "fore{}_{}".format(name.capitalize(), side)),
                    (skChain[0], skChain[2], "{}_{}".format(skChain[1].split("_")[1], side))]

            ctrlInf = []
            mesh = meshs.pop(0)
            for cp in clstPnt[:-1]:
                s = MiniToolRig.MT_arc.getVertexZoneName(mesh, cp[0], cp[1], radius=radius)
                clstName, clstHandle = cmds.cluster(s, n="cluster" + cp[2][0].upper() + cp[2][1:])
                MiniToolRig.MT_arc.assignPercentWeigth(mesh, cp[0], cp[1], clstName, radius=radius)

                root, inf, ctrl = MiniToolRig.MT_arc.createStarCtrl("arc_" + cp[2])
                ctrlInf.append(inf)
                toDelete = cmds.pointConstraint(cp[0], cp[1], root, mo=False)
                cmds.delete(toDelete)
                toDelete = cmds.orientConstraint(cp[0], cp[1], root, mo=False)
                cmds.delete(toDelete)
                cmds.disconnectAttr(u'{}.worldMatrix'.format(clstHandle), u'{}.matrix'.format(clstName))
                cmds.disconnectAttr(u'{}Shape.clusterTransforms'.format(clstHandle), u'{}.clusterXforms'.format(clstName))
                cmds.delete(u'{}'.format(clstHandle), u'{}Shape'.format(clstHandle))
                cmds.connectAttr("{}.matrix".format(ctrl),  "{}.weightedMatrix".format(clstName))
                cmds.connectAttr("{}.parentInverseMatrix[0]".format(ctrl),  "{}.bindPreMatrix".format(clstName))
                cmds.connectAttr("{}.parentMatrix[0]".format(ctrl),  "{}.preMatrix".format(clstName))
                cmds.connectAttr("{}.worldMatrix[0]".format(ctrl),  "{}.matrix".format(clstName))
            
            #patch 
            cp = clstPnt[-1]
            s = MiniToolRig.MT_arc.getVertexZoneName(mesh, cp[0], cp[1], radius=radius)
            clstName, clstHandle = cmds.cluster(s, n="cluster" + cp[2][0].upper() + cp[2][1:])
            MiniToolRig.MT_arc.assignPercentWeigth(mesh, cp[0], cp[1], clstName, radius=radius)

            root, inf, ctrl = MiniToolRig.MT_arc.createStarCtrl("arc_" + cp[2])
            ctrlInf.append(inf)
            toDelete = cmds.pointConstraint(skChain[1], root, mo=False)
            cmds.delete(toDelete)
            toDelete = cmds.orientConstraint(skChain[0], skChain[1], root, mo=False)
            cmds.delete(toDelete)
            cmds.disconnectAttr(u'{}.worldMatrix'.format(clstHandle), u'{}.matrix'.format(clstName))
            cmds.disconnectAttr(u'{}Shape.clusterTransforms'.format(clstHandle), u'{}.clusterXforms'.format(clstName))
            cmds.delete(u'{}'.format(clstHandle), u'{}Shape'.format(clstHandle))
            cmds.connectAttr("{}.matrix".format(ctrl),  "{}.weightedMatrix".format(clstName))
            cmds.connectAttr("{}.parentInverseMatrix[0]".format(ctrl),  "{}.bindPreMatrix".format(clstName))
            cmds.connectAttr("{}.parentMatrix[0]".format(ctrl),  "{}.preMatrix".format(clstName))
            cmds.connectAttr("{}.worldMatrix[0]".format(ctrl),  "{}.matrix".format(clstName))

            cmds.sets('{}.cv[1:3][0:1]'.format(nurb), include ="{}Set".format(clstName))
            cmds.percent(clstName, "{}.cv[1:3][0:1]".format(nurb), v=0.5)
            cmds.percent(clstName, "{}.cv[2][0:1]".format(nurb), v=1)

            for mesh in meshs:
                for cp in clstPnt:
                    s = MiniToolRig.MT_arc.getVertexZoneName(mesh, cp[0], cp[1], radius=radius)
                    clstName = "cluster" + cp[2][0].upper() + cp[2][1:]
                    cmds.sets(s, include ="{}Set".format(clstName))
                    MiniToolRig.MT_arc.assignPercentWeigth(mesh, cp[0], cp[1], clstName, radius=radius)

            return ctrlInf

        @staticmethod
        def grpCtrls(ctrl):
            cmds.setAttr(ctrl + ".overrideEnabled",1)
            cmds.setAttr(ctrl + ".overrideColor", 9)
            name = ctrl[2:]
            pose = cmds.group(ctrl, n="pose_" + name, a=True)
            inf = cmds.group(pose, n="inf_" + name, a=True)
            root = cmds.group(inf, n="root_" + name, a=True)
            return root, inf, ctrl

        @staticmethod
        def createStarCtrl(name, pointed=8, strenght=0.09):
            nb = max(3,pointed) * 2
            
            ctrl = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=360, r=1, d=3, ut=0, tol=0.01, s=nb, ch=1, n="c_{}".format(name))[0]
            vtx = ["{}.cv[{}]".format(ctrl, x) for x in range(0, nb, 2)]
            cmds.scale(strenght, strenght, strenght, *vtx, r=True, ocp=True)
            cmds.delete(ctrl, constructionHistory = True)
            return MiniToolRig.MT_arc.grpCtrls(ctrl)

        @staticmethod
        def skinSkToNurb(nurb, chain):
            top = chain[0]
            middle = chain[1]
            end = chain[2]
            middleOri = [x for x in cmds.listRelatives(top) if "Ori_" in x]
            middleOri = middleOri[0] if len(middleOri) == 1 else middle
            middleZero = [x for x in cmds.listRelatives(top) if "0_" in x]
            middleZero = middleZero[0] if len(middleZero) == 1 else middle
            endOri = [x for x in cmds.listRelatives(middle) if "Ori_" in x]
            endOri = endOri[0] if len(endOri) == 1 else end

            skinBones = list(set([top,middle,middleOri,middleZero,endOri]))
            skCls = cmds.skinCluster( skinBones + [nurb])[0]
            cmds.skinPercent( skCls, '{}.cv[0][0:1]'.format(nurb), transformValue=[(top, 1)])
            cmds.skinPercent( skCls, '{}.cv[1][0:1]'.format(nurb), transformValue=[(top, 0.5), (middleOri, 0.5)])
            cmds.skinPercent( skCls, '{}.cv[2][0:1]'.format(nurb), transformValue=[(middleZero, 1)])
            cmds.skinPercent( skCls, '{}.cv[3][0:1]'.format(nurb), transformValue=[(middle, 0.5), (endOri, 0.5)])
            cmds.skinPercent( skCls, '{}.cv[4][0:1]'.format(nurb), transformValue=[(endOri, 1)])

        def createArc(self):
            meshs = self.c_mesh.chain[:]
            memberName = cmds.textField(self.c_memberName, q=True, tx=True)
            side = self.c_side.side
            skChain = self.c_skChain.chain[:]
            radius = cmds.floatField(self.c_radius, q=True, v=True)

            if len(skChain) != 3:
                cmds.error("Please, select at least 3 consecutive bones")

            cmds.progressWindow(title="Arc Creation ", progress=0, status="Starting")
            try:
                nurb = MiniToolRig.MT_arc.CreateNurbSpine(memberName, side, skChain)
                infs = MiniToolRig.MT_arc.groupAimInfUp(memberName, side, nurb)
                ctrlInfs = MiniToolRig.MT_arc.createCluster(meshs, nurb, skChain, memberName, side, radius)
                for i, inf in enumerate(infs):
                    cmds.parentConstraint(inf, ctrlInfs[i], mo=True)
                middleJoints = cmds.listRelatives(skChain[0])
                zero = [x for x in middleJoints if "0_" in x]
                jointMiddle = zero[0] if len(zero) == 1 else skChain[1]
                cmds.parentConstraint(jointMiddle, ctrlInfs[2], mo=True)
                MiniToolRig.MT_arc.skinSkToNurb(nurb, skChain)
            finally:
                cmds.progressWindow(endProgress=True)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)

            self.c_side = self.attach(MiniToolRig.MC_sideSelect(self.layout).load(), top="FORM", right="FORM", margin=(5, 5, 5, 5))
            self.c_memberName = self.attach(cmds.textField(p=self.layout, pht="arm, leg...", ann="Member's name"), top="FORM", left="FORM", right=self.c_side, margin=(5, 5, 5, 5))
            self.c_radius = self.attach(cmds.floatField(p=self.layout, v=1, pre=1), top=self.c_side, right="FORM")
            self.c_radiusLabel = self.attach(cmds.text(p=self.layout, l="radius"), top=self.c_side, right=self.c_radius, margin=(3, 3, 3, 3))
            self.c_skChain = self.attach(MiniToolRig.MC_getChain(self.layout, name="Sk").load(), top=self.c_radius, left="FORM", right=50, margin=(5, 5, 2, 1))
            self.c_mesh = self.attach(MiniToolRig.MC_getChain(self.layout, name="meshs").load(), top=self.c_radius, left=50, right="FORM", margin=(5, 5, 1, 2))
            self.c_generate = self.attach(cmds.button(p=self.layout, l="Generate arc", c=Callback(self.createArc)), bottom="FORM", right="FORM", margin=(5, 5, 5, 2))

            self.applyAttach()

    class MT_options(Module):
        def __init__(self, parent, sections, name=None):
            Module.__init__(self, parent, name=name)
            self.sections = sections
            self.vis = True
            self.vscConnect = cmds.commandPort("localhost:7001", q=True)

        def switch(self):
            self.vis = not self.vis
            cmds.layout(self.layout, e=True, vis=self.vis)

        def secSwitch(self, sec):
            print(sec)
            self.sections[sec].hiddenSwitch()
            stateIcon = "switchOff.png" if self.sections[sec].hidden else "switchOn.png"
            cmds.iconTextButton(self.switchsButtons[sec], e=True, image1=stateIcon)

        def loadAllIconWin(self):
            name = "All Icons"
            if cmds.workspaceControl(name, exists=1):
                cmds.deleteUI(name)
            self.winIcon = cmds.workspaceControl(name, retain=False, iw=840, ih=550, floating=True)

            cl_main = cmds.columnLayout(p=self.winIcon, adj=1)
            self.label =  cmds.textFieldGrp(label="Resources: ", text="click icons to get icon names")
            sl_listIcon = cmds.scrollLayout(verticalScrollBarThickness=16, h=500)
            rcl_list = cmds.rowColumnLayout(numberOfColumns=25)
                
            icons = cmds.resourceManager(nameFilter="*")
            for ico in icons:
                cmds.iconTextButton(w=32, h=32, style="iconOnly", command=Callback(self.updateIconField, self.label, ico), image1=ico)
        
        def updateIconField(self, label, name):
            cmds.textFieldGrp(label, e=True, text=name)

        def SwitchVscConnection(self):
            if self.vscConnect:
                cmds.commandPort(n="localhost:7001", close=True)
                cmds.iconTextButton(self.SyncIconBtn, e=True, image1="syncOff.png")
                info("Disconnected")
            else:
                try:
                    cmds.commandPort(n="localhost:7001", stp="mel", echoOutput=True)
                except:
                    cmds.error("Can't connect to VS code. The connection must be already established with an other instance of maya")
                    pass
                info("Connection Established")
                cmds.iconTextButton(self.SyncIconBtn, e=True, image1="syncOn.png")
            self.vscConnect = not self.vscConnect


        def load(self):
            self.layout = cmds.formLayout("main", p=self.parent, w=5, bgc=[0.4,0.4,0.4], vis=self.vis)
            self.templayout = self.attach(cmds.formLayout("tmp", p=self.layout, w=5), top="FORM", right="FORM", left="FORM")
            last = "FORM"
            h, w = 20, 20
            if type(self.sections) is not dict:
                return
            l = [(k, sec) for k, sec in self.sections.items()]
            l = sorted(l, key=lambda x: x[1].name)
            colorGap = False
            self.switchsButtons = {}
            for k, sec in l:
                if sec is None:
                    continue

                color = 0.3 + 0.1 * colorGap
                colorGap = not colorGap
                line = self.attach(cmds.formLayout(p=self.templayout, h=20, bgc=[color,color,color]), top=last, left="FORM", right="FORM", margin=(2,0,0,0))

                iconLayout = cmds.columnLayout(p=line, w=w, h=h,)
                cmds.iconTextButton(style='iconOnly', w=w, h=h, p=iconLayout, image1=sec.image)
                iconLock = cmds.image(p=line, i="lock.png", vis=sec.locked, ann="you do not have the permission to use this tool")
                iconWip = cmds.image(p=line, i="out_time.png", vis=sec.wip, ann="Work in progress")
                

                stateIcon = "switchOff.png" if sec.hidden else "switchOn.png"
                
                iconSwitch = cmds.iconTextButton(style='iconOnly', w=w, h=h, p=line, image1=stateIcon, c=Callback(self.secSwitch, k))
                self.switchsButtons[k] = iconSwitch
                title = cmds.text(p=line, l=sec.name)
                
                cmds.formLayout(line, e=True, af=[(iconLayout, "top", 0), (iconLayout, "left", 5),
                                                  (iconSwitch, "top", 0), (iconSwitch, "right", 2),
                                                  (iconLock, "top", 0), 
                                                  (iconWip, "top", 0),
                                                  (title, "top", 5)],
                                              ac=[(title, "left", 5, iconLayout),
                                                  (iconLock, "right", 5, iconSwitch),
                                                  (iconWip, "right", 5, iconLock),
                                                  ])


                last = line

            self.showIconBtn = self.attach(cmds.iconTextButton(p=self.layout, image1="iconLarge.png", c=self.loadAllIconWin), top=self.templayout, left="FORM")
            cntIcon = "syncOn.png" if self.vscConnect else "syncOff.png"
            self.SyncIconBtn = self.attach(cmds.iconTextButton(p=self.layout, image1=cntIcon, c=self.SwitchVscConnection), top=self.showIconBtn, left="FORM")
            self.applyAttach()
            # cmds.formLayout(self.layout, e=True, af=[(self.templayout, "top", 0), (self.templayout, "bottom", 0), (self.templayout, "left", 0), (self.templayout, "right", 0)])

    class MT_follows(Module):
        presetMainTarget = "c_FLY"
        presetTarget = ["c_FK_head", "c_IK_chest", "c_IK_pelvis", "c_WORLD"]

        @staticmethod
        def getInfParent(e):
            p = cmds.listRelatives(e, p=True)
            if p is None or len(p) < 1:
                return None
            if p[0].startswith("inf_"):
                return p[0]
            return MiniToolRig.MT_follows.getInfParent(p[0])

        def applyFollows(self, const):
            CONSTRAINT = ["parentConstraint", "pointConstraint"]
            ctrls = self.c_ctrls.chain
            targets = self.c_targets.chain
            print("="*10)
            print(ctrls)
            print(targets)
            mainTarget = cmds.textField(self.c_main, q=True, tx=True)
            targets = [mainTarget] + targets
            print(targets)
            for c in ctrls:
                inf = MiniToolRig.MT_follows.getInfParent(c)
                if inf is None:
                    continue
                cmds.addAttr(c, longName='parent', attributeType='enum', en=" ", k=True)
                for i, t in enumerate([t for t in targets if cmds.objExists(t)]):
                    if t.endswith("_L") or t.endswith("_R"):
                        elems = t.split("_")[-2:]
                        elems = [x.capitalize() for x in elems]
                        name = "".join(elems)
                    else:
                        elems = t.split("_")[-1:]
                        elems = [x.capitalize() for x in elems]
                        name = "".join(elems)
                    tName = inf.replace("inf_", "tgt_") + "_" + name
                    # name = name.lower()
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
                        print(c + '.follow' + name)
                        cmds.addAttr(c, longName='follow' + name, defaultValue=0, minValue=0, maxValue=1, k=True)
                        
                        cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1." + Wname, 1)
                        cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 1)
                        cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1.reverseroot", cd=inf + "_" + CONSTRAINT[const] + "1." + Wname)

                        cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1." + Wname, 0)
                        cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 0)
                        cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1.reverseroot", cd=inf + "_" + CONSTRAINT[const] + "1." + Wname)
                        cmds.connectAttr( c + '.follow' + name, inf + "_" + CONSTRAINT[const] + "1." + Wname)
                        # reinitialisation de precaution 
                        print(c + '.follow' + name)
                        cmds.setAttr(c + '.follow' + name, 1)
                        cmds.setAttr(c + '.follow' + name, 0)

        def applyPreset(self):
            cmds.textField(self.c_main, e=True, tx=self.presetMainTarget)
            self.c_targets.setChain(self.presetTarget)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            self.c_main = cmds.textField(p=self.layout, pht="Default target", ed=False)
            self.c_setMain = cmds.button(p=self.layout, l="Set" )
            self.c_setPreset = cmds.button(p=self.layout, l="Preset", c=Callback(self.applyPreset))
            self.c_targets = MiniToolRig.MC_getChain(self.layout, name="Targets").load()
            self.c_ctrls = MiniToolRig.MC_getChain(self.layout, name="ctrls").load()
            self.c_applyParent = cmds.button(p=self.layout, l="parent", c=Callback(self.applyFollows, 0))
            self.c_applyPoint = cmds.button(p=self.layout, l="point", c=Callback(self.applyFollows, 1))

            # self.c_targets.chain = self.defaultTarget
            # self.c_targets.load()

            self.attach(self.c_setPreset, top="FORM", left="FORM", margin=(5, 5, 2, 1))
            self.attach(self.c_main, top=self.c_setPreset, left="FORM", right=self.c_setMain, margin=(5, 5, 2, 1))
            self.attach(self.c_setMain, top=self.c_setPreset, right="FORM", margin=(5, 5, 2, 1))
            self.attach(self.c_targets, top=self.c_setMain, left="FORM", right=50, margin=(5, 5, 2, 1))
            self.attach(self.c_ctrls, top=self.c_setMain, left=50, right="FORM", margin=(5, 5, 2, 1))
            self.attach(self.c_applyParent, bottom="FORM", right=self.c_applyPoint, margin=(5, 5, 1, 2))
            self.attach(self.c_applyPoint, bottom="FORM", right="FORM", margin=(5, 5, 1, 2))

            self.applyAttach()

    class MT_nurbs(Module):

        def setNurbsSel(self, t):
            pass

        def load(self):
            self.layout = cmds.formLayout(p=self.parent)
            
            self.b_DnSet = self.attach(cmds.button(p=self.layout, label="Set", en=True, c=Callback(self.setNurbsSel, "LTF_Up")), top="FORM", right="FORM")
            self.t_Dn = self.attach(cmds.text(p=self.layout, label="Dn"), top="FORM", left="FORM")
            self.tf_Dn = self.attach(cmds.textField(p=self.layout, ed=False), top="FORM", left=self.t_Dn, right=self.b_DnSet, margin=(0,0,3,0))
            self.b_UpSet = self.attach(cmds.button(p=self.layout, label="Set", en=True, c=Callback(self.setNurbsSel, "LTF_Up")), top=self.b_DnSet, right="FORM")
            self.t_Up = self.attach(cmds.text(p=self.layout, label="Up"), top=self.b_DnSet, left="FORM")
            self.tf_Up = self.attach(cmds.textField(p=self.layout, ed=False), top=self.b_DnSet, left=self.t_Up, right=self.b_UpSet, margin=(0,0,3,0))

            self.t_Name = self.attach(cmds.text(p=self.layout, label="Name"), top=self.b_UpSet, left="FORM")
            self.tf_Name = self.attach(cmds.textField(p=self.layout, tx="spine"), top=self.b_UpSet, left=self.t_Name , right="FORM", margin=(0,0,3,0))
            self.t_nb = self.attach(cmds.text(p=self.layout, label="Nb"), top=self.tf_Name, left="FORM")
            self.if_nb = self.attach(cmds.intField(p=self.layout, v = 3, w=50), top=self.tf_Name, right="FORM")

            self.b_CreateNurbs = self.attach(cmds.button(p=self.layout, label="Create Nurbs", en=True, c=Callback(None)), top=self.if_nb, left="FORM", right="FORM")
            self.b_createJoints = self.attach(cmds.button(p=self.layout, label="Create Joints", en=True, c=Callback(None)), top=self.b_CreateNurbs, left="FORM", right="FORM")
            self.applyAttach()

    class MTG_blendshapes(Module):
        
        def transfertBlendshape(self):
            sel = cmds.ls(sl=True)
            if len(sel) != 2:
                return
            src = sel[0]
            dst = sel[1]
            originPos = cmds.xform(src, q=True, t=True)
            bbox = cmds.exactWorldBoundingBox(dst)
            width = abs(bbox[0] - bbox[3])
            height = abs(bbox[1] - bbox[4])
            print(bbox, width, height)
            pcTmp = cmds.parentConstraint(dst, src, mo=False)
            cmds.delete(pcTmp)
            cmds.select(cl=True)
            cmds.select(dst, src)
            cmds.CreateWrap()
            history = cmds.listHistory(src)        
            blendshapes = cmds.ls(history, type='blendShape')
            history = cmds.listHistory(dst)  
            wrapDef = cmds.ls(history, type='wrap')
            weights = cmds.listAttr(blendshapes[0] + '.w' , m=True)
            for i, w in enumerate(weights):
                print(w)
                cmds.setAttr(blendshapes[0] + "." + w, 1)
                dup = cmds.duplicate(dst, n=w)[0]
                for attr in cmds.listAttr(dup, k=True):
                    cmds.setAttr("{}.{}".format(dup, attr), lock=False)
                cmds.setAttr("{}.tx".format(dup), (i / 2) * width + width)
                if w.endswith("_R"):
                    cmds.setAttr("{}.ty".format(dup), height * 2)
                    cmds.setAttr("{}.tx".format(dup), (i / 2) * width + width)
                else:
                    cmds.setAttr("{}.ty".format(dup), height)

                cmds.setAttr(blendshapes[0] + "." + w, 0)
            cmds.delete(wrapDef)

            cmds.xform(src, t=originPos)
        
        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            self.transfertBsButton = self.attach(cmds.iconTextButton(p=self.layout, i="out_transform.png", c=Callback(self.transfertBlendshape)), top="FORM", left="FORM")
            self.applyAttach()

    class MTG_skin(Module):
        def load(self):
            self.layout = cmds.formLayout(p=self.parent, w=5)
            self.transfertBsButton = self.attach(cmds.iconTextButton(p=self.layout, i="out_transform.png", c=Callback(self.transfertBlendshape)), top="FORM", left="FORM")
            self.applyAttach()


    ####################################
    #    core of the main Interface    #
    ####################################

    class Section(Module):
        tmp = True
        def __init__(self, parent, name, image="out_bulge.png", locked=False, wip=False):
            Module.__init__(self, parent, name)
            self.image = image
            self.hidden = False
            self.collapsed = False
            self.greyedOut = False

            self.locked = locked
            self.wip = wip

        def __setattr__(self, name, value):
                Module.__setattr__(self, name, value)
                if name == "locked":
                    self.collapsed = self.locked
                    self.greyedOut = self.locked or self.greyedOut
                if name == "wip":
                    self.hidden = self.wip
                    self.greyedOut = self.wip or self.greyedOut

        def parentCollapseSwitch(self):
            self.runEvent("parentCollapseSwitch")

        def collapseSwitch(self, state=None):
            if state is None:
                self.collapsed = not self.collapsed
            else :
                self.collapsed = state
            cmds.layout(self.childrenLayout, e=True, vis=not self.collapsed)

        def hiddenSwitch(self):
            self.hidden = not self.hidden
            cmds.layout(self.layout, e=True, vis=not self.hidden)

        def move(self, other):
            Module.move(self, other)
            for i, c in enumerate(self.parent.childrens):
                col = 0.25 + 0.05 * (i % 2)
                cmds.layout(c.layout, e=True, bgc=[col, col, col])

        def load(self):
            self.clearAttach()
            if not self.hidden:
                MiniToolRig.Section.tmp = not MiniToolRig.Section.tmp
            c = 0.25 + 0.05 * MiniToolRig.Section.tmp
            self.layout = cmds.formLayout(self.name, p=self.parent, bgc=[c, c, c], dgc=Callback(self._dragCb).getCommandArgument(), dpc=Callback(self._dropCb).getCommandArgument(), en=True, vis=not self.hidden) 
            self.iconLayout = self.attach(cmds.columnLayout(p=self.layout, w=30, h=30,), top="FORM", left="FORM")
            self.icon = cmds.iconTextButton(style='iconOnly', w=30, h=30, p=self.iconLayout, image1=self.image, c=Callback(self.collapseSwitch),dcc=Callback(self.parentCollapseSwitch))
            self.childrenLayout = self.attach(cmds.columnLayout(p=self.layout, adj=True, bgc=[0.2, 0.2, 0.2], vis=not self.collapsed, en=not self.locked), top=self.iconLayout, left="FORM", right="FORM", margin=(5,5,5,5))
            
            self.lockStatus = self.attach(cmds.image(p=self.layout, i="lock.png", h=30, w=30, vis=self.locked), top="FORM", right="FORM")
            self.wipStatus = self.attach(cmds.image(p=self.layout, i="out_time.png", h=30, w=30, vis=self.wip), top="FORM", right=self.lockStatus)
            annotation = "\n| [LOCKED] You do not have permission to use this tools" * self.locked + "\n| [WIP] Use with caution\n" * self.wip
            if self.locked or self.wip:
                cmds.formLayout(self.layout, e=True, ann=annotation)
            self.title = self.attach(cmds.text(p=self.layout, l=self.name, align="left"), top="FORM", left=self.iconLayout, right="FORM", bottom=self.childrenLayout)

            for c in self.childrens:
                c.load()

            self.applyAttach()

    class Tabs(Module):
        def __init__(self, parent, name):
            Module.__init__(self, parent, name)
            self.childrens = []
            self.nbColumn = -1

        def refresh(self):
            self.reformatChildLay()

        def resize(self):
            nbc = self.width / 240
            if nbc != self.nbColumn:
                self.nbColumn = max(nbc, 1)
                self.reformatChildLay()

        def reformatChildLay(self):
            if self.childrenLayout is None:
                return
            layout = self.childrenLayout
            ap, af, ac, an = [], [], [], []
            gap = 100 / self.nbColumn
            height = sum([x.height for x in self.childrens])
            heightPerColumn = height / self.nbColumn

            total_h = 0
            side_top = None
            side_left = None
            col = 0
            side_right = gap * (col + 1) if self.nbColumn - 1 != col else None
            for c in self.childrens:
                total_h += c.height
                if side_top == None:
                    af.append((c.layout, "top", 0))
                else:
                    ac.append((c.layout, "top", 2, side_top))
                if side_left == None:
                    af.append((c.layout, "left", 0))
                else:
                    ap.append((c.layout, "left", 2, side_left))
                if side_right == None:
                    af.append((c.layout, "right", 0))
                else:
                    ap.append((c.layout, "right", 2, side_right))
                an.append((c.layout, "bottom"))

                
                side_top = c.layout
                if total_h > heightPerColumn:
                    total_h = 0
                    side_top = None
                    col += 1
                    side_left = gap * col
                    side_right = gap * (col + 1) if self.nbColumn - 1 != col else None
            cmds.formLayout(layout, e=True, ap=ap, af=af, ac=ac, an=an)

        def load(self):
            self.layout = cmds.formLayout(self.name, p=self.parent)
            self.scrollLayout = self.attach(cmds.scrollLayout(p=self.layout, w=1, cr=True, rc=Callback(self.resize)), top="FORM", left="FORM", right="FORM", bottom="FORM")
            self._tmpLayout = cmds.formLayout(p=self.scrollLayout)
            # self.childrenLayout = cmds.columnLayout(p=self._tmpLayout, adj=True, w=1)
            self.childrenLayout = cmds.formLayout(p=self._tmpLayout)
            cmds.formLayout(self._tmpLayout, e=True, af=[(self.childrenLayout, "top", 0), (self.childrenLayout, "bottom", 0), (self.childrenLayout, "left", 0), (self.childrenLayout, "right", 0)])

            for c in self.childrens:
                c.load()
            self.reformatChildLay()
            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)
            
    sections_order = ["naming", "transform", "constraint", "coloring", "construction", "squeletton", "additionalJoint", "controllers", "ik", "switch", "nurbs", "follow", "still", "arc", "blendshape"]

    def __init__(self):
        Module.__init__(self, None) 

        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)
        self._scriptJobIndex = []
        self.pannel_rig = ""

        self.defineSections()

    def displayOption(self):
        self.optionModule.switch()
        cmds.layout(self.optLayout.layout, e=True, vis=self.optionModule.vis)

    def openDoc(self):
        webbrowser.open("https://mirror-flyaway-413.notion.site/MiniToolRig-Doc-314f657689aa4e54a47428c093e0a3cd")

    def sendTicket(self):
        subject = "[Ticket] // MiniTool-Rig v{}// [...]".format(__version__)
        subject = urllib.quote_plus(subject)
        body = r"Your message here%0D%0AChange the [...] in the subject to the name of the issue%0D%0ABe precise, short and nice"
        # body = "%0D%0A".join(body.splitlines())
        webbrowser.open("mailto:{}?subject={}&body={}".format(__email__, subject, body))

    def cs_defineLockState(self):
        '''Function to limit Creative seeds' student
        
        
        Si tu t'es donné•e la peine d'aller jusqu'ici pour dévérouiller des options bonus
        tu le mérite amplement ;)
        Ajoute ton nom dans le authorizedUser
        '''
        authorizedUser = ["a.paris", "y.genty"]
        user = getpass.getuser()
        present = datetime.datetime.now()
        yearsPermission = [
            [],
            ["naming", "transform", "constraint", "coloring"],
            ["naming", "transform", "constraint", "coloring", "construction", "squeletton", "additionalJoint", "controllers"],
            ["naming", "transform", "constraint", "coloring", "construction", "squeletton", "additionalJoint", "controllers", "ik", "switch", "nurbs", "follow", "still", "arc", "blendshape"],
            ["naming", "transform", "constraint", "coloring", "construction", "squeletton", "additionalJoint", "controllers", "ik", "switch", "nurbs", "follow", "still", "arc", "blendshape"],
        ]

        if not os.path.exists("Q:/"):
            return self.sections_order[:]
            
        if present < datetime.datetime(2022, 1, 31):
            return self.sections_order[:]


        if user in authorizedUser:
            return self.sections_order[:]

        for y in range(1, 6):
            if not os.path.exists("Q:/annee0{}/casiers".format(y)):
                continue
            if user in os.listdir("Q:/annee0{}/casiers".format(y)):
                break

        return yearsPermission[y - 1]

    def defineSections(self):
        self.sections = {}

        self.sections["construction"] = MiniToolRig.Section(self.pannel_rig, "Construction", "locator.svg")  
        self.sections["squeletton"] = MiniToolRig.Section(self.pannel_rig, "Squeletton", "HIKCharacterToolSkeleton.png")  
        self.sections["additionalJoint"] = MiniToolRig.Section(self.pannel_rig, "Additional Joint", "ikRPsolver.svg")  
        self.sections["naming"] = MiniToolRig.Section(self.pannel_rig, "Naming", "renamePreset_100.png")  
        self.sections["constraint"] = MiniToolRig.Section(self.pannel_rig, "Constraint", "out_aimConstraint.png")  
        self.sections["transform"] = MiniToolRig.Section(self.pannel_rig, "Transform", "holder.svg")  
        self.sections["controllers"] = MiniToolRig.Section(self.pannel_rig, "Controllers", "polySuperEllipse.png")  
        self.sections["coloring"] = MiniToolRig.Section(self.pannel_rig, "Coloring", "colorProfile.png")  
        self.sections["ik"] = MiniToolRig.Section(self.pannel_rig, "Ik", "ikHandle.svg", wip=True) 
        self.sections["switch"] = MiniToolRig.Section(self.pannel_rig, "Switch", "redrawPaintEffects.png", wip=True) 
        self.sections["nurbs"] = MiniToolRig.Section(self.pannel_rig, "Nurbs", "nurbsSurface.svg", wip=True) 
        self.sections["arc"] = MiniToolRig.Section(self.pannel_rig, "Arcs", "motionTrail.png")  
        self.sections["follow"] = MiniToolRig.Section(self.pannel_rig, "Follows", "menuIconFocus.png")  
        self.sections["still"] = MiniToolRig.Section(self.pannel_rig, "Stills", "nodeGrapherDockBack.png", wip=True) 
        self.sections["blendshape"] = MiniToolRig.Section(self.pannel_rig, "BlendShapes", "blendShape.png", wip=True) 

        MiniToolRig.MG_construction(self.sections["construction"])
        MiniToolRig.MT_squeletton(self.sections["squeletton"])
        MiniToolRig.MT_additional(self.sections["additionalJoint"])
        MiniToolRig.MT_naming(self.sections["naming"])
        MiniToolRig.MGT_controller(self.sections["controllers"])
        MiniToolRig.MGT_constraintGroup(self.sections["constraint"])
        MiniToolRig.MG_transformGroup(self.sections["transform"])
        MiniToolRig.MT_coloring(self.sections["coloring"])
        MiniToolRig.MG_ikGroup(self.sections["ik"])
        MiniToolRig.MT_switch(self.sections["switch"])
        MiniToolRig.MT_follows(self.sections["follow"])
        MiniToolRig.MT_nurbs(self.sections["nurbs"])
        MiniToolRig.MT_arc(self.sections["arc"])
        MiniToolRig.MTG_blendshapes(self.sections["blendshape"])

        unlockSection = self.sections_order[:]
        if self.cs_defineLockState():
            unlockSection = ["naming", "transform", "constraint", "coloring", "squeletton", "construction", "controllers"]
        unlockSection = self.cs_defineLockState()
        for k, i in self.sections.items():
            if k not in unlockSection:
                i.locked = True

    def collapsAllSection(self):
        state = 0
        for name in self.sections_order:
            if name in self.sections.keys():
                state = max(int(self.sections[name].collapsed), state)

        for name in self.sections_order:
            if name in self.sections.keys():
                self.sections[name].collapseSwitch(not bool(state))

    # Loading methods
    def load(self):
        '''loading The window
        '''
        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=700, iw=250, retain=False, floating=True, h=700, w=250)

        # Call self.killJobs if the windows is killed
        cmds.scriptJob(ro=True, uid=[self.win, Callback(self._killJobs)])
        self._loadJobs()

        self.layout = cmds.formLayout(p=self.win)
        self.optionButton = self.attach(cmds.iconTextButton(style='iconOnly', w=30, h=30, p=self.layout, ann="Options", image1="advancedSettings.png", c=Callback(self.displayOption)), bottom="FORM", right="FORM")
        
        self.helpButton = self.attach(cmds.iconTextButton(style='iconOnly', w=30, h=30, p=self.layout, ann="About", image1="help.png", c=Callback(self.openDoc)), bottom="FORM", right=self.optionButton)
        self.ticketButton = self.attach(cmds.iconTextButton(style='iconOnly', w=30, h=30, p=self.layout, ann="Send ticket", image1="SP_FileIcon.png", c=Callback(self.sendTicket)), bottom="FORM", right=self.helpButton)
        self.childrenLayout = self.attach(cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5), top="FORM", left="FORM", right="FORM", bottom=self.optionButton)
        self.optLayout = self.attach(MiniToolRig.Tabs(self.layout, "Option").load(), top=50, left="FORM", right="FORM", bottom=self.optionButton)
        self.optionModule = MiniToolRig.MT_options(self.optLayout, self.sections).load()
        self.displayOption()

        self.pannel_rig = MiniToolRig.Tabs(self.childrenLayout, "Rig").load()
        # self.pannel_mod = MiniToolRig.Tabs(self.tabs, "Mod").load()
        
        self.applyAttach()
        for name in self.sections_order:
            if name in self.sections.keys():
                self.sections[name].setParent(self.pannel_rig)
                self.sections[name].load()
                self.sections[name].eventHandler("parentCollapseSwitch", self.collapsAllSection)

    def unload(self):
        if self.win == None:
            return self
        cmds.deleteUI(self.win)
        return self
    # Jobs
    def _loadJobs(self):
        '''Load all jobs
        '''
        # Example : 
        # self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))

    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)

if __name__ == "__main__":
    if sys.executable.endswith(u"bin\maya.exe"):
        print("load Minitool rig")
        plop = MiniToolRig()
        print(plop.__repr__())
        plop.load()
    else:
        print("display version")
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)

def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    MiniToolRig().load()

def initializePlugin(*args):
    '''To load the tool as a plugin
    '''
    MiniToolRig().load()

def uninitializePlugin(*args):
    MiniToolRig().unload()
