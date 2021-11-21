import maya.cmds as cmds
def setColor(name, color):
    cmds.setAttr(name + ".overrideEnabled", 1)
    cmds.setAttr(name + ".overrideColor", color)
sl = cmds.ls(dag=True)
baseDAG = ["time1", "sequenceManager1", "hardwareRenderingGlobals", "renderPartition", "renderGlobalsList1", "defaultLightList1", "defaultShaderList1", "postProcessList1", "defaultRenderUtilityList1", "defaultRenderingList1", "lightList1", "defaultTextureList1", "lambert1", "standardSurface1", "particleCloud1", "initialShadingGroup", "initialParticleSE", "initialMaterialInfo", "shaderGlow1", "dof1", "defaultRenderGlobals", "defaultRenderQuality", "defaultResolution", "defaultLightSet", "defaultObjectSet", "defaultViewColorManager", "defaultColorMgtGlobals", "hardwareRenderGlobals", "characterPartition", "defaultHardwareRenderGlobals", "ikSystem", "hyperGraphInfo", "hyperGraphLayout", "globalCacheControl", "strokeGlobals", "dynController1", "lightLinker1", "persp", "top", "front", "side", "redshiftOptions", "defaultRedshiftPostEffects", "shapeEditorManager", "poseInterpolatorManager", "layerManager", "defaultLayer", "renderLayerManager", "defaultRenderLayer", ]
name = ""
l = []
for s in sl:
    p = cmds.listRelatives(s, p=True)
    if p is None and s not in baseDAG:
        l.append(s)
if len(l) != 1:
    exit("there is no or more than 1 master group")
else:
    name = l[0]
allMeshs = cmds.ls(dag=True, type='mesh')
bb = cmds.exactWorldBoundingBox(allMeshs)
radius = max(bb)
ctrls = ["WORLD", name, "offset"]
cmds.circle(n = "c_" + ctrls[0], r=radius * 3, nr=[0,1,0])
cmds.circle(n = "c_" + ctrls[1], r=radius * 2, nr=[0,1,0])
cmds.circle(n = "c_" + ctrls[2], r=radius * 1.5, nr=[0,1,0])
setColor("c_" + ctrls[0], 17)
setColor("c_" + ctrls[1], 14)
setColor("c_" + ctrls[2], 20)
gCtrls = cmds.group(n="CTRLS", em=True)
cmds.parent(gCtrls, name)
old = None
for c in ctrls:
    g = "c_" + c
    if c == ctrls[2]:
        sk = cmds.joint(g, n="sk_" + name)
        cmds.setAttr(sk + ".v", False)
        cmds.bindSkin(allMeshs + [sk], ta=True)
    cmds.setAttr(g + ".v", k=False, l=True)
    cmds.delete(g, ch=True)
    if c != "WORLD":
        g = cmds.group(g, n="pose_" + c)
        g = cmds.group(g, n="inf_" + c)
        g = cmds.group(g, n="root_" + c)
        cmds.parent(g, gCtrls)
        if old is not None:
            cmds.parentConstraint(old, "inf_" + c)
            cmds.scaleConstraint(old, "inf_" + c)
        old = "c_" +c
    else:
        cmds.parent(g, name)
        dm = cmds.createNode("decomposeMatrix", name="dm_WORLD")
        cmds.connectAttr(g + ".worldMatrix[0]", dm + ".inputMatrix", f=True)
        cmds.connectAttr(dm + ".outputTranslate", gCtrls + ".translate")
        cmds.connectAttr(dm + ".outputRotate", gCtrls + ".rotate")
        cmds.connectAttr(dm + ".outputScale", gCtrls + ".scale")
        cmds.connectAttr(dm + ".outputShear", gCtrls + ".shear")
        cmds.addAttr(g, longName='globalScale', defaultValue=1.0, minValue=0.001, maxValue=10000, k=True)
        cmds.connectAttr(g + ".globalScale", g + ".sx")
        cmds.connectAttr(g + ".globalScale", g + ".sy")
        cmds.connectAttr(g + ".globalScale", g + ".sz")
        cmds.setAttr(g + ".sx", k=False, l=True)
        cmds.setAttr(g + ".sy", k=False, l=True)
        cmds.setAttr(g + ".sz", k=False, l=True)