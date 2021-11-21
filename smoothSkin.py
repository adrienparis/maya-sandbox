#!/usr/bin/env python

"""smoothSkin.py: Tools to create linear influence of two joint to selected mesh"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.0a1.dev1"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
import math
# pylint: disable=F0401
import maya.cmds as cmds
import maya.mel as mel
# define the global local scale of the name object

class SmoothSkin(object):
    # Callback function
    __cbFuncNum = 0
    __cbFunc = {}
    @staticmethod
    def Callback(func, *args, **kwargs):
        '''callback function to be called when using maya interface system
        to keep object as an object and not as a string
        '''
        if callable(func):
            SmoothSkin.__cbFuncNum += 1
            SmoothSkin.__cbFunc[SmoothSkin.__cbFuncNum - 1] = [func, args, kwargs]
            return "SmoothSkinWin.Callback(" + str(SmoothSkin.__cbFuncNum)  + ")"
        SmoothSkin.__cbFunc[func - 1][0](*SmoothSkin.__cbFunc[func - 1][1], **SmoothSkin.__cbFunc[func - 1][2])

    # Name of the application
    name = u"Skin Smoother"


    def __init__(self):
        self.win = None
        self.vtxSelection = SmoothSkin.GrpVTX()


    class Line(object):
        ''' Piece of user interface that can be added to another UI element
            parent: Must be a SmoothSkin class object
            layout: may formLayout
            name: name of the attribute you want
            annotation: Explication text
            color: [r, g, b] where r,g,b are float between 0 and 1            
            type: "PICKER" / "TEXT" 
        '''
        def __init__(self, parent, layout, name, annotation="", color=[0.32, 0.52, 0.65], type="PICKER", callbackEvent=None):
            self.name = name
            self.color = color
            self.parentClass = parent
            self.parentLay = layout
            self.value = ""
            self.layout = None
            self.callback = callbackEvent
            self.valueText = None
            self.titleText = None
            self.annotations = annotation
            self.type = type
            self.load()

        def setValue(self, value):
            self.value = value
            if self.valueText == None:
                return
            if self.type == "PICKER":
                cmds.text(self.valueText, e=True, label=self.value )
            elif self.type == "TEXT":
                cmds.textField(self.valueText, e=True, text=self.value )
            if self.callback is not None:
                self.callback(self.name, self.value)

        def setColor(self, color):
            self.color = color
            if self.titleText == None:
                return
            cmds.text(self.titleText, e=True, bgc=self.color )

        def load(self):
            self.layout = cmds.formLayout(p=self.parentLay, bgc=[0.32, 0.32, 0.32], ann=self.annotations.capitalize())
            self.titleText = cmds.text(p=self.layout, label=" " + self.name.capitalize() + " : ", bgc=self.color )
            if self.type == "PICKER":
                self.valueText = cmds.text(p=self.layout, label=self.value, bgc=[0.275, 0.275, 0.275], align='left')
                self.clsBtn = cmds.button(parent=self.layout, label="cls", c=SmoothSkin.Callback(self.clsBtnAct), en=True)
                self.setBtn = cmds.button(parent=self.layout, label="set", c=SmoothSkin.Callback(self.setBtnAct))
                cmds.formLayout(self.layout, e=True,
                                af=[(self.titleText, "left", 3), (self.titleText, "top", 3), (self.titleText, "bottom", 3),
                                    (self.valueText, "top", 3), (self.valueText, "bottom", 3),
                                    (self.clsBtn, "top", 3),  (self.clsBtn, "bottom", 3),
                                    (self.setBtn, "top", 3), (self.setBtn, "right", 3), (self.setBtn, "bottom", 3)
                                    ],
                                ac=[(self.valueText, "left", 3, self.titleText),(self.valueText, "right", 3, self.clsBtn),
                                    (self.clsBtn, "right", 3, self.setBtn)]
                )
            elif self.type == "TEXT":
                # self.valueText = cmds.textField(p=self.layout, text=self.value, bgc=[0.275, 0.275, 0.275], cc="print('plop')")
                self.valueText = cmds.textField(p=self.layout, text=self.value, bgc=[0.275, 0.275, 0.275], cc=SmoothSkin.Callback(self.valueTextCcAct))
                cmds.formLayout(self.layout, e=True,
                                af=[(self.titleText, "left", 3), (self.titleText, "top", 3), (self.titleText, "bottom", 3),
                                    (self.valueText, "top", 3), (self.valueText, "bottom", 3), (self.valueText, "right", 3),
                                    ],
                                ac=[(self.valueText, "left", 3, self.titleText)]
                )

        def valueTextCcAct(self):
            self.value = cmds.textField(self.valueText, q=True, text=True)
            self.callback(self.name, self.value)

        def setBtnAct(self):
            sl = cmds.ls(sl=True)
            if len(sl) == 1:
                self.value = sl[0]
            cmds.text(self.valueText, e=True, label=self.value)
            if self.callback is not None:
                self.callback(self.name, self.value)

        def clsBtnAct(self):
            self.value = ""
            cmds.text(self.valueText, e=True, label=self.value)
            if self.callback is not None:
                self.callback(self.name, self.value)



    class SkJoin():
        def __init__(self, name, parent=None):
            #attrs
            self.longName = name
            if cmds.attributeQuery("liw", node=self.longName, ex=True):
                cmds.setAttr(self.longName + ".liw",  0)
            self.visibility = cmds.getAttr(name + ".v")

            self.side = "L" if self.longName.endswith("_L") else "R" if self.longName.endswith("_R") else  ""
            self.particule = ""
            self.pos = cmds.xform(name,q=1,ws=1,rp=1)

            #relatives
            self.parent = None
            self.setParent(parent)
            self.children = []
            self.mirror = None
            self.__getChildren()

            self.name = name

        def __getChildren(self):
            allChildren = cmds.listRelatives(self.longName, typ="joint")
            if allChildren is None:
                return None
            for c in allChildren:
                j = SmoothSkin.SkJoin(c, parent=self)
                j.setParent(self)
            for c in self.children:
                c.getShortName()

        # Parenting methodes
        def setParent(self, parent):
            oldParent = self.parent
            self.parent = parent
            if oldParent is not None:
                oldParent.__delChildren(self)
            if self.parent is not None:
                self.parent.__addChildren(self)

        def __addChildren(self, child):
            self.children.append(child)
        def addChildren(self, child):
            child.setParent(self)

        def __delChildren(self, child):
            self.children.remove(child)
        def delChildren(self, child):
            child.setParent(None)

        def getShortName(self):
            if self.name.startswith("sk_"):
                self.name = self.name[3:]
            if self.name.endswith("_L") or self.name.endswith("_R"):
                self.name = self.name[:-2]
            if not self.visibility:
                if self.parent is not None:
                    for s in self.parent.children:
                        if s == self:
                            continue
                        if s.name in self.longName and s.particule == "" and s.side == self.side:
                            self.particule = self.name.replace(s.name, "").replace("_", "")
                            self.name = s.name

        def getSibblings(self):
            if self.parent == None:
                return []
            siblings = self.parent.children[:]
            siblings.remove(self)
            siblings = [x for x in siblings if x.name == self.name]
            return siblings

        @staticmethod
        def printTree(sk, depth=0):
            print("  " * depth + sk.name + "   " + sk.particule + "   " + sk.side + " ")
            for c in sk.children:
                SmoothSkin.SkJoin.printTree(c, depth + 1)

        @staticmethod
        def treeToList(tree):
            childs = [tree]
            for c in tree.children:
                # childs.append(c)
                childs += SmoothSkin.SkJoin.treeToList(c)
            return childs

        def getDistFrom(self, pos):
            return math.sqrt((self.pos[0] - pos[0])**2 + (self.pos[1] - pos[1])**2 + (self.pos[2] - pos[2])**2)

        def __repr__(self):
            return self.longName

    class GrpVTX(object):
        def __init__(self):
            self.vtxs = []
            self.autoSelect = False
            self.center = [0, 0, 0]
            self._events = {}

        def enableAutoSelect(self):
            self.job = cmds.scriptJob(e=["SelectionChanged", self.updateSelection])
            self.autoSelect = True

        def disableAutoSelect(self):
            if not self.autoSelect:
                return
            cmds.scriptJob(kill=self.job)
            self.autoSelect = False

        def getSkinCluster(self, vtx):
            obj = vtx.split(".")[0]
            shp = obj.split("|")[-1]+ "Shape"
            shapeNode = obj + "|" + shp
            histList = cmds.listHistory(obj)
            if histList:
                for histItem in histList:
                    if cmds.objectType(histItem) == "skinCluster":
                        return histItem


        def getInfluentJoints(self, vtx, skinCluster):
            weights = cmds.skinPercent( skinCluster, vtx, query=True, value=True)
            joints = cmds.skinCluster( skinCluster, q=True, inf=True)
            jointWeight = {}
            for j, w in zip(joints, weights):
                if w < 0.001:
                    continue
                jointWeight[j] = w
            return jointWeight

        def setInfluentJoints(self, joints):
            w = []
            for k, v in joints.items():
                w.append((str(k), v))
                cmds.setAttr(k.longName + ".liw",  0)
            for v in self.vtxs:
                skCls = self.getSkinCluster(v)
                # cmds.skinCluster(skCls, e=True, lw=False)
                cmds.skinPercent( skCls, v, transformValue=w)

        def updateSelection(self):
            sel = cmds.ls(sl=True, o=True)
            self.vtxs = []
            for s in sel:
                self.vtxs += SmoothSkin.GrpVTX.selectVertices(s)
            self.getCenter()
            self.runEvent("SelectionUpdated", self)

        def eventHandler(self, event, function, *args):
            """Execute the given command when the UC call an [Event]
                event: type of Event
                function : function you want to call (some event might send more argument than your function ask)
                *args: Other argument you want to give
            """
            if not event in self._events:
                self._events[event] = []
            self._events[event].append((function, args))
        def runEvent(self, event, *args):
            """Manually run an event
            """
            if not event in self._events:
                return
            for c in self._events[event]:
                if c[0] is None:
                    # cmds.error("Event \"" + event + "\" call a function not implemented yet -WIP-")
                    log.debug.warning("Event \"" + event + "\" call a function not implemented yet -WIP-")
                    continue
                a = c[1] + args
                c[0](*a)

        @staticmethod
        def selectVertices(sel):
            sel_vtx = cmds.ls('{}.vtx[:]'.format(sel), fl=True, sl=True)
            sel_edg = cmds.ls('{}.e[:]'.format(sel), fl=True, sl=True)
            if len(sel_vtx) == 0:
                sel_vtx = cmds.polyListComponentConversion( sel_edg, tv=True)
            new_list = []
            for vtx in sel_vtx:
                if not(vtx.find(':') == -1):
                    num_vtx = vtx[vtx.find('[') + 1:vtx.find(']')]
                    if ':' in num_vtx:
                        start = int(num_vtx[num_vtx.find('[') + 1:num_vtx.find(':')])
                        end = int(num_vtx[num_vtx.find(':') + 1:num_vtx.find(']')])
                    else:
                        start = int(num_vtx)
                        end = start

                    name = vtx[0:vtx.find('[') + 1]
                    l = []
                    for i in range(start, end + 1):
                        l.append((name + str(i) + ']').decode('unicode-escape'))
                    new_list = new_list + l
                else:
                    new_list.append(vtx)
            print(new_list)
            return new_list

        def getCenter(self):
            vmax = [-99999,-99999,-99999]
            vmin = [99999,99999,99999]
            
            for vtx in self.vtxs:
                tmp = cmds.xform(vtx, q=True, ws=True, t=True)[:3]
                vmin = [min(vmin[i], tmp[i]) for i in range(len(vmin))]
                vmax = [max(vmax[i], tmp[i]) for i in range(len(vmax))]

            self.center = [vmax[i] + vmin[i] for i in range(len(vmax))]
            self.center = [self.center[i] / 2 for i in range(len(self.center))]
            return self.center

    class pointInZone:
        def __init__(self, A, B):
            self.A = A[:]
            self.B = B[:]
            #vecteur AB
            self.AB = [self.B[i] - self.A[i] for i in range(len(self.A))]
            #norme du vecteur AB
            self.normeAB =  math.sqrt((self.AB[0]*self.AB[0]) + (self.AB[1]*self.AB[1]) + (self.AB[2]*self.AB[2]))
            #vecteur AB normalise
            self.u = [self.AB[i] / self.normeAB for i in range(len(self.AB))]
        def isPointBetween(self, M):
            #vecteur AM
            AM = [M[i] - self.A[i] for i in range(len(self.A))]
            #produit scalaire p=u.AM
            p = self.u[0] * AM[0] + self.u[1] * AM[1] + self.u[2] * AM[2]
            return 0<=p and p<=self.normeAB

        def percentPointBetween(self, M):
            #vecteur AM
            AM = [M[i] - self.A[i] for i in range(len(self.A))]
            #produit scalaire p=u.AM
            p = self.u[0] * AM[0] + self.u[1] * AM[1] + self.u[2] * AM[2]
            return p / self.normeAB

    def execute(self):
        print(self.jointStartInputLay.value)
        print(self.jointEndInputLay.value)
        self.jStart = SmoothSkin.SkJoin(self.jointStartInputLay.value)
        self.jEnd = SmoothSkin.SkJoin(self.jointEndInputLay.value)
        self.zone = SmoothSkin.pointInZone(self.jStart.pos, self.jEnd.pos)
        self.vtxSelection.updateSelection()
        print(self.vtxSelection.vtxs)
        for v in self.vtxSelection.vtxs:
            print("#" * 20)
            pos = cmds.xform(v, q=True, ws=True, t=True)[:3]
            percent = self.zone.percentPointBetween(pos)
            print(percent, pos)
            percent = max(0, percent)
            percent = min(1, percent)
            w = [(self.jStart.longName, 1 - percent), (self.jEnd.longName, percent)]

            skCls = self.vtxSelection.getSkinCluster(v)
            print(skCls, v, w)
            cmds.skinPercent( skCls, v, transformValue=w)
            print(v, percent)

    def loadWin(self):
        '''Load the UI in a window
        '''

        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=300, retain=False, floating=True)
        self.layout = cmds.formLayout(p=self.win)

        self.jointStartInputLay = SmoothSkin.Line(self, self.layout, "joint start", "le joint d'ou ca commence")
        self.jointEndInputLay = SmoothSkin.Line(self, self.layout, "joint end", "le joint ou ca termine")
        self.goBtn = cmds.button(parent=self.layout, label="Go!", c=SmoothSkin.Callback(self.execute))

        af = []
        ac = []
        ap = []

        af.append((self.goBtn, "bottom", 3))
        af.append((self.goBtn, "left", 3))
        af.append((self.goBtn, "right", 3))

        af.append((self.jointStartInputLay.layout, "top", 3))
        af.append((self.jointStartInputLay.layout, "left", 3))
        af.append((self.jointStartInputLay.layout, "right", 3))

        ac.append((self.jointEndInputLay.layout, "top", 3, self.jointStartInputLay.layout))
        af.append((self.jointEndInputLay.layout, "left", 3))
        af.append((self.jointEndInputLay.layout, "right", 3))

        cmds.formLayout(self.layout, e=True, ac=ac, af=af, ap=ap)

def onMayaDroppedPythonFile(*args):
    '''Drag and drop function
    '''
    current_path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    sys.path.append(current_path)
    cmd = '''from ''' + __name__ + ''' import SmoothSkin;'''
    cmd += '''SmoothSkinWin = SmoothSkin();'''
    cmd += '''SmoothSkinWin.loadWin()'''
    mel.eval('''python("'''+ cmd + '''")''')
    # win = SmoothSkin()
    # win.start()

if __name__ == "__main__":
    win = SmoothSkin()
    win.loadWin()
