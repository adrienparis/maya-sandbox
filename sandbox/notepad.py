#!/usr/bin/env python
# -- coding: utf-8 --

"""notepad.py: Notepad for maya that has a "notion" kinda feeling """

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "0.0.0"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import ctypes
import sys
try:
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
    
class Notepad():
    class Line():
        def __init__(self, parent):
            self.parent = parent
            self.childrenLayout = None
            self.layout = None
            self.af = []
            self.ac = []
            self.ap = []
            self._events = {}


        def eventHandler(self, event, function, *args):
            """Execute the given command when the UC call an [Event]
                event: type of Event
                function : function you want to call (some event might send more argument than your function ask)
                *args: Other argument you want to give
            """
            if not event in self._events:
                self._events[event] = []
            self._events[event].append((function, args))
            return self
        def runEvent(self, event, *args):
            """Manually run an event
            """
            if not event in self._events:
                return self
            for c in self._events[event]:
                if c[0] is None:
                    cmds.warning("Event \"" + event + "\" call a function not implemented yet -WIP-")
                    continue
                a = c[1] + args
                c[0](*a)
            return self

        def attach(self, elem, top=None, bottom=None, left=None, right=None, margin=(0,0,0,0)):
            '''attach "FORM": string
                      elem : layout/control
                      pos : float
                      None
            '''
            for s, n, m in [(top, "top", margin[0]), (bottom, "bottom", margin[1]), (left, "left", margin[2]), (right, "right", margin[3])]: 
                print(s, n, m, type(s))
                if s == None:
                    continue
                if isinstance(s, (str, unicode)):
                    if s == "FORM":
                        self.af.append((elem, n, m))
                    else:
                        self.ac.append((elem, n, m, s))
                if isinstance(s, float):
                    self.ap.append((elem, n, m, s))
            return elem

        def focus(self):
            cmds.setFocus(self.CTF_line)
            return self

        def delete(self):
            cmds.deleteUI(self.layout)

        def load(self):
            self.layout = cmds.formLayout(p=self.parent)
            self.CI_grab = self.attach(cmds.image(image="shelfTab.png"), top="FORM", left="FORM")
            self.CITB_delete = self.attach(cmds.iconTextButton(image="hotkeyFieldClear.png", c=Callback(self.runEvent, "Delete", self)), top="FORM", right="FORM")
            self.CTF_line = self.attach(cmds.textField(p=self.layout, bgc=[0.27, 0.27, 0.27], ec=Callback(self.runEvent, "NewLine"), aie=True), top="FORM", left=self.CI_grab, right=self.CITB_delete)



            cmds.formLayout(self.layout, e=True, af=self.af, ac=self.ac, ap=self.ap)
            return self

        def __str__(self):
            return str(self.childrenLayout)

    def __init__(self):
        self.name = self.__class__.__name__
        self._scriptJobIndex = []

    # Loading methods
    def load(self):
        '''loading The window
        '''
        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)
        self.LC_list = cmds.columnLayout(p=self.win, adj=True, rs=-5)

        # Call self.killJobs if the windows is killed
        cmds.scriptJob(ro=True, uid=[self.win, Callback(self._killJobs)])
        self._loadJobs()

        Notepad.Line(self.LC_list).load().eventHandler("NewLine", self.addNewLine).eventHandler("Delete", self.deleteLine)
        Notepad.Line(self.LC_list).load().eventHandler("NewLine", self.addNewLine).eventHandler("Delete", self.deleteLine)
        Notepad.Line(self.LC_list).load().eventHandler("NewLine", self.addNewLine).eventHandler("Delete", self.deleteLine)
        Notepad.Line(self.LC_list).load().eventHandler("NewLine", self.addNewLine).eventHandler("Delete", self.deleteLine)

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
    
    def addNewLine(self, *args):
        print(args)
        Notepad.Line(self.LC_list).load().eventHandler("NewLine", self.addNewLine).eventHandler("Delete", self.deleteLine).focus()

    def deleteLine(self, line):
        line.delete()

if __name__ == "__main__":
    if sys.executable.endswith(u"bin\maya.exe"):
        Notepad().load()
    else:
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)


def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    Notepad().load()

