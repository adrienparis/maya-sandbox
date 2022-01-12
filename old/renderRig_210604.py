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

print(charas)
    
#Colorize ctrls
objsCtrls = {}
#get color of ctrls
for char in charas:
    print(char)
    ctrls = {}
    for o in charas[char]:
        n = o
        if ":" in o:
            n = o.split(":")[-1]
        if n.startswith("c_"):
            cmds.select(o, add=True)
            k = cmds.getAttr(o + ".overrideColor")
            if k not in ctrls:
                ctrls[k] = []
            ctrls[k].append(o)
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
        

