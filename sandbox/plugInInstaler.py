import maya
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
         
fMayaExitingCB = None
    
# Remove the UI when Maya exits
def removeUI(clientData):
    maya.cmds.setParent(maya.mel.eval("global string $gShelfTopLevel;$temp = $gShelfTopLevel"))
    if maya.cmds.layout("TestPluginShelf", exists=True):
        maya.cmds.deleteUI("TestPluginShelf", layout=True)
    
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "TestPlugin", "1.0", "Any")
    
    # Create shelf and buttons
    maya.cmds.setParent(maya.mel.eval("global string $gShelfTopLevel;$temp = $gShelfTopLevel"))

    if maya.cmds.layout("TestPluginShelf", exists=True) == False:
    maya.cmds.shelfLayout("GreenButton", style="textOnly")
    maya.cmds.shelfButton(image1="scriptIcon.png",
                          label="script", annotation="externalScript",
                          command="import ExternalScript reload(ExternalScript)", 
                          sourceType="python")

    # Add callback to clean up UI when Maya exits
    global fMayaExitingCB
    fMayaExitingCB =  OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kMayaExiting, removeUI)
    
    
# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    
    # Cleanup the UI and remove the callback when plug-in is unloaded
    maya.cmds.setParent(maya.mel.eval("global string $gShelfTopLevel;$temp = $gShelfTopLevel"))
    if maya.cmds.layout("TestPluginShelf", exists=True):
            maya.cmds.deleteUI("TestPluginShelf", layout=True)
    
    global fMayaExitingCB
        if (fMayaExitingCB != None):		
        OpenMaya.MSceneMessage.removeCallback(fMayaExitingCB)