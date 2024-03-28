import maya.cmds as cmds
import maya.OpenMaya as omo
# (Open Maya Old)

# https://gist.github.com/chris-lesage/17834ce88917b9446cae553bd8e23a4d
def soft_selection_weights():
    ''' create and return a list of the soft selection weights '''
    #TODO: Would be nice to rewrite this using the new API. Low priority.
    #TODO: Debug on multiple selections

    # temporary hack. Turn off symmetry when reading MRichSelection until I learn to use symmetry.
    # as far as my tests go, this maintains the symmetrical selection but reads it like a whole selection.
    # otherwise, only one half will be reading by MRichSelection. How does getSymmetry() work?
    symmetryOn = cmds.symmetricModelling(q=True, symmetry=True)
    if symmetryOn:
        cmds.symmetricModelling(e=True, symmetry=False)

    selection = omo.MSelectionList()
    softSelection = omo.MRichSelection()
    omo.MGlobal.getRichSelection(softSelection)
    #softSelection.getSymmetry(selection)
    softSelection.getSelection(selection)

    dagPath = omo.MDagPath()
    selection.getDagPath(0, dagPath)
    component = omo.MObject()
    geoIter = omo.MItGeometry(dagPath)
    pointCount = geoIter.exactCount()
    #TODO: MFloatArray and MDoubleArray had strange inconsistencies. But a list might be slow.
    weightArray = [0.0] * pointCount

    iter = omo.MItSelectionList(selection, omo.MFn.kMeshVertComponent)
    #NOTE: since I commented out the while loop, this should just work on the first selected transform.
    #while not iter.isDone():
    iter.getDagPath(dagPath, component)
    fnComp = omo.MFnSingleIndexedComponent(component)
    if fnComp.hasWeights():
        for i in range(fnComp.elementCount()):
            element = fnComp.element(i)
            weight = fnComp.weight(i).influence()
            weightArray[element] = weight
    #iter.next()

    # Put the symmetry back to the way it was.
    cmds.symmetricModelling(e=True, symmetry=symmetryOn)
    return {i: e for i, e in enumerate(weightArray) if e > 0.001}


def grpCtrls(ctrl):
    cmds.setAttr(ctrl + ".overrideEnabled",1)
    cmds.setAttr(ctrl + ".overrideColor", 9)
    name = ctrl[2:]
    pose = cmds.group(ctrl, n="pose_" + name, a=True)
    inf = cmds.group(pose, n="inf_" + name, a=True)
    root = cmds.group(inf, n="root_" + name, a=True)
    return root, inf, ctrl

def createControl(name):
    sel = []
    sel += cmds.circle(nr=[1, 0, 0], ch=False)
    sel += cmds.circle(nr=[0, 1, 0], ch=False)
    sel += cmds.circle(nr=[0, 0, 1], ch=False, n=name)
    
    parent = sel.pop()
    for s in sel:    
        cmds.makeIdentity(s, apply=True, t=True, r=True, s=True)
    shapes = cmds.listRelatives(sel, c=True, f=True)
    cmds.parent(shapes, parent, r=True, s=True)
    
    for s in cmds.listRelatives(parent, c=True, f=True):
        cmds.setAttr(s + ".ihi", 0)
    
    cmds.delete(sel)
    return parent

def createCluster(mesh, weights, name="contact"):
    vtxs = ["{}.vtx[{}]".format(mesh, v) for v in weights.keys()]
    clstName, clstHandle = cmds.cluster(vtxs, n="cluster" + name[0].upper() + name[1:])

    for v, w in weights.items():
        cmds.percent(clstName, "{}.vtx[{}]".format(mesh, v), v=w)


    root, inf, ctrl = grpCtrls(createControl("c_" + clstName))
    toDelete = cmds.pointConstraint(clstHandle, root, mo=False)
    cmds.delete(toDelete)

    cmds.disconnectAttr(u'{}.worldMatrix'.format(clstHandle), u'{}.matrix'.format(clstName))
    cmds.disconnectAttr(u'{}Shape.clusterTransforms'.format(clstHandle), u'{}.clusterXforms'.format(clstName))
    cmds.delete(u'{}'.format(clstHandle), u'{}Shape'.format(clstHandle))
    cmds.connectAttr("{}.matrix".format(ctrl),  "{}.weightedMatrix".format(clstName))
    cmds.connectAttr("{}.parentInverseMatrix[0]".format(ctrl),  "{}.bindPreMatrix".format(clstName))
    cmds.connectAttr("{}.parentMatrix[0]".format(ctrl),  "{}.preMatrix".format(clstName))
    cmds.connectAttr("{}.worldMatrix[0]".format(ctrl),  "{}.matrix".format(clstName))

mesh = cmds.ls(sl=True, o=True)[0]

weights = soft_selection_weights()

createCluster(mesh, weights)
