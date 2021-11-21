import maya.cmds as cmds

#you need to select the top group with good UV and then the top group with bad ones
#the objects needs to be arranged the same way in both grps

def tUV(*args):
    grps = cmds.ls(sl=True)

    if len(grps) == 2:
        good = cmds.listRelatives(grps[0], allDescendents=True, type="mesh", f=True)
        good = [cmds.listRelatives(x, p=True, f=True)[0] for x in good]
        bad = cmds.listRelatives(grps[1], allDescendents=True, type="mesh", f=True)
        bad = [cmds.listRelatives(x, p=True, f=True)[0] for x in bad]
    else :
        cmds.confirmDialog( title='WWUV', message='You need to select two group', button=['ok'], defaultButton='ok')
    


    for mesh_source, mesh_target in zip(good, bad):
    
        shapes = cmds.listRelatives(mesh_target)


        if len(shapes)== 1 :
   
            cmds.select(mesh_source, replace=True)
            cmds.select(mesh_target, toggle=True)
            cmds.transferAttributes( mesh_source,mesh_target, transferUVs=2, transferColors=2 )
            cmds.select(mesh_target, replace=True)
            cmds.delete(ch = True)

        else :
            shapeBase, shapeOrig = shapes[0], shapes[1]
            cmds.select (shapeBase, replace=False)
            cmds.setAttr("{shapeBase}.intermediateObject".format(shapeBase=shapeBase), True);
            cmds.select (shapeOrig, replace=True)
            cmds.setAttr("{shapeOrig}.intermediateObject".format(shapeOrig=shapeOrig), False);
            cmds.select(clear=True)

            cmds.select(mesh_source, replace=True)
            cmds.select(mesh_target, toggle=True)
            cmds.transferAttributes( mesh_source,mesh_target, transferUVs=2, transferColors=2 )

            cmds.select(mesh_target, replace=True)
            cmds.delete(ch = True)

            cmds.select (shapeBase, replace=True)
            cmds.setAttr("{shapeBase}.intermediateObject".format(shapeBase=shapeBase),False);
            cmds.select (shapeOrig, replace=False)
            cmds.setAttr("{shapeOrig}.intermediateObject".format(shapeOrig=shapeOrig), True);
            cmds.select(clear=True)

    print ('done')
#UV WAWA

window = cmds.window("wawa_UV", title="WwUV", widthHeight=(250, 55), backgroundColor=(0.384, 0.384, 0.384))
cmds.columnLayout(adjustableColumn=True)
cmds.button(label='TRANSFERT',command=tUV)
cmds.button(label='Close', command=('cmds.deleteUI(\"'+window+'\", window=True)') )
cmds.setParent('..')
cmds.showWindow(window)

    
   