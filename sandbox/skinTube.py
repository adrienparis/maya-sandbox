from math import *
from maya import cmds


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

def convertToList(sel):
    new = []
    for s in sel:
        num = s[s.find('[') + 1:s.find(']')]
        name = s.split('.')[0]
        t = s[s.find('.') + 1:s.find('[')]
        if ':' in num:
            start, end = num.split(':')
            start, end = int(start), int(end)
            for i in range(start, end + 1):
                new.append("{}.{}[{}]".format(name, t, i))
        else:
            new.append(s)
    return new

def createLocator(sel, name):
    bb = cmds.exactWorldBoundingBox(sel)
    gap =  [abs(bb[i + 3] - bb[i]) for i in range(len(bb) / 2)]
    center = [bb[i] + gap[i] / 2 for i in range(len(gap))]
    size = max(gap) / 2
    
    name = cmds.spaceLocator(r=True, p=[0,0,0], n=name)[0]
    cmds.move(center[0], center[1], center[2], name, a=True)
    size = float('%.3f'%(size * 1.1))
    size = max(0.1, size)
    cmds.setAttr(name + ".localScaleX", size)
    cmds.setAttr(name + ".localScaleY", size)
    cmds.setAttr(name + ".localScaleZ", size)
    cmds.setAttr(name + ".overrideEnabled",1)
    cmds.setAttr(name + ".overrideColor", 10)
    return name

def setJoint(obj):
    pos = cmds.xform(obj, q=True, t=True, ws=True)    
    rot = cmds.xform(obj, q=True, ro=True, ws=True)    
    cmds.select(clear=True)
    size = cmds.getAttr(obj + '.localScaleZ') * 1.2
    return cmds.joint(p=pos[0:3], orientation=rot[0:3], name=obj.replace("TMP_", "sk_").replace("pose_", "sk_"), radius=size)

toVertex = lambda x: convertToList(cmds.polyListComponentConversion(x, tv=True))
toEdges = lambda x: convertToList(cmds.polyListComponentConversion(x, te=True, internal=True))
expandedSelVtx = lambda x: toVertex(cmds.polyListComponentConversion(x, te=True))

def createJointsNskin(HAIR_NB, upEdges):

    sel = cmds.ls(sl=True)
    vertex = toVertex(sel)
    oldVertex = vertex
    i = 0
    gap = 2
    name = "webbing"
    tmps = []
    for x in range(0, 500):
        vertex = expandedSelVtx(vertex)
        vertex = [x for x in vertex if x not in oldVertex]
        oldVertex += vertex
        if vertex == []:
            print(vertex)
            break
        if i % gap == 0:
            upPosition = [v for v in vertex if v in upEdges]
            if len(upPosition) >= 1:
                t = createLocator(vertex, "TMP_{}{:02d}_{:02d}".format(name, HAIR_NB, i / gap + 1))
                u = createLocator(upPosition, "TMP_{}{:02d}_{:02d}Up".format(name, HAIR_NB, i / gap + 1))
                tmps.append((t,u))
        i += 1
    #	cmds.select(toEdges(vertex))
    print(tmps)
    grp = cmds.group(em=True, n="tmp_{}{:02d}".format(name, HAIR_NB))
    for t in tmps:
        cmds.parent(t[0], grp)
        cmds.parent(t[1], grp)
    joints = []
    prev = tmps.pop(0)
    for t in tmps:
        print(prev[0], t[0], prev[1])
        todelete = cmds.aimConstraint(prev[1], prev[0], aim=[1,0,0], u=[0,1,0], wut="object", wuo=t[0])
        cmds.delete(todelete)
        joints.append(setJoint(prev[0]))
        prev = t

    todelete = cmds.aimConstraint(prev[1], prev[0], aim=[1,0,0], u=[0,-1,0], wut="object", wuo=tmps[-2][0])
    cmds.delete(todelete)
    joints.append(setJoint(prev[0]))

    parjnt = joints[::-1]
    p = parjnt.pop(0)
    while parjnt:
        s = parjnt.pop(0)
        cmds.parent(p, s)
        p = s
    obj = sel[0].split(".")[0]

    zones = {}
    prev = joints[0]
    for j in joints[1:]:
        A = cmds.xform(prev,q=1,ws=1,rp=1)
        B = cmds.xform(j,q=1,ws=1,rp=1)
        zones[j] = Vector(A, B)
        prev = j



    skClst = cmds.skinCluster( joints + [obj])[0]
    for i in range(0, cmds.polyEvaluate(obj, v=True)):
        vtxName = "{}.pnts[{}]".format(obj, i)
        pos = cmds.xform(vtxName,q=1,ws=1,t=1)
        for k, z in zones.items():
            if z.isPointBetween(pos):
                continue
                print(vtxName, k, z.getRatio(pos), skClst)
                cmds.skinPercent( skClst, vtxName, transformValue=(k, z.getRatio(pos)))
upEdges = []

def buttonAddUpEdges(*_):
    global upEdges
    e = cmds.ls(sl=True)
    upEdges = toVertex(e)
    print(upEdges)

def buttonPressed(*_):
    numName = cmds.intField(IF_numName, q=True, v=True)
    cmds.intField(IF_numName, e=True, v=numName + 1)
    createJointsNskin(numName, upEdges)

name = "skin-Tube"
if cmds.workspaceControl(name, exists=1):
    cmds.deleteUI(name)
win = cmds.workspaceControl(name, ih=80, iw=250, retain=False, floating=True, h=80, w=250)

cmds.button(p=win, l="set Up edges", c=buttonAddUpEdges)
IF_numName = cmds.intField(p=win, v=1)
cmds.button(p=win, l="create", c=buttonPressed)


