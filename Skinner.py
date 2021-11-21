#!/usr/bin/env python

"""miniToolRig.py: A little tool to help rigging character."""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "2.0.0"
__copyright__   = "Copyright 2021, Creative Seeds"

import ctypes
try:
# pylint: disable=F0401
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass


class Callback():
    __author__ = "Adrien PARIS"
    __email__ = "a.paris.cs@gmail.com"
    __version__     = "3.0.1"
    __copyright__   = "Copyright 2021, Creative Seeds"
    
    def __init__(self, func, *args, **kwargs):
        '''Use for maya interface event, because it send you back your argument as strings
        func : the function you want to call
        *args : your arguments
        '''
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.repeatable_value = False
        self.getCommandArgument_value = False

    def repeatable(self):
        self.repeatable_value = True
        return self

    def getCommandArgument(self):
        self.getCommandArgument_value = True
        return self

    def __call__(self, *args):
        if self.getCommandArgument_value:
            ag = self.args +  args
        else:
            ag = self.args
        if self.repeatable_value:
            cmds.repeatLast(ac='''python("import ctypes; print(ctypes.cast(''' + str(id(self)) + ''', ctypes.py_object).value())")''')
        return self.func(*ag, **self.kwargs)
    

if __name__ == "__main__":
    ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport".format(__version__), "{} info".format(__file__), 0)


def onMayaDroppedPythonFile(*_):
    window = Skinner()
    window.load()

class Skinner(object):
    def __init__(self):
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)
        self.userInterface = Skinner.UserInterface(self.name)
        self.userInterface.load()
        

    class UserInterface(object):
        def __init__(self, name):
            self.name = name

        def load(self):
            '''load the user interface
            '''
            if cmds.workspaceControl(self.name, exists=1):
                cmds.deleteUI(self.name)
            self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)

        class TreeListPanel():
            pass

        class RelativePanel():
            class SibblingPanel():
                pass
        
        class AdjustPanel():
            pass
