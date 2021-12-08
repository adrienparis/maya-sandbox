import datetime
import maya.app.general.executeDroppedPythonFile as dropModule
from maya import cmds

class manInTheMiddle():
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args):
        before = False
        for win in cmds.lsUI( type=['workspaceControl']):
            if win.startswith('MiniToolRig'):
                version = int(win.split("V1.4.")[1].split("-")[0])
                if version < 7:
                    before = True
        print("man in the middle")
        self.func(*args)
        for win in cmds.lsUI( type=['workspaceControl']):
            if win.startswith('MiniToolRig'):
                version = int(win.split("V1.4.")[1].split("-")[0])
                if version < 7:
                    cmds.deleteUI(win)
                    if not before:
                        cmds.sysFile( args[0], delete=True )

def activate():
    if not "func" in dir(dropModule.executeDroppedPythonFile):
        dropModule.executeDroppedPythonFile = manInTheMiddle(dropModule.executeDroppedPythonFile)

def deactivate():
    if "func" in dir(dropModule.executeDroppedPythonFile):
        dropModule.executeDroppedPythonFile = dropModule.executeDroppedPythonFile.func

present = datetime.datetime.now()

if present > datetime.datetime(2022, 1, 1) and present < datetime.datetime(2022, 1, 31):
    activate()
else:
    deactivate()

