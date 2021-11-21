import math
import maya.cmds as cmds

class vtx:
    def __init__(self, name):
        self.nb = name[name.find("[")+1:name.find("]")]
        self.msh = name[:name.find(".")]
        self.neighbor = []

class bone:
    def __init__(self, name):
        self.name
        self.coord = cmds.objectCenter(self.name, gl=True)
        self.x = self.coord[0]
        self.y = self.coord[1]
        self.z = self.coord[2]
    def __str__(self):
        return self.name + str(self.coord)

class pointInZone:
    def __init__(self, A, B):
        self.A = A[:]
        self.B = B[:]
        #vecteur AB
        self.AB = [self.B[i] - self.A[i] for i in range(len(self.A))]
        #norme du vecteur AB
        self.normeAB =  math.sqrt((self.AB[0]*self.AB[0]) + (self.AB[1]*self.AB[1]) + (self.AB[2]*self.AB[2]))
        #vecteur AB normalisé
        self.u = [self.AB[i] / self.normeAB for i in range(len(self.AB))]
    def isPointBetween(self, M):
        #vecteur AM
        AM = [M[i] - self.A[i] for i in range(len(self.A))]
        #produit scalaire p=u.AM
        p = self.u[0] * AM[0] + self.u[1] * AM[1] + self.u[2] * AM[2]
        return 0<=p and p<=self.normeAB


def getConnectedVtx(obj, vtx):
    print(cmds.polyInfo(obj + vtx, ve=True))

def getClosestPoint():




# v = pointInZone([-2.5,5,-1.5],[3,7.5,-7.5])
# print(v.isPointBetween([2,0,-5]))
# print(v.isPointBetween([-1,1.5,4]))


def start():
    lJoint = []
    lMesh = []

    sel = cmds.ls(sl=True, st=True)

    for i in range(0, len(sel), 2):
        print(sel[i])
        
        if sel[i + 1] == u'joint':
            lJoint.append(sel[i])
        else:
            lMesh.append(sel[i])
    print(lJoint)
    print(lMesh)




# def f(xp, yp, zp):
#     a = 1
#     b = 1
#     c = 1
#     d = 3
#     print(a*xp + b * yp + c * zp + d)
    
# #    d = (x2 - x1) * (yp - y1) - (xp - x1) * (y2 - y1)
#     print(d)

# #f(4,-5,-6)


# sel = cmds.ls(sl=True, o=True)[0]
# print(sel)

# sel_vtx = cmds.ls('{}.vtx[:]'.format(sel), fl=True, sl=False)
# print(sel_vtx)


# pos = (cmds.xform(sel, q=True, t=True, ws=True)[:3]).copy()


# print(sel)
# print(pos)
# child = cmds.listRelatives(sel)
# childPos = cmds.xform(child, q=True, t=True, ws=True)[:3]
# print(child, childPos)
# print(childPos - pos)





# class bone:
#     def __init__(self, name):
#         self.name = name
#         self.coord = cmds.objectCenter(self.name, gl=True)
#         self.x = self.coord[0]
#         self.y = self.coord[1]
#         self.z = self.coord[2]
#     def __str__(self):
#         return self.name + str(self.coord)
#     def __repr__(self):
#         return self.name + str(self.coord)

# def getAllBones(name):
#     list = [name]
#     childrens = cmds.listRelatives(name, c=True)
#     if childrens is None:
#         return list
#     for c in childrens:
#         if c.startswith("sk_"):
#             b = getAllBones(c)
#             list += b
#     return list

# def getVtxPos( shapeNode ) :
 
# 	vtxWorldPosition = []    # will contain positions un space of all object vertex
 
# 	vtxIndexList = cmds.getAttr( shapeNode+".vrts", multiIndices=True )
 
# 	for i in vtxIndexList :
# 		curPointPosition = cmds.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True )    # [1.1269192869360154, 4.5408735275268555, 1.3387055339628269]
# 		vtxWorldPosition.append( curPointPosition )
 
# 	return vtxWorldPosition

# def listVertices(meshs):
#     for m in meshs:
#         lVertices = []

# def start():
#     lJoint = []
#     lMesh = []

#     sel = cmds.ls(sl=True, st=True)

#     for i in range(0, len(sel), 2):
#         print(sel[i])
        
#         if sel[i + 1] == u'joint':
#             lJoint += getAllBones(sel[i])
#         else:
#             lMesh.append(sel[i])
# #TODO remove duplicate            
# #    lJoint = list(dict.fromkeys(lJoint))
#     joints = []
#     for j in lJoint:
#         joints.append(bone(j))

#     print(lJoint)
#     print(str(joints))
#     print(lMesh)
#     print(getVtxPos(lMesh[0]))

# start()