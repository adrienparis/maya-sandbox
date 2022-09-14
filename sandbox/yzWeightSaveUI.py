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

def yzWeightStore(node, doStoreGeo):

    # got skin
    skin = cmds.listHistory(node)
    skin = cmds.ls( skin,et="skinCluster")

    # got clusters
    clusters = cmds.listHistory(node)
    clusters = cmds.ls(clusters, et="cluster")

    if len(skin) < 1 and len(clusters) < 1:
        cmds.error(node + " has no skin/clusters..")
    # doSkin doClusters
    doSkin = bool(len(skin))
    doClusters = bool(len(clusters))


    # get infos
    pointList = getPointList(node)

    # skin infos
    infList = []
    maxInf = 0
    if doSkin:
        infList = cmds.skinCluster(q=True, inf=skin[0])
        maxInf = cmds.getAttr(skin[0] + ".mi")
        maxInf = len(infList) if len(infList) < maxInf else 5 if cmds.getAttr(skin[0] + ".mmi") == 0 else 0


    iSize = len(infList)
    cSize = len(pointList)

    # clusters infos
    infListCluster = []
    clusterSet = []
    for clst in clusters:
        handle = cmds.listConnections(clst + ".matrix")
        infListCluster.append(handle[0])

        deformSet = cmds.listConnections(clst + ".msg")
        clusterSet.append(deformSet[0])

    # get membership lists
    tmpMatrix = cmds.createNode("transform", n="yzWeightStoreTmp")
    cmds.addAttr(ln="skin", at="long", m=True)
    for cl, _ in enumerate(clusters):
        cmds.addAttr(ln=("cluster" + cl), at="long", m=True)
    cmds.addAttr(ln="clusterInf", at="long", m=True)

    # skinSet = listConnections (skin[0]+".msg")
    for cl, _ in enumerate(clusters):
        clusterPoints = cmds.sets(clusterSet[cl], q=True)
        clusterPoints = cmds.filterExpand(clusterPoints, sm=[31, 28, 36, 47, 46])

        for c in range(cSize):
            cmds.setAttr (tmpMatrix+".cluster"+cl+"["+c+"]", 0)
            if pointList[c] in clusterPoints:
                cmds.setAttr(tmpMatrix + ".cluster" + cl + "[" + c + "]", 1)

    # pcl node
    name = node.split("|")[0]
    pcl = cmds.particle(n=(name + "Weight#"))
    pcl += cmds.listRelatives( pcl[0], pa=True, s=True)
    pcl[1] = cmds.rename(pcl[1],pcl[0]+"Shape")

    # copy mesh
    copy = 0
    doDye = 0

    if doStoreGeo:
        dupe = cmds.duplicate(node)
        shape = getShape(dupe[0])
        doDye = 1 if cmds.nodeType(shape)=="mesh" else 0

        if not cmds.pluginInfo("decomposeMatrix", q=True, l=True):
            cmds.loadPlugin("decomposeMatrix")
        dmx = cmds.createNode("decomposeMatrix")
        copy = cmds.createNode("transform", p=pcl[0], n=name+"Copy#")

        cmds.connectAttr(node + ".wm", dmx + ".imat")
        cmds.connectAttr(dmx + ".ot", copy + ".t")
        cmds.connectAttr(dmx + ".or", copy + ".r")
        cmds.connectAttr(dmx + ".os", copy + ".s")
        cmds.connectAttr(dmx + ".osh", copy + ".sh")
        cmds.refresh()
        cmds.delete(dmx)

        cmds.parent(shape, copy, r=True, s=True)
        cmds.delete(dupe)

        cmds.setAttr(copy + ".overrideEnabled", 1)
        cmds.setAttr(copy + ".overrideDisplayType", 2)
        cmds.setAttr(copy + ".displayColors", 1)
        cmds.polyOptions("colorMaterialChannel", "ambient+diffuse", copy)
        cmds.setAttr(copy+".materialBlend", 0)

        mel.eval('source "assignSG";')
        mel.eval('assignSG("lambert1", )'.format(copy))

    # attributes
    cmds.addAttr(pcl[0], ln="skinGeometry", dt="string")
    cmds.setAttr(pcl[0]+".skinGeometry", node, type="string")

    if doSkin:
        cmds.addAttr(pcl[0], ln="skinWeightList", dt="string", m=True, im=0)
        for i in range(iSize):
            cmds.setAttr("{}.skinWeightList[{}]".format(pcl[0], i), infList[i], type="string")

        cmds.addAttr(pcl[0], ln="skinMaxInf", at="long", dv=maxInf)

    if doClusters:
        cmds.addAttr(pcl[0], ln="clusterList", dt="string", m=True, im=0)
        for i, _ in enumerate(clusters):
            cmds.setAttr("{}.skinWeightList[{}]".format(pcl[0], i), infListCluster[i], type="string")
        cmds.addAttr(pcl[0], ln="clusterMaxInf", at="long")
        cmds.setAttr(pcl[0] + ".clusterMaxInf", len(clusters))
        cmds.addAttr(pcl[0], ln="clusterSkinMaxInf", at="long")

    # attr tables
    if doSkin:
        for i in range(maxInf):
            cmds.addAttr(pcl[1], k=1, ln=("i" + str(i) + "W"), dt="doubleArray")
            cmds.addAttr(pcl[1], k=1, ln=("i" + str(i) + "W0"), dt="doubleArray")
            cmds.addAttr(pcl[1], k=1, ln=("w" + str(i) + "W"), dt="doubleArray")
            cmds.addAttr(pcl[1], k=1, ln=("w" + str(i) + "W0"), dt="doubleArray")

    if doClusters:
        for i, _ in enumerate(clusters):
            cmds.addAttr(pcl[1], k=1, ln="c" + str(i) + "W", dt="doubleArray")
            cmds.addAttr(pcl[1], k=1, ln="c" + str(i) + "W0", dt="doubleArray")

    # associate random colors to influences
    wColor = []
    colorSize = len(clusters) if(not doSkin) else iSize

    for i in range(colorSize):
        wColor.append([random.random(),random.random(),random.random()])

    # display
    cmds.addAttr(pcl[1], ln="rgbPP", dt="vectorArray")
    cmds.addAttr(pcl[1], ln="rgbPP0", dt="vectorArray")
    cmds.addAttr(pcl[1], internalSet=True, ln="pointSize", at="long", min=1, max=60, dv=4)
    cmds.addAttr(pcl[1], internalSet=True, ln="pointSize0", at="long", min=1, max=60, dv=4)

    cmdColor = ("setAttr {}.vclr[0:{}].vrgb ".format(copy, len(pointList)-1))
    cmdAlpha = ("setAttr {}.vclr[0:{}].vxal ".format(copy, len(pointList)-1))

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
        cmd = ("emit -o {} -pos {} {} {} ".format(pcl[0], pos[0], pos[1], pos[2]))


        # skin part
        if doSkin:
            # get weight
            wList = cmds.skinPercent(skin[0], pointList[c], q=True, v=True)
            iListTmp = iList

            if iSize > maxInf:
                sort = getSortIndex(wList, maxInf)
                wList = sortFloat(wList, sort)
                iListTmp = sortInt(iList, sort)


            for w, _ in enumerate(wList):
                # wList[w] = roundoff(wList[w], 4) # 4 decimals only, prune law
                cmd += ("-at i{}W -fv {} ".format(w, iListTmp[w]))
                cmd += ("-at w{}W -fv {} ".format(w, wList[w]))
                color += [x * wList[w] for x in wColor[iListTmp[w]]]



        # clusters part
        if doClusters:
            for cl, _ in enumerate(clusters):
                wList = cmds.percent(clusters[cl], pointList[c], q=True, v=True)
                if not cmds.getAttr(tmpMatrix + ".cluster" + cl + "[" + c + "]"):
                    wList = 0

                cmd += ("-at c" + cl + "W -fv " + wList[0] + " ")

                if wList[0] > 0:
                    cmds.setAttr("{}.clusterInf[{}]".format(tmpMatrix, c), cmds.getAttr("{}.clusterInf[{}]".format(tmpMatrix, c)) + 1)

                if not doSkin:
                    color += wColor[cl] * wList[0]



        # mesh color
        if doDye:
            cmdColor += ("".format(color[0], color[1], color[2]))
            cmdAlpha += "1 "


        cmd += ("-at rgbPP -vv {} {} {}".format(color[0], color[1], color[2]))
        mel.eval(cmd)

        processing += float(c / cSize)*100
        amount = int(processing)
        cmds.progressWindow(e=True, progress=amount, status="cv: {}/{}".format(c + 1, cSize))


    # color mesh
    if doDye:
        mel.eval(cmdColor)
        mel.eval(cmdAlpha)
        cmds.setAttr("{}.displayImmediate".format(copy), 1)
        cmds.setAttr("{}.displayImmediate".format(copy), 0)


    # cluster maxInf lookup
    if doClusters:
        maxInf = 0
        for c in range(cSize):
            clusterInf = cmds.getAttr("{}.clusterInf[{}]".format(tmpMatrix, c))
            if clusterInf > maxInf:
                maxInf = clusterInf

        cmds.setAttr(pcl[0] + ".clusterSkinMaxInf", maxInf)

    cmds.delete(tmpMatrix)

    # cache
    cmds.particle(pcl[1], e=True, cache=0)
    cmds.saveInitialState(pcl[0])


    # exit
    cmds.progressWindow(endProgress=True)
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
        clusters = cmds.ls(history, et="cluster")

        if len(skin) < 1 and len(clusters) < 1:
            continue

        pcl = yzWeightStore(s0, doStoreGeo)
        weights.append(pcl[0])
    cmds.select(weights)

yzwsStoreCB()