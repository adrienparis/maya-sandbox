
from math import *
from maya import cmds


def distance(A, B):
    return sqrt(pow(A[0]-B[0],2) + pow(A[1]-B[1],2) + pow(A[2]-B[2],2))

def distPointLine(A, B, p):
    # distance AB
    d = distance(A, B)
    # direction vecteur AB
    d = [(x - y) / d for x, y in zip(A, B)]

    # vecteur Ap
    v = [x - y for x, y in zip(p, A)]

    # produit scalaire v.d
    t = sum([x * y for x, y in zip(v, d)])

    projection = [x + t * y for x, y in zip(A, d)]
    print(projection)
    return distance(p, projection)




A = cmds.xform("locator2",q=1,ws=1,rp=1)
B = cmds.xform("locator3",q=1,ws=1,rp=1)
p1 = cmds.xform("locator1",q=1,ws=1,rp=1)
p2 = cmds.xform("locator4",q=1,ws=1,rp=1)

proj = cmds.xform("locator4",q=1,ws=1,rp=1)

print("="* 50)
print(distPointLine(A, B, p1))
print(distPointLine(A, B, p2))


print(distance(p1, proj))
