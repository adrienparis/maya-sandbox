#!/usr/bin/env python
# -- coding: utf-8 --

"""renderRig_211208.py: Will duplicate ctrls and Add them to redshift set to be colorized in a redshift render"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "2.1.1-ALPHA"
__copyright__   = "Copyright 2021, Creative Seeds"

from maya import cmds
COLOR = [
        0x000101,
        0x3d4147,
        0x7f7d83,
        0x9c0222,
        0x00035e,
        0x0003f4,
        0x044217,
        0x240148,
        0xc005c0,
        0x874430,
        0x411e1f,
        0x952500,
        0xfc0104,
        0x00fd04,
        0x023f9a,
        0xfeffff,
        0xfbfc06,
        0x65d9f7,
        0x40fca2,
        0xf8ada8,
        0xe5a975,
        0xfafb64,
        0x029552,
        0xa06632,
        0x9e9c2d,
        0x689f2f,
        0x2f9e5b,
        0x309f9d,
        0x2b659d,
        0x732aa0,
        0xa12c68,
]

COLORSNAMES = [
        "grey",
        "black",
        "darkGrey",
        "lightGrey",
        "plum",
        "darkBlue",
        "blue",
        "darkGreen",
        "darkPurple",
        "fushia",
        "lightBrown",
        "darkBrown",
        "brown",
        "red",
        "green",
        "royaleBlue",
        "white",
        "yellow",
        "cyan",
        "seaGreen",
        "plum",
        "rosyBrown",
        "lemon",
        "emerald",
        "bronze",
        "lightOlive",
        "olive",
        "turquoise",
        "mediumTurquoise",
        "indigo",
        "purple",
        "magenta",
]
def hexToRGB(hexa):
    """
    :hexa:
    """
    rgb = []
    rgb.append((round(hexa / 0x10000) % 0x100) / 0x100)
    rgb.append((round(hexa / 0x100) % 0x100) / 0x100)
    rgb.append(float(hexa % 0x100) / 0x100)
    return rgb

def getTopGrp(obj):
    while cmds.listRelatives(obj, p=True) is not None:
        obj = cmds.listRelatives(obj, p=True, f=True)
    return obj
    
objs = cmds.ls(type="transform")
charas = {}

for o in objs:
    n = o
    if ":" in o:
        n = o.split(":")[-1]
    if n.startswith("c_"):
        c = getTopGrp(o)[0]
        if c in charas:
            charas[c].append(o)
        else:
            charas[c] = [o]

def unlockAttr(elem):
	attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility']
	for a in attrs:
		cmds.setAttr("{}.{}".format(elem, a), l=False, k=True)

def isHidden(obj):
    while cmds.listRelatives(obj, p=True) is not None:
        if cmds.getAttr("{}.visibility".format(obj)):
            obj = cmds.listRelatives(obj, p=True, f=True)[0]
        else:
            return True
    return False

print(charas)


#Colorize ctrls
objsCtrls = {}
#get color of ctrls
for char in charas:
    print(char)
    
    sdwGrp = cmds.group(n="Shadows_" + char, em=True, w=True)

    ctrls = {}
    for o in charas[char]:
        n = o
        if ":" in o:
            n = o.split(":")[-1]
        if n.startswith("c_"):
            
            shadow = cmds.duplicate(o, n="Shadow_{}".format(o), rc=True)[0]
            shapes = cmds.listRelatives(shadow, f=True)
            if shapes == None:
                cmds.delete(shadow)
                continue
            for shp in shapes:
                if cmds.objectType(shp) != "nurbsCurve":
                    cmds.delete(shp)
            cmds.parent(shadow, sdwGrp)	
            unlockAttr(shadow)
            cmds.parentConstraint(o, shadow)
            cmds.setAttr("{}.visibility".format(shadow), not isHidden(o))

            cmds.select(o, add=True)
            if not cmds.getAttr(o + ".overrideEnabled"):
                shp = cmds.listRelatives(o, s=True, f=True)[0]
                if cmds.getAttr(shp + ".overrideEnabled"):
                    k = cmds.getAttr(shp + ".overrideColor")
                    print(o, k)
                else :
                    k = 0
            else:
                k = cmds.getAttr(o + ".overrideColor")
            if k not in ctrls:
                ctrls[k] = []
            ctrls[k].append(shadow)




    print(ctrls)
    objsCtrls[char] = ctrls

for ctrls in objsCtrls:
    ns_name =  ctrls.replace("|", "").replace(":", "_")
    ctrl_transform_name = ns_name + '_render_ctrls_param'
    print(ctrl_transform_name)
    cmds.group( em=True, name=ctrl_transform_name )
    cmds.addAttr(ctrl_transform_name, longName='width', defaultValue=0.01, minValue=0.0, k=True)
    cmds.addAttr(ctrl_transform_name, longName='precision', defaultValue=40, minValue=0.0, k=True)

    


    for t in ["translate", "rotate", "scale"]:
        for axe in ["X", "Y", "Z"]:
            cmds.setAttr( ctrl_transform_name + '.' + t + axe, k=False, cb=False )

    cmds.setAttr( ctrl_transform_name + '.visibility', k=False, cb=False )
    #set curveSet by color
    print(objsCtrls[ctrls])
    for k in objsCtrls[ctrls]:
        print(k, type(k))
        print(k, COLORSNAMES[k - 1], COLOR[k - 1])
        curveSetName = cmds.createNode("RedshiftCurveSet", n=ns_name + "_cs_mayaColor" + str(COLORSNAMES[k].capitalize()))
        
        cmds.connectAttr(ctrl_transform_name + ".width", curveSetName + ".width")
        cmds.connectAttr(ctrl_transform_name + ".precision", curveSetName + ".sampleRate")
        #cmds.setAttr(curveSetName + ".width", 0.01)
        #cmds.setAttr(curveSetName + ".sampleRate", 120)
        
        cmds.setAttr(curveSetName + ".rsEnableVisibilityOverrides", True)
        cmds.setAttr(curveSetName + ".rsShadowCaster", False)
        shaderName = "shd_mayaColor" + str(COLORSNAMES[k].capitalize())
        cmds.shadingNode("surfaceShader", asShader=True, name=shaderName)
        c = hexToRGB(COLOR[k - 1])
        print(c, hex(COLOR[k - 1]), k)
        cmds.setAttr(shaderName + ".outColor", c[0], c[1], c[2])
        i = 0
        for v in objsCtrls[ctrls][k]:
            print("\t" + v)
            cmds.connectAttr(v + ".instObjGroups[0]", curveSetName + ".dagSetMembers[" + str(i) + "]")
            i += 1
            # cmds.select(v, add=True)
        # cmds.select(clear=True)
        cmds.connectAttr(shaderName + ".outColor", curveSetName + ".shader")

print(cmds.ls(sl=True, showType=True))
objs = cmds.ls(type="transform")        
        

