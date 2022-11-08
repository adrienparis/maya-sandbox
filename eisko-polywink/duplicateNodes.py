from maya import cmds

def listPackConnection(node):
    lst = cmds.listConnections(node, s=True, d=False, c=True, p=True, scn=True)
    if not lst:
        return []
    lstCnt = [(lst[i], lst[i+1]) for i in range(0, len(lst)-1,2)]
    return lstCnt

def connectLike(dupParent, dupChild, parentCnt, childCnt):
    dupChildCnt = dupChild + '.' + '.'.join(childCnt.split('.')[1:])
    dupParentCnt = dupParent + '.' + '.'.join(parentCnt.split('.')[1:])
    if cmds.isConnected(dupParentCnt, dupChildCnt):
        return
    cmds.connectAttr(dupParentCnt, dupChildCnt)

def connectLikeSwitchMaster(dupParent, dupChild, parentCnt, childCnt, switchAttrs):
    dupChildCnt = dupChild + '.' + '.'.join(childCnt.split('.')[1:])
    for oldAttr, newAttr in switchAttrs:
        currentAttr = '.'.join(parentCnt.split('.')[1:])
        if currentAttr == oldAttr:
            dupParentCnt = dupParent + '.' + newAttr
            break
    else:
        dupParentCnt = dupParent + '.' + '.'.join(parentCnt.split('.')[1:])
    if cmds.isConnected(dupParentCnt, dupChildCnt):
        return
    print(dupParentCnt, dupChildCnt)
    cmds.connectAttr(dupParentCnt, dupChildCnt)


def duplicateNodeTo(source, stopNode, target=None, switchAttrs=[], depth=0, limit=10):
    if depth >= limit:
        return None

    sourceName, sourceAttr = source.split('.') if '.' in source else (source, None)

    if sourceName == stopNode:
        return stopNode

    duplicate = None

    lstCnt = listPackConnection(sourceName)

    for current, parent in lstCnt:
        parentDuplicate = duplicateNodeTo(parent, stopNode, switchAttrs=switchAttrs, depth=depth + 1, limit=limit)
        if parentDuplicate is not None:
            duplicate = sourceName + "_lol"
            if not cmds.objExists(duplicate):
                if target is not None:
                    duplicate = target
                else:
                    duplicate = cmds.duplicate(sourceName, n=duplicate)[0]
            if parentDuplicate != stopNode:
                connectLike(parentDuplicate, duplicate, parent, current)
            else:
                connectLikeSwitchMaster(parentDuplicate, duplicate, parent, current, switchAttrs)
    return duplicate

duplicateNodeTo("joint_Left", "master", "joint_Right", switchAttrs=[('rotateY', 'rotateX')])
