#!/usr/bin/env python
# -- coding: utf-8 --

"""yzWeightSaveModule.py: Python version of the yzWeightSaveUI.mel"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.0.1-RC"
__mayaversion__ = "Autodesk Maya 2017"

import random
import maya.OpenMaya as OpenMaya
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
from maya import cmds

class yzWeightSave():
    """Python vesion of the yzWeightSaveUI
    It store and restore the skin into a particle system or a mesh
    """

    def __init__(self, name=None, progressFuncUpdate=lambda x, y: None):
        self.mesh = None    # Maya transform node that contains shape
        self.shape = None   # Shape of the transform
        self.history = []   # history
        self.skin = None    # skin
        self.nbVtx = 0      # quantity of vertices in the shape
        self.vtxInf = []      # quantity of vertices in the shape
        self.vtxPos = []      # quantity of vertices in the shape
        self.infList = []   # list of joints that influence the mesh
        self.maxInf = 5     # Max influences that can skin a vtx at the same time
        self.particle = None
        self.prtclShape = None

        self.progressFuncUpdate = progressFuncUpdate

        self.initialized = False

        if name is None:
            return
        shape = cmds.listRelatives(name, children=True)[0] if cmds.objectType(name, isAType="transform") else name

        if cmds.objectType(shape, isAType="particle"):
            self.getFromParticle(name)
        if cmds.objectType(shape, isAType="mesh"):
            self.getFromSkin(name)

    def addProgressionEvent(self, func):
        self.progressFuncUpdate = func
        return self

    def _progrressionUpdateStatus(self, title, progression, status):
        cmds.progressWindow(title="Arc Creation ", progress=0, status="Starting")
        cmds.progressWindow(endProgress=True)



    @staticmethod
    def getVtxPos(mesh, update=lambda x, y: None):
        """mesh : str = name of the mesh (the transform, not the shape)
        return value : array of array (first array is for each vtx, second array is x y z coordinates)

        Get the coordinate of each vertex of a mesh

        author -> Dorian Fevrier
        """

        # get the active selection
        selection = OpenMaya.MSelectionList()
        selection.add(mesh)
        iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)

        # go througt selection
        while not iterSel.isDone():

            # get dagPath
            dagPath = OpenMaya.MDagPath()
            iterSel.getDagPath( dagPath )

            # create empty point array
            inMeshMPointArray = OpenMaya.MPointArray()

            # create function set and get points in world space
            currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
            currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kObject)

            # put each point to a list
            pointList = []
            size = inMeshMPointArray.length()
            for i in range( inMeshMPointArray.length() ) :
                update(i, size)
                pointList.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )

            return pointList

    def getVtxInf(self):
        """
        """
        selList = om2.MSelectionList()
        selList.add(self.shape)
        meshDagPath = selList.getDagPath(0)

        indices = range(self.nbVtx)
        singleIdComp = om2.MFnSingleIndexedComponent()
        vertexComp = singleIdComp.create(om2.MFn.kMeshVertComponent) # MObject
        singleIdComp.addElements(indices)

        mFnSkinCluster  = None
        mItDependencyGraph = om2.MItDependencyGraph(meshDagPath.node(),
                                                    om2.MItDependencyGraph.kDownstream,
                                                    om2.MItDependencyGraph.kPlugLevel)
        while not mItDependencyGraph.isDone():
            mObject = mItDependencyGraph.currentNode()
            if mObject.hasFn(om2.MFn.kSkinClusterFilter):
                mFnSkinCluster  = oma2.MFnSkinCluster(mObject)
                break
            mItDependencyGraph.next()

        weights, numInfs = mFnSkinCluster.getWeights(meshDagPath, vertexComp)
        return [list(weights[x:x+numInfs]) for x in range(0, len(weights), numInfs)]

    @staticmethod
    def getColorArray(size):
        """size : int = number of differents colors you need
        return value : list of list = first list for each influence, second list for RGB value

        creating a random color array of size
        """
        wColor = []
        for _ in range(size):
            wColor.append([random.random(),random.random(),random.random()])
        return wColor

    @staticmethod
    def normalizeSkinInf(infs):
        ratio = sum(infs)
        infs = [x / ratio for x in infs]
        return infs

    @staticmethod
    def normalizeSkinInfTuple(infs):
        ratio = sum([x[1] for x in infs])
        infs = [(x[0], x[1] / ratio) for x in infs]
        return infs

    def _checkInit(self):
        if not self.initialized:
            cmds.error("must load from mesh or particle system")

    # Getting the skin info from
    def getFromParticle(self, particle):
        """particle : str = name of the particle system
        get all the skin weight info from the particle system
        """
        self.particle = particle
        self.prtclShape = cmds.listRelatives(self.particle, shapes=True)[0]

        #store influences names from particle's systeme
        self.infList = []
        nbInfs = len(cmds.getAttr("{}.skinWeightList".format(self.particle), mi=True))
        for i in range(nbInfs):
            infName = cmds.getAttr("{}.skinWeightList[{}]".format(self.particle, i))
            if infName is None:
                continue
            self.infList.append(infName)

        #store basic information
        self.mesh = cmds.getAttr("{}.skinGeometry".format(self.particle))
        self.shape = cmds.listRelatives(self.mesh, shapes=True)[0] if cmds.objExists(self.mesh) else None
        self.maxInf = int(cmds.getAttr("{}.skinMaxInf".format(self.particle)))
        self.nbVtx = cmds.particle(self.prtclShape, q=True, count=True)

        # Store vertices positions and influences
        self.vtxInf = []
        self.vtxPos = []
        for vtxOrder in range(self.nbVtx):
            vtxWeight = [0.0] * len(self.infList)
            self.progressFuncUpdate(vtxOrder, self.nbVtx)
            for j in range(self.maxInf):
                weightValue = cmds.particle(self.prtclShape, q=True, order=vtxOrder, at="w{}W".format(j))[0]
                weightIndex = int(cmds.particle(self.prtclShape, q=True, order=vtxOrder, at="i{}W".format(j))[0])
                vtxWeight[weightIndex] = weightValue
            vtxWeight = self.normalizeSkinInf(vtxWeight)
            self.vtxInf.append(vtxWeight)
            self.vtxPos.append(cmds.particle(self.prtclShape, q=True, order=vtxOrder, at="position"))

        self.initialized = True

    def getFromSkin(self, mesh):
        """mesh : str = name of the mesh that has a skin

        get all the skin weight info from the skinCluster of the mesh
        """
        self.mesh = mesh
        self.shape = cmds.listRelatives(self.mesh, shapes=True)[0]
        self.history = cmds.listHistory(mesh)
        self.skin = cmds.ls(self.history, et="skinCluster")
        if len(self.skin) < 1:
            return
        self.skin = self.skin[0]
        self.nbVtx = cmds.polyEvaluate(self.mesh, v=True )
        self.infList = cmds.skinCluster(self.skin, q=True, inf=True)
        self.maxInf = int(cmds.getAttr(self.skin + ".mi"))
        self.vtxPos = self.getVtxPos(self.mesh, self.progressFuncUpdate)
        self.vtxInf = self.getVtxInf()

        self.initialized = True

    # Storing the saved skin into
    def storeToMesh(self, mesh=None):
        """ name : str = name of mesh that will receive the skin

        Create a skinCluster to the mesh
        must be initialized with a getFromParticle() or getFromSkin() method
        The mesh should not have any skinCluster on it
        """
        self._checkInit()
        if mesh is None:
            mesh = self.mesh
        skin = cmds.skinCluster(mesh, self.infList, mi=5)[0]
        order = cmds.skinCluster(skin, q=True, inf=True)
        orderInfs = [order.index(inf) for inf in self.infList]
        for vtxIndex in range(self.nbVtx):
            self.progressFuncUpdate(vtxIndex, self.nbVtx)
            for vtxInfIndex, infIndex in enumerate(orderInfs):
                cmds.setAttr("{}.weightList[{}].weights[{}]".format(skin, vtxIndex, infIndex), self.vtxInf[vtxIndex][vtxInfIndex])
        return skin

    def storeToParticles(self, name=None):
        """ name : str = name of the particle system
        return value : str = new name of the particle system

        Create a particle system that has all the skin weight
        must be initialized with a getFromParticle() or getFromSkin() method
        """
        self._checkInit()
        name = self.mesh.split("|")[0] + "Weight#" if name is None else name

        # Create particle's syteme
        self.particle, self.prtclShape = cmds.particle(n=name)
        self.prtclShape = cmds.rename(self.prtclShape, self.particle + "Shape")

        # store influences names in particle's systeme
        cmds.addAttr(self.particle, ln="skinWeightList", dt="string", m=True, im=0)
        for i, inf in enumerate(self.infList):
            cmds.setAttr("{}.skinWeightList[{}]".format(self.particle, i), inf, type="string")    # attr tables

        cmds.addAttr(self.prtclShape, internalSet=True, ln="pointSize", at="long", min=1, max=60, dv=4)
        cmds.addAttr(self.prtclShape, internalSet=True, ln="pointSize0", at="long", min=1, max=60, dv=4) # have to double the argument so they can be saved in the cache when exporting selection
        # Add color attribut
        cmds.addAttr(self.prtclShape, k=1, ln="rgbPP", dt="vectorArray")
        cmds.addAttr(self.prtclShape, k=1, ln="rgbPP0", dt="vectorArray") # have to double the argument so they can be saved in the cache when exporting selection
        # Add weight attributes
        for i in range(self.maxInf):
            cmds.addAttr(self.prtclShape, k=1, ln="i" + str(i) + "W", dt="doubleArray")
            cmds.addAttr(self.prtclShape, k=1, ln="w" + str(i) + "W", dt="doubleArray")
            # have to double the arguments so they can be saved in the cache when exporting selection
            cmds.addAttr(self.prtclShape, k=1, ln="i" + str(i) + "W0", dt="doubleArray")
            cmds.addAttr(self.prtclShape, k=1, ln="w" + str(i) + "W0", dt="doubleArray")

        wColor = self.getColorArray(len(self.infList))

        # Store basic information
        cmds.addAttr(self.particle, ln="skinGeometry", dt="string")
        cmds.addAttr(self.particle, ln="skinMaxInf")
        cmds.setAttr("{}.skinGeometry".format(self.particle), self.mesh, type="string")
        cmds.setAttr("{}.skinMaxInf".format(self.particle), self.maxInf)

        for vtx, pos in enumerate(self.vtxPos):
            cmds.emit(o=self.particle, pos=pos)
            color = [0,0,0]
            infs = [inf for inf in list(enumerate(self.vtxInf[vtx])) if inf[1] >= 0.0001]
            if len(infs) < self.maxInf:
                # Add empty influence
                infIndex = [idx[0] for idx in infs]
                infs += [(i, 0.0) for i in range(len(self.infList)) if i not in infIndex][:self.maxInf - len(infs)]
            if len(infs) > self.maxInf:
                # Trunc influence
                infs = sorted(infs, key=lambda x : x[1], reverse=True)
                infs = infs[:self.maxInf]
                infs = self.normalizeSkinInfTuple(infs)
            self.progressFuncUpdate(vtx, self.nbVtx)

            for i, inf in enumerate(infs):
                cmds.particle(self.prtclShape, e=True, order=vtx, at="w{}W".format(i), fv=inf[1])
                cmds.particle(self.prtclShape, e=True, order=vtx, at="i{}W".format(i), fv=inf[0])
                # color += [x * inf for x in wColor[iListTmp[w]]]
                color = [x + c * inf[1] for x, c in zip(color, wColor[inf[0]])]

            cmds.particle(self.prtclShape, e=True, order=vtx, at="rgbPP", vv=color)

            cmds.particle(self.prtclShape, e=True, cache=0)
            cmds.saveInitialState(self.particle)
            # cmds.setAttr(self.prtclShape + ".usc", True)
            # cmds.setAttr(self.prtclShape + ".scp", "20221005_Elly_Head_Skin001_RigPro_etape_01_MDT_init_tmp1_startup", type=True)

        return self.particle

if __name__ == "__main__":
    # Example:
    import time

    print("testing yzWeightSaveModule")
    meshsSelected = cmds.ls(sl=True)
    duplicatesMeshs = [cmds.duplicate(s) for s in meshsSelected]
    particles = []

    for s in meshsSelected:
        # Storing skin from the selected mesh to a particle system
        start = time.time()

        # Creating an instance of skinWeight
        plop = yzWeightSave(s)
        # or
            # plop = skinWeight()
            # plop.getFromSkin(s)
        particleName = plop.storeToParticles()

        end = time.time()
        print("Storing to particle [{}]: {}".format(particleName, end - start))
        particles.append(particleName)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    for dupMesh, particle in zip(duplicatesMeshs, particles):
        # Storing skin from the particle system to the duplicated mesh
        start = time.time()

        plop = yzWeightSave(particle)
        # or
            # plop = skinWeight()
            # plop.getFromParticle(particleName)
        plop.storeToMesh(dupMesh)

        end = time.time()
        print("Storing to mesh [{}]: {}".format(dupMesh, end - start))
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #