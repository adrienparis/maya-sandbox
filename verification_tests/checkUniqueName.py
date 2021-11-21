import maya.cmds as cmds

objs = cmds.ls()

for o in objs:
    if "|" in o:
        print(o)
