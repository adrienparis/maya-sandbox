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

isObjectVisible = lambda obj : False if 0 in [cmds.getAttr(p + ".visibility") for p in (cmds.listRelatives(obj, ap=True) if cmds.listRelatives(obj, ap=True) is not None else [])] + [cmds.getAttr(obj + ".visibility")] else True

distanceBetween = lambda x, y: math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2 + (x[2] - y[2])**2)

class Vector:
    @staticmethod
    def distance(A, B):
        return math.sqrt(pow(A[0]-B[0],2) + pow(A[1]-B[1],2) + pow(A[2]-B[2],2))

    def __init__(self, A, B):
        self.A = A[:]
        self.B = B[:]
        #vecteur AB
        self.AB = [self.B[i] - self.A[i] for i in range(len(self.A))]
        #norme du vecteur AB
        self.normeAB = math.sqrt((self.AB[0]*self.AB[0]) + (self.AB[1]*self.AB[1]) + (self.AB[2]*self.AB[2]))
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

class SmoothSkin(object):
    
    # Name of the application
    name = u"Skin Smoother"
    draggerContextName = "AP_SmoothSkin"

    def __init__(self):
        self.win = None
        self.vtxSelection = SmoothSkin.GrpVTX()
        self.anchor = [0.0, 0.0, 0.0]
        self.jnts = []
        
        if (cmds.contextInfo(self.draggerContextName, exists = True)):
            cmds.deleteUI(self.draggerContextName, toolContext = True )
        cmds.draggerContext(self.draggerContextName, pressCommand=self.dragger_onPress, releaseCommand=self.dragger_onRelease, dragCommand=self.dragger_onDrag,
                            cursor = "crossHair", space="world", i1="skin.png", undoMode="step", snp=True, projection="objectPlane")

    class GrpVTX(object):
        def __init__(self):
            self.vtxs = []
            self.autoSelect = False
            self._events = {}

        @staticmethod
        def getSkinCluster(vtx):
            obj = vtx.split(".")[0]
            shp = obj.split("|")[-1]+ "Shape"
            shapeNode = obj + "|" + shp
            histList = cmds.listHistory(obj)
            if histList:
                for histItem in histList:
                    if cmds.objectType(histItem) == "skinCluster":
                        return histItem

        def updateSelection(self):
            sel = cmds.ls(sl=True, o=True, type="mesh")
            self.vtxs = []
            for s in sel:
                self.vtxs += SmoothSkin.GrpVTX.selectVertices(s)

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

    @staticmethod
    def getClosestJointFromPos(pos):
        print(cmds.ls(type="joint"))
        jnts = jnts = [(x, cmds.xform(x, q=True, t=True, ws=True)) for x in cmds.ls(type="joint") if isObjectVisible(x)]
        jnts = sorted(jnts, key=lambda j: distanceBetween(j[1], pos))
        return jnts[0]

    @staticmethod
    def getClosestJointFromLinePos(pos):
        jnts = jnts = [(x, cmds.xform(x, q=True, t=True, ws=True)) for x in cmds.ls(type="joint") if isObjectVisible(x)]
        curCamera = 'persp'
        vp = cmds.getPanel(withFocus=True)
        if "modelPanel4" in vp:
            curCamera=cmds.modelEditor(vp,q=1,av=1,cam=1)
        A = pos
        B = cmds.xform(curCamera,q=1,ws=1,rp=1)
        line = Vector(A, B)

        for j in jnts:
            print(line.distPointToLine(j[1]))
        jnts = sorted(jnts, key=lambda j: line.distPointToLine(j[1]))
        jnts = filter(lambda j: line.distPointToLine(j[1]) <= 1, jnts)
        print(jnts)
        if jnts:
            return jnts[0]
        return (None, [0.0, 0.0, 0.0])



    @staticmethod
    def moveLoc(name, pos):
        if cmds.objExists(name):
            cmds.setAttr("{}.tx".format(name), pos[0])
            cmds.setAttr("{}.ty".format(name), pos[1])
            cmds.setAttr("{}.tz".format(name), pos[2])
            # cmds.setAttr("{}.tz".format(name), pos[2])
        else:
            cmds.spaceLocator(n=name, p=pos)

    def dragger_onPress(self):
        print(u"#"*10)
        print(cmds.ls(sl=True))
        pos = cmds.draggerContext(SmoothSkin.draggerContextName, query = True, anchorPoint = True)
        print(pos)
        SmoothSkin.moveLoc("Start", pos)
        if cmds.draggerContext(SmoothSkin.draggerContextName, query = True, button=True) != 1:
            return
        mdf = cmds.draggerContext(SmoothSkin.draggerContextName, query = True, modifier=True)
        if mdf == "ctrl":
            jnt, _ = SmoothSkin.getClosestJointFromPos(pos)
            if jnt in self.jnts:
                self.jnts.pop(self.jnts.index(jnt))
            if len(self.jnts) >= 2:
                rem = self.jnts.pop(0)
                cmds.select(rem, d=True)
            self.jnts.append(jnt)
            print(self.jnts)
            cmds.select(jnt, add=True)
        elif mdf == "none":
            self.anchor = pos
        elif mdf == "shift":
            _, coord = SmoothSkin.getClosestJointFromPos(pos)
            self.anchor = coord
    
    @staticmethod
    def skinLinear(jStart, jEnd, locStart, locEnd, vertices):
        zone = Vector(locStart, locEnd)
        for v in vertices:
            pos = cmds.xform(v, q=True, ws=True, t=True)[:3]
            percent = zone.getRatio(pos)
            percent = max(0, percent)
            percent = min(1, percent)
            w = [(jStart, 1 - percent), (jEnd, percent)]

            skCls = SmoothSkin.GrpVTX.getSkinCluster(v)
            cmds.skinPercent( skCls, v, transformValue=w)
        
    def dragger_onDrag(self):
        pass

    def dragger_onRelease(self):
        mdf = cmds.draggerContext(SmoothSkin.draggerContextName, query = True, modifier=True)
        print(mdf)
        btnMouse = cmds.draggerContext(SmoothSkin.draggerContextName, query = True, button=True)
        if btnMouse != 1:
            return
        pos = cmds.draggerContext(SmoothSkin.draggerContextName, query = True, dragPoint = True)
        SmoothSkin.moveLoc("End", pos)
    
        if mdf == "none":
            pass
        elif mdf == "shift":
            # _, pos = SmoothSkin.getClosestJointFromPos(pos)
            jnt, pos = SmoothSkin.getClosestJointFromLinePos(pos)
            print(jnt, pos)
            if jnt is not None:
                cmds.select(jnt)
        else:
            return
        
        if self.anchor == pos:
            print("same place")
            return
        self.zone = Vector(self.anchor, pos)
        print(len(self.jnts), self.jnts)
        if len(self.jnts) != 2:
            return
        print("Starting")
        jStart = self.jnts[0]
        jEnd = self.jnts[1]
        self.vtxSelection.updateSelection()
        print(self.vtxSelection.vtxs)
        for v in self.vtxSelection.vtxs:
            print("#" * 20)
            pos = cmds.xform(v, q=True, ws=True, t=True)[:3]
            percent = self.zone.getRatio(pos)
            print(percent, pos)
            percent = max(0, percent)
            percent = min(1, percent)
            w = [(jStart, 1 - percent), (jEnd, percent)]

            skCls = SmoothSkin.GrpVTX.getSkinCluster(v)
            print(skCls, v, w)
            cmds.skinPercent( skCls, v, transformValue=w)
            print(v, percent)

    def execute(self):        
        cmds.setToolTo(SmoothSkin.draggerContextName)

def onMayaDroppedPythonFile(*args):
    '''Drag and drop function
    '''
    SmoothSkin().execute()

if __name__ == "__main__":
    SmoothSkin().execute()

