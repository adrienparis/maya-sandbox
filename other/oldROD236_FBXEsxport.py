###################################################################
###################################################################
##               __          _______ _____                       ##
##               \ \        / /_   _|  __ \                      ##
##                \ \  /\  / /  | | | |__) |                     ##
##                 \ \/  \/ /   | | |  ___/                      ##
##                  \  /\  /   _| |_| |                          ##
##                   \/  \/   |_____|_|                          ##
##                                                               ##
###################################################################
###################################################################
print(elements_to_combine)

def getParent(node):
    p = cmds.listRelatives(node, p=True, type="joint")
    if not p:
        return node
    else:
        return getParent(p[0])

def getSkinCluster(node):
    hist = cmds.listHistory(node, lv=1)
    if hist:
        skinCl = cmds.ls(hist, type="skinCluster")
        if skinCl:
            return skinCl
    return None

def getAllRootedJoints():
    rootJoints = {}
    for sk in cmds.ls(type="joint"):
        rtJ = getParent(sk)
        if rtJ in rootJoints:
            rootJoints[rtJ] += 1
        else:
            rootJoints[rtJ] = 1
    return rootJoints

def progressBarUpdate(value, total):
    cmds.progressWindow(e=True, progress=(float(value) / total) * 100, status="{} / {}".format(value, total))


allJnts = cmds.ls(type="joint")
jnts = cmds.ls(sl=True)
jnts=["Root"]
jnts += cmds.listRelatives(jnts, allDescendents=True)
jnts = cmds.ls(jnts, type="joint")
badJnts = [x for x in allJnts if x not in jnts]


rootJoints = getAllRootedJoints()

commonJoint = max(rootJoints, key=rootJoints.get)
commonJoint = "Head_sk"
elemWithNoSkin = [x for x in elements_to_combine if getSkinCluster(x) is None]

print(elemWithNoSkin, commonJoint, rootJoints)

# for elem in elemWithNoSkin:

#     cmds.skinCluster(elem, commonJoint)


#Apply a skin if there is no skincluster on the mesh
for elem in elements_to_combine:
    skclst = getSkinCluster(elem)
    if skclst is None:
        print("new skincluster for {} with {}".format(elem, commonJoint))
        skclst = cmds.skinCluster(elem, commonJoint, tsb=True)
    else:
        weights = cmds.skinCluster(skclst, q=True, wi=True)
        rmJnts = [x for x in weights if x in badJnts]
        if len(rmJnts) == 0:
            print("keep {}'s skin".format(elem))
            continue
        if len(rmJnts) < len(weights):
            print("Removing {} useless weight for {} of {} joints :".format(len(rmJnts), elem, len(weights)))
            for rj in rmJnts:
                print("\t{}".format(rj))
            cmds.skinCluster(skclst, e=True, ri=rmJnts)
        else:
            print("unbinding {}".format(elem))
            cmds.skinCluster(skclst, e=True, ub=True)
            cmds.skinCluster(elem, commonJoint, tsb=True)

# cmds.select(elements_to_combine)

for x in elements_to_combine:
    print(x)

meshSkinCombinned = cmds.polyUniteSkinned(elements_to_combine, ch=1, mergeUVSets=1, centerPivot=False)
cmds.progressWindow(title="Transfert Skin", progress=0, status="Starting")
skin = yzWeightSave(meshSkinCombinned[0], progressFuncUpdate=progressBarUpdate)
ptcl = skin.storeToParticles()
skin = yzWeightSave(ptcl)
print(meshSkinCombinned[0])
print(skin)
neutralShapeName = neutralShape[0]._name
print(neutralShapeName)
# skin.storeToMesh(neutralShapeName)
cmds.progressWindow(endProgress=True)


# for elem in elemWithNoSkin:
#     skClst = getSkinCluster(elem)
#     cmds.skinCluster(elem, e=True, ub=True)