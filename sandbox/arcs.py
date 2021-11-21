# -- coding: utf-8 --

from maya import cmds
from math import *


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

def getVtxPos(shapeNode) :
 
	vtxWorldPosition = []
 
	vtxIndexList = cmds.getAttr( shapeNode+".vrts", multiIndices=True )
	for i in vtxIndexList :
		curPointPosition = cmds.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True ) 
		vtxWorldPosition.append(curPointPosition)
 
	return vtxWorldPosition

def getVertexZoneName(mesh, start, end, radius=1.2):
    A = cmds.xform(start,q=1,ws=1,rp=1)
    B = cmds.xform(end,q=1,ws=1,rp=1)

    zone = Vector(A, B)
    vtx = getVtxPos(mesh)
    selection = []
    for v, p in enumerate(vtx):
        if zone.isPointBetween(p):
            if zone.distPointToLine(p) < radius:
                selection.append("{}.vtx[{}]".format(mesh, v))
    return selection

def assignPercentWeigth(mesh, start, end, clst, radius=1.2):
    cmds.progressWindow(e=True, progress=(0), status="{} <~ {}".format(mesh, clst))
    A = cmds.xform(start,q=1,ws=1,rp=1)
    B = cmds.xform(end,q=1,ws=1,rp=1)

    zone = Vector(A, B)
    vtx = getVtxPos(mesh)
    selection = []
    
    totalVtx = len(vtx)
    for v, p in enumerate(vtx):
        if zone.isPointBetween(p):
            if zone.distPointToLine(p) < radius:
                r = zone.getRatio(p)
                h = (cos(r * 6.25) * -1) / 2 + 0.5
                mesh + ".vtx[" + str(v) + "]"
                cmds.percent(clst, "{}.vtx[{}]".format(mesh, v), v=h)
        cmds.progressWindow(e=True, progress=((float(v) / float(totalVtx)) * 100), status="{} <~ {} [{}/{}]".format(mesh, clst, v, totalVtx))

def CreateNurbSpine(name, side, skChain):
        
    nurb = "_".join(["nrb", name, side])

    n = cmds.nurbsPlane(p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=1, u=2, v=1, ch=1, n=nurb)[0]

    skTop = cmds.xform(skChain[0],q=1,ws=1,rp=1)
    skMid = cmds.xform(skChain[1],q=1,ws=1,rp=1)
    skLast = cmds.xform(skChain[2],q=1,ws=1,rp=1)

    cmds.move(-0.5, 0, 0, n + ".cv[2][0:1]",r=True, os=True, ws=True)
    cmds.move(0.5, 0, 0, n + ".cv[0][0:1]",r=True, os=True, ws=True)
    cmds.move(skTop[0], skTop[1], skTop[2], n + ".cv[0][0:1]",r=True, os=True, ws=True)
    cmds.move(skMid[0], skMid[1], skMid[2], n + ".cv[1][0:1]",r=True, os=True, ws=True)
    cmds.move(skLast[0], skLast[1], skLast[2], n + ".cv[2][0:1]",r=True, os=True, ws=True)

    cmds.rebuildSurface(n, sv=1, su=4, dv=1, du=1)

    return n

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
    print(nbShape)
    
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

def createCluster(meshs, nurb, skChain, name, side):
    clstPnt = [(skChain[0], skChain[1], "mid{}_{}".format(name.capitalize(), side)),
               (skChain[1], skChain[2], "fore{}_{}".format(name.capitalize(), side)),
               (skChain[0], skChain[2], "{}_{}".format(skChain[1].split("_")[1], side))]
    ctrlInf = []
    mesh = meshs.pop(0)
    for cp in clstPnt:
        s = getVertexZoneName(mesh, cp[0], cp[1])
        clstName, clstHandle = cmds.cluster(s, n="cluster" + cp[2][0].upper() + cp[2][1:])
        assignPercentWeigth(mesh, cp[0], cp[1], clstName)

        print(cp[2])
        root, inf, ctrl = createStarCtrl("arc_" + cp[2])
        ctrlInf.append(inf)
        toDelete = cmds.pointConstraint(cp[0], cp[1], root, mo=False)
        cmds.delete(toDelete)
        toDelete = cmds.orientConstraint(skChain[0], skChain[2], root, sk=["x", "y"], mo=False)
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
            s = getVertexZoneName(mesh, cp[0], cp[1])
            clstName = "cluster" + cp[2][0].upper() + cp[2][1:]
            cmds.sets(s, include ="{}Set".format(clstName))
            assignPercentWeigth(mesh, cp[0], cp[1], clstName)

    return ctrlInf

def grpCtrls(ctrl):
    cmds.setAttr(ctrl + ".overrideEnabled",1)
    cmds.setAttr(ctrl + ".overrideColor", 9)
    name = ctrl[2:]
    pose = cmds.group(ctrl, n="pose_" + name, a=True)
    inf = cmds.group(pose, n="inf_" + name, a=True)
    root = cmds.group(inf, n="root_" + name, a=True)
    return root, inf, ctrl

def createStarCtrl(name, pointed=8, strenght=0.09):
    nb = max(3,pointed) * 2
    
    ctrl = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=360, r=1, d=3, ut=0, tol=0.01, s=nb, ch=1, n="c_{}".format(name))[0]
    vtx = ["{}.cv[{}]".format(ctrl, x) for x in range(0, nb, 2)]
    cmds.scale(strenght, strenght, strenght, *vtx, r=True, ocp=True)
    cmds.delete(ctrl, constructionHistory = True)
    return grpCtrls(ctrl)

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
    print(skinBones + [nurb])
    skCls = cmds.skinCluster( skinBones + [nurb])[0]
    print(skCls)
    cmds.skinPercent( skCls, '{}.cv[0][0:1]'.format(nurb), transformValue=[(top, 1)])
    cmds.skinPercent( skCls, '{}.cv[1][0:1]'.format(nurb), transformValue=[(top, 0.5), (middleOri, 0.5)])
    cmds.skinPercent( skCls, '{}.cv[2][0:1]'.format(nurb), transformValue=[(middleZero, 1)])
    cmds.skinPercent( skCls, '{}.cv[3][0:1]'.format(nurb), transformValue=[(middle, 0.5), (endOri, 0.5)])
    cmds.skinPercent( skCls, '{}.cv[4][0:1]'.format(nurb), transformValue=[(endOri, 1)])

def createArc(meshs, memberName, side, skChain):
    if len(skChain) != 3:
        cmds.error("Please, select at least 3 consecutive bones")

    cmds.progressWindow(title="Arc Creation ", progress=0, status="Starting")
    try:
        nurb = CreateNurbSpine(memberName, side, skChain)
        infs = groupAimInfUp(memberName, side, nurb)
        ctrlInfs = createCluster(meshs, nurb, skChain, memberName, side)
        print(infs)
        print(ctrlInfs)
        for i, inf in enumerate(infs):
            print(inf, ctrlInfs[i])
            cmds.parentConstraint(inf, ctrlInfs[i], mo=True)
        middleJoints = cmds.listRelatives(skChain[0])
        zero = [x for x in middleJoints if "0_" in x]
        jointMiddle = zero[0] if len(zero) == 1 else skChain[1]
        cmds.parentConstraint(jointMiddle, ctrlInfs[2], mo=True)
        skinSkToNurb(nurb, skChain)
    finally:
        cmds.progressWindow(endProgress=True)

createArc(["msh_body", "msh_boot"], "leg", "L", cmds.ls(sl=True))

