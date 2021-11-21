#!/usr/bin/env python
# -- coding: utf-8 --

"""template.py: template of how to create a tool for maya"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "0.0.0"
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
    __version__     = "3.1.0"
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
        ''' Call this methode to make the function repeatable with 'g'
        '''
        self.repeatable_value = True
        return self

    def getCommandArgument(self):
        ''' Call this methode to receive the argument of the event
        '''
        self.getCommandArgument_value = True
        return self
        

    def __call__(self, cb_repeatLast=False, *args):

        ag = self.args + args if self.getCommandArgument_value else self.args

        if self.repeatable_value and not cb_repeatLast:
            import ctypes; print(ctypes.cast(id(self), ctypes.py_object).value)
            import __main__
            __main__.cb_repeatLast = self
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast(cb_repeatLast=True)"); ''')

        return self.func(*ag, **self.kwargs)
    
if __name__ == "__main__":
    ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)


def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    Template().load()

class Template():

    def __init__(self):
        self.name = self.__class__.__name__
        self._scriptJobIndex = []
        pass

    # Loading methods
    def load(self):
        '''loading The window
        '''
        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)

        # Call self.killJobs if the windows is killed
        cmds.scriptJob(ro=True, uid=[self.win, Callback(self._killJobs)])
        self._loadJobs()

        ###################
        # LOAD STUFF HERE #
        ###################

        return self

    # Jobs
    def _loadJobs(self):
        '''Load all jobs
        '''
        # Example : 
        # self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))

    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)
    
