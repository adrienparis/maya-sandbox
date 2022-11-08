import random
from maya import cmds
from maya import mel


def getPointList(node):
    return cmds.ls(node + ".cp[*]", fl=True)

def getShape(mesh):
    shapes = cmds.listRelatives(mesh, pa=True, s=True)
    for shape in shapes:
        if cmds.getAttr(shape + ".intermediateObject") == 0:
            return shape
    return ""

def getSortIndex(list, max):
    # work list
    listTmp = list[:]

    # reverse sort
    listSortTmp = sorted(list)
    listSort = []
    for i in range(len(listSortTmp) - 1, -1, -1):
        listSort.append(listSortTmp[i])

    sort = [0 for _ in range(len(listSort))]
    for i in range(len(listSort)):
        for j in range(len(listTmp)):
            if listSort[i] == listTmp[j]:
                sort[i]=j
                listTmp[j]=-1
                break
        if len(sort) == max:
            break
    return sort

def sortFloat(list, sort):
    listNew = []
    for i in range(len(sort)):
        listNew.append(list[sort[i]])
    return listNew

def sortInt(list, sort):
    listNew = []
    for i in range(len(sort)):
        listNew.append(list[sort[i]])
    return listNew

def yzWeightStore(node):

    # got skin
    skin = cmds.listHistory(node)
    skin = cmds.ls( skin,et="skinCluster")

    if len(skin) < 1:
        cmds.error(node + " has no skin")


    # get infos
    pointList = getPointList(node)

    # skin infos
    infList = []
    maxInf = 0

    infList = cmds.skinCluster(q=True, inf=skin[0])
    maxInf = cmds.getAttr(skin[0] + ".mi")
    maxInf =  len(infList) - 1 if len(infList) - 1 <= maxInf else 5 if cmds.getAttr(skin[0] + ".mmi") == 0 else 0


    iSize = len(infList)
    cSize = len(pointList)

    # get membership lists
    tmpMatrix = cmds.createNode("transform", n="yzWeightStoreTmp")
    cmds.addAttr(ln="skin", at="long", m=True)

    # pcl node
    name = node.split("|")[0]
    pcl = cmds.particle(n=(name + "Weight#"))
    pcl += cmds.listRelatives( pcl[0], pa=True, s=True)
    pcl[1] = cmds.rename(pcl[1],pcl[0]+"Shape")


    # attributes
    cmds.addAttr(pcl[0], ln="skinGeometry", dt="string")
    cmds.setAttr(pcl[0]+".skinGeometry", node, type="string")

    cmds.addAttr(pcl[0], ln="skinWeightList", dt="string", m=True, im=0)
    for i in range(iSize):
        cmds.setAttr("{}.skinWeightList[{}]".format(pcl[0], i), infList[i], type="string")

    cmds.addAttr(pcl[0], ln="skinMaxInf", at="long", dv=maxInf)

    # attr tables
    for i in range(maxInf):
        cmds.addAttr(pcl[1], k=1, ln=("i" + str(i) + "W"), dt="doubleArray")
        cmds.addAttr(pcl[1], k=1, ln=("i" + str(i) + "W0"), dt="doubleArray")
        cmds.addAttr(pcl[1], k=1, ln=("w" + str(i) + "W"), dt="doubleArray")
        cmds.addAttr(pcl[1], k=1, ln=("w" + str(i) + "W0"), dt="doubleArray")

    # associate random colors to influences
    wColor = []
    colorSize = iSize

    for i in range(colorSize):
        wColor.append([random.random(),random.random(),random.random()])

    # display
    cmds.addAttr(pcl[1], ln="rgbPP", dt="vectorArray")
    cmds.addAttr(pcl[1], ln="rgbPP0", dt="vectorArray")
    cmds.addAttr(pcl[1], internalSet=True, ln="pointSize", at="long", min=1, max=60, dv=4)
    cmds.addAttr(pcl[1], internalSet=True, ln="pointSize0", at="long", min=1, max=60, dv=4)

    iList = range(iSize)


    # emit pcl from weights
    for c in range(cSize):
        amount = 0
        processing = 0
        cmds.progressWindow(title="exporting " + str(pcl[0]), progress=amount, status="cv: 1/" + str(cSize))

        # get weight location
        pos = cmds.xform(pointList[c], q=True, ws=True, t=True)
        color = [0,0,0]

        # emit cmd
        cmd = "emit -o {} -pos {} {} {} ".format(pcl[0], pos[0], pos[1], pos[2])

        # skin part
        # get weight
        wList = cmds.skinPercent(skin[0], pointList[c], q=True, v=True)
        iListTmp = iList

        if iSize > maxInf:
            sort = getSortIndex(wList, maxInf)
            wList = sortFloat(wList, sort)
            iListTmp = sortInt(iList, sort)
        print("-" * 50)

        newAttrs = []
        newValues = []
        for w, _ in enumerate(wList):
            # wList[w] = roundoff(wList[w], 4) # 4 decimals only, prune law
            newAttrs.append("i{}W".format(w))
            newAttrs.append("w{}W".format(w))
            newValues.append(iListTmp[w])
            newValues.append(wList[w])
            color += [x * wList[w] for x in wColor[iListTmp[w]]]



        cmd += ("-at rgbPP -vv {} {} {}".format(color[0], color[1], color[2]))
        print("↓" * 50)
        print(cmd)
        cmds.emit(o=pcl[0], pos=[pos[0], pos[1], pos[2]], at=newAttrs, fv=newValues)
        # mel.eval(cmd)
        print("↑" * 50)

        processing += float(c / cSize)*100
        amount = int(processing)
        cmds.progressWindow(e=True, progress=amount, status="cv: {}/{}".format(c + 1, cSize))

    cmds.delete(tmpMatrix)

    # cache
    cmds.particle(pcl[1], e=True, cache=0)
    cmds.saveInitialState(pcl[0])


    # exit
    cmds.progressWindow(endProgress=True)
    print(pcl)
    return pcl

def  yzwsStoreCB():
    sel = cmds.ls(sl=True, et="transform")
    weights = []

    # doStoreGeo = cmds.checkBox("yzwsStoreGeo", q=True, v=True)
    doStoreGeo = False

    for s0 in sel:
        #got milk
        history = cmds.listHistory(s0)
        skin = cmds.ls(history, et="skinCluster")

        if len(skin) < 1:
            continue

        pcl = yzWeightStore(s0, doStoreGeo)
        weights.append(pcl[0])
    cmds.select(weights)

yzwsStoreCB()