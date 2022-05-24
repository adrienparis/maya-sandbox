for s in cmds.ls(sl=True):
    color = (0,0,0) if s.split('_')[2] == 'B' else (1,1,1)
    lamberName = s.replace("msh_", "shd_")
    cName = s.replace("msh_", "cnd_")
    cHandName = s.replace("msh_", "cnd_hand_")
    ctrl = s.replace("msh_", "c_")
    

    
    cName = cmds.shadingNode("condition", asUtility=True, n=cName)
    cHandName = cmds.shadingNode("condition", asUtility=True, n=cHandName)
    lamberName = cmds.shadingNode("lambert", asShader=True, n=lamberName)

    cmds.setAttr(cHandName + ".colorIfFalse", 0.4475, 0.895, 0, type="double3")
    cmds.setAttr(cHandName + ".colorIfTrue", 0, 0.461533, 1, type="double3")

    cmds.setAttr(cName + ".colorIfTrue", *color, type="double3")
    cmds.connectAttr(cHandName + ".outColor", cName + ".colorIfFalse")

    cmds.connectAttr(ctrl + ".hand", cHandName + ".firstTerm")
    cmds.setAttr(cHandName + ".secondTerm", 1)
    cmds.connectAttr(ctrl + ".hand", cName + ".firstTerm")
    cmds.setAttr(cName + ".secondTerm", 0)


    cmds.connectAttr(cName + ".outColor", lamberName + ".color")

    # cmds.hyperShade(s, lamberName, assign=True )
    # cmds.sets(s, e=True, forceElement= lamberName + 'SG' )
    # cmds.connectAttr(lamberName + ".outColor", lamberName+ "SG.surfaceShader")
    sg = cmds.sets(empty=True, renderable=True, noSurfaceShader=True,  name=lamberName + "SG")
    cmds.connectAttr( lamberName + ".outColor", sg+".surfaceShader", f=True)
    cmds.sets(s, e=True, forceElement=sg)


# assign shader
# sha = cmds.shadingNode('lambert', asShader=True, name="{}_{}_lambert".format(selection, x))
# sg = cmds.sets(empty=True, renderable=True, noSurfaceShader=True,  name="{}_{}_sg".format(selection, x))
# cmds.connectAttr( sha+".outColor", sg+".surfaceShader", f=True)
# cmds.sets(faces, e=True, forceElement=sg)
