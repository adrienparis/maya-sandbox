from maya import cmds

BS_NODE = "BSsourceNode"

bs = cmds.listAttr(BS_NODE + ".w", m=True)

mesh = "neck"


grp = cmds.group(n="BS_NECK", em=True)
for b in bs:
    print(b)
    cmds.setAttr(BS_NODE + "." + b, 1)
    dup = cmds.duplicate(mesh)
    cmds.parent(dup, grp)
    cmds.rename(dup, b)
    cmds.setAttr(BS_NODE + "." + b, 0)