from maya import cmds

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


def getSkinCluster(vtx):
    obj = vtx.split(".")[0]
    histList = cmds.listHistory(obj)
    if histList:
        for histItem in histList:
            if cmds.objectType(histItem) == "skinCluster":
                return histItem

def getInfluentJoints(vtx, skinCluster):
    weights = cmds.skinPercent( skinCluster, vtx, query=True, value=True)
    joints = cmds.skinCluster( skinCluster, q=True, inf=True)
    jointWeight = {}
    for j, w in zip(joints, weights):
        if w < 0.001:
            continue
        jointWeight[j] = [w]
    return jointWeight

def setInfluentJoints(skCls, vtx, joints):
    w = []
    for k, v in joints.items():
        w.append((str(k), v))
        cmds.setAttr(k + ".liw",  0)
    cmds.skinPercent( skCls, vtx, transformValue=w)

toVertex = lambda x: convertToList(cmds.polyListComponentConversion(x, tv=True))
toEdges = lambda x: convertToList(cmds.polyListComponentConversion(x, te=True, internal=True))
expandedSelVtx = lambda x: toVertex(cmds.polyListComponentConversion(x, te=True))

sel = cmds.ls(sl=True)

vertex = toVertex(sel)
vertex = convertToList(vertex)
for vtx in vertex:
    skCls = getSkinCluster(vtx)
    infs = getInfluentJoints(vtx, skCls)
    print(" -" * 15)
    print(infs)
    infsL = [{'name' : k, 'value': v[0]} for k, v in infs.items()]
    newlist = sorted(infsL, key=lambda d: d['value'], reverse=True)
    for i, e in enumerate(newlist):
        if e['value'] < 0.1:
            break
    print(i)
    i = min(i + 1, 5)
    tokeep = newlist[:i]
    smallValueSum = sum([x['value'] for x in newlist[i:]])
    tokeep[0]['value'] += smallValueSum
    newInfs = {x['name']: x['value'] for x in tokeep}
    print(newInfs)
    setInfluentJoints(skCls, vtx, newInfs)

    continue
    neigbor = expandedSelVtx(vtx)
    nbNeigh = len(neigbor)
    neigbor = [x for x in neigbor if x not in vertex]
    neigInf = {}
    if len(neigbor) == nbNeigh:
        continue
    for n in neigbor:
        for k in infs.keys():
            # print(k, infs[k])
            if k in neigInf.keys():
                neigInf[k] += infs[k]
            else:
                neigInf[k] = infs[k]
    for k, v in neigInf.items():
        neigInf[k] = sum(v) / len(neigbor)
    setInfluentJoints(skCls, vtx, neigInf)
    # print(neigInf)
    # print("voisin: ", neigbor)



# vertex = cmds.polyListComponentConversion(sel, tv=True, internal=True)
