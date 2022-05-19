#!/usr/bin/env python
# -- coding: utf-8 --

"""template.py: template of how to create a tool for maya"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.0.0-Alpha"
__copyright__   = "Copyright 2021, Creative Seeds"

import sys
import ctypes
try:
    # pylint: disable=F0401
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

class Callback():
    '''Use for maya interface event, because it send you back your argument as strings
    func : the function you want to call
    *args : your arguments
    **kwargs : your keywords arguments

    Example:
    cmds.button(c=Callback(myFunc, arg1, arg2))
    cmds.button(c=Callback(myFunc, arg1, arg2).repeatable())
    '''
    __author__ = "Adrien PARIS"
    __email__ = "a.paris.cs@gmail.com"
    __version__     = "3.1.0"
    __copyright__   = "Copyright 2021, Creative Seeds"

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.repeatArgs = args
        self.kwargs = kwargs
        self.repeatable_value = False
        self.getCommandArgument_value = False

    def repeatable(self):
        ''' Call this methode to make the function repeatable with 'g' key
        '''
        self.repeatable_value = True
        return self

    def getCommandArgument(self):
        ''' Call this methode to receive the argument of the event
        '''
        self.getCommandArgument_value = True
        return self

    def _repeatCall(self):
        return self.func(*self.repeatArgs, **self.kwargs)

    def __call__(self, *args):
        ag = self.args + args if self.getCommandArgument_value else self.args
        if self.repeatable_value:
            import __main__
            __main__.cb_repeatLast = self
            self.repeatArgs = ag
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast._repeatCall()"); ''')
        return self.func(*ag, **self.kwargs)

# Decorator
def callback(func):
    def wrapper(*args, **kwargs):
        return Callback(func, *args, **kwargs)
    return wrapper

class Module(object):
    '''Little bloc to encapsulate the UI's maya's system
    The parent must be either a Module, either a string that has the name of a maya's layout
    (cmds.layout, cmds.formLayout, cmds.columnLayout, ...)

    When converting this object to str, it print the layout to store his childrens
    like that, even if whe call it has a parent, it still return a maya's layout

    You must create a load function.

    Name your class starting by
    M_  if it's a simple module
    MG_ if it's a group of module
    MT_ if it's for a specific tools
    MC_ if it's for a control
    MGT_ if it's a group that contain tools
    '''
    # Maya's colors
    class Color():
        WHITE = [1, 1, 1]
        BLACK = [0, 0, 0]
        BLUE = [0.32, 0.52, 0.65]
        TURQUOISE = [0.28, 0.66, 0.70]
        EUCALYPTUS = [0.37,0.68,0.53]
        ORANGE = [0.86, 0.58, 0.34]
        DARKGREY = [0.21, 0.21, 0.21]
        GREY = [0.26, 0.26, 0.26]
        LIGHTGREY = [0.36, 0.36, 0.36]
        GREEN = [0.48, 0.67, 0.27]
        RED = [0.85, 0.34, 0.34]
        YELLOW = [0.86,0.81,0.53]

    _increment = 0
    _drag = None

    def __init__(self, parent, name=None):

        if name is None:
            name = self.__class__.__name__ + str(Module._increment)
            Module._increment += 1
        self.name = name
        self.childrens = []
        self.commands = {}
        self.layout = None
        self.parent = None
        self._height = 100
        self._width = 500
        self.setParent(parent)
        self._scriptJobIndex = []
        self.childrenLayout = None
        self.bgc = False
        self._dragged = False
        self.loaded = False
        self._af = []
        self._ac = []
        self._ap = []
        self._an = []

    def __str__(self):
        return str(self.childrenLayout)

    def __getattribute__(self, name):
        if name.endswith("_getter"):
            return self._cb_getter(name)
        if name == 'load':
            return object.__getattribute__(self, "_load")
        if name == 'unload':
            return object.__getattribute__(self, "_unload")
        if name == '__dir__':
            return object.__getattribute__(self, name)
        if name == "height":
            return cmds.layout(self.layout, q=True, h=True)
        if name == "width":
            return cmds.layout(self.layout, q=True, w=True)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == "height":
            self._height = value
            if self.layout is not None:
                cmds.layout(self.layout, e=True, h=value)
        if name == "width":
            self._width = value
            if self.layout is not None:
                cmds.layout(self.layout, e=True, w=value)

    def getter(self, name, func=None):
        pass

    @callback
    def _cb_getter(self, name, updateFunc=None):

        return object.__getattribute__(self, name)

    def setParent(self, parent):
        if self.parent is not None:
            if isinstance(self.parent, Module):
                self.parent.childrens.remove(self)
        self.parent = parent
        if isinstance(self.parent, Module):
            self.parent.childrens.append(self)

    def attach(self, elem, top=False, bottom=False, left=False, right=False, margin=(0,0,0,0)):
        '''For formLayout
            Register the attach information of your elem
            attach "FORM": string
                    elem : layout/control
                    pos : float
                    None
            return elem
            Use applyAttach() to attach the layout to your parent
        '''
        if isinstance(elem, Module):
            e = elem.layout
        else:
            e = elem
        for s, n, m in [(top, "top", margin[0]), (bottom, "bottom", margin[1]), (left, "left", margin[2]), (right, "right", margin[3])]:
            if isinstance(s, bool):
                if not s:
                    continue
            if s is None:
                self._an.append((e, n))
            if isinstance(s, (str, unicode)):
                if s.upper() == "FORM":
                    # print("FORM", s, e, n, m)
                    self._af.append((e, n, m))
                else:
                    self._ac.append((e, n, m, s))
            if isinstance(s, Module):
                self._ac.append((e, n, m, s.layout))
            if isinstance(s, (float, int)):
                print("INT", s, e, n, m)
                self._ap.append((e, n, m, float(s)))
        return elem

    def clearAttach(self):
        self._af = []
        self._ac = []
        self._ap = []
        self._an = []

    @staticmethod
    def _getParentLayout(attachList):
        parLayout = {}
        for af in attachList:
            e = af[0]
            if isinstance(e, Module):
                parLayout[e.parent] = [af] if e.parent not in parLayout else parLayout[e.parent] + [af]
            else:
                if cmds.layout(e, exists=True):
                    parent = cmds.layout(e, q=True, p=True)
                elif cmds.control(e, exists=True):
                    parent = cmds.control(e, q=True, p=True)
                else:
                    continue
                parLayout[parent] = [af] if parent not in parLayout else parLayout[parent] + [af]
        return parLayout

    def applyAttach(self):
        parLayoutAf = Module._getParentLayout(self._af)
        parLayoutAc = Module._getParentLayout(self._ac)
        parLayoutAp = Module._getParentLayout(self._ap)
        parLayoutAn = Module._getParentLayout(self._an)
        parentlayouts = parLayoutAf.keys() + parLayoutAc.keys() + parLayoutAp.keys() + parLayoutAn.keys()
        parentlayouts = list(dict.fromkeys(parentlayouts))
        for pl in parentlayouts:
            af = parLayoutAf[pl] if pl in parLayoutAf else []
            ac = parLayoutAc[pl] if pl in parLayoutAc else []
            ap = parLayoutAp[pl] if pl in parLayoutAp else []
            an = parLayoutAn[pl] if pl in parLayoutAn else []
            try:
                cmds.formLayout(pl, e=True, af=af, ac=ac, ap=ap, an=an)
            except Exception as inst:
                print(inst)
                raise Exception("Can't attach {} {}".format(pl, inst))

    def _load(self):
        # Create a workspaceControl if there is no parent
        par = self.parent
        if self.parent == None:
            if cmds.workspaceControl(self.name, exists=1):
                cmds.deleteUI(self.name)
            self.win = cmds.workspaceControl(self.name, ih=self._height, iw=self._width, retain=False, floating=True, h=self._height, w=self._width)
            par = self.win

        # Create Default layout and ChildrenLayout
        self.layout = cmds.formLayout(parent=par)
        self.childrenLayout = cmds.formLayout(p=self.layout)
        defaultLayout = self.layout
        defaultChildrenLay = self.childrenLayout

        # Execute The function develope by the user
        object.__getattribute__(self, "load")()

        # Delete Default Layout & ChildrenLayout if not used
        if self.childrenLayout != defaultChildrenLay:
            if cmds.layout(defaultChildrenLay, q=True, ex=True):
                cmds.deleteUI(defaultChildrenLay)
        else:
            self.attach(self.childrenLayout, top="FORM", bottom="FORM", left="FORM", right="FORM")

        if self.layout != defaultLayout:
            if cmds.layout(defaultLayout, q=True, ex=True):
                cmds.deleteUI(defaultLayout)

        # Apply Attach to the form Layout
        self.applyAttach()

        # log UnloadEvent
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self.unloadEvent)])

        # manage ScriptJob events
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self._killJobs)])
        self.loadJobs()

        self.loaded = True

        # so the function load() can be callable
        return self

    def load(self):
        ''' Put your main layout in the self.layout
        If you use a formeLayout use self.attach()
        Put the layout where the childrens will go in self.childrenLayout
        '''
        # raise Exception('load function not implemented')

    def reload(self):
        self.unload()
        self.load()

    def _unload(self):
        if self.layout == None:
            return self
        for c in self.childrens:
            c.unload()
        if cmds.workspaceControl(self.layout, exists=1):
            cmds.deleteUI(self.layout)
        self.loaded = False
        return self

    def unload(self):
        '''Unload function'''
        pass

    def unloadEvent(self):
        '''Called function when the module is deleted'''
        pass

    # Jobs
    def loadJobs(self):
        '''Load all jobs
            Example :
            self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))
        '''
        pass

    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)
        self._scriptJobIndex = []

    # drag&Drop
    def _dragCb(self, dragControl, x, y, modifiers):
        Module._drag = self

        if not self._dragged:
            self.bgc = cmds.layout(self.layout, q=True, bgc=True)
            self.ebg = cmds.layout(self.layout, q=True, ebg=True)
        self._dragged = True
        cmds.layout(self.layout, e=True, ebg=True)
        cmds.layout(self.layout, e=True, bgc=Module.COLOR_BLUE)
    def _dropCb(self, dragControl, dropControl, messages, x, y, dragType):
        cmds.layout(Module._drag.layout, e=True, bgc=Module._drag.bgc)
        cmds.layout(Module._drag.layout, e=True, ebg=Module._drag.ebg)
        Module._drag._dragged = False
        Module._drag.move(self)
        Module._drag = None

    # Events
    def eventHandler(self, event, c, *args):
        if not event in self.commands:
            self.commands[event] = []
        self.commands[event].append((c, args))
    def runEvent(self, event, *args):
        if not event in self.commands:
            return
        for c in self.commands[event]:
            if c[0] is None:
                continue
            a = c[1] + args
            c[0](*a)

CURRENT_APP = Module

def info(message):
    mel.eval('trace -where ""; print "{}\\n"; trace -where "";'.format(message))

# This part is to load the application
def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    CURRENT_APP().load()

def initializePlugin(*args):
    '''To load the tool as a plugin
    '''
    CURRENT_APP().load()

def uninitializePlugin(*args):
    CURRENT_APP().unload()

def main():
    if sys.executable.endswith(u"bin\maya.exe"):
        CURRENT_APP().load()
    else:
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)



# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ YOUR APPLICATION  ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼

class labelDropper(Module):

    def __init__(self):
        Module.__init__(self, None)
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)

        #example
        self.width = 100
        self.height = 200

        self.path = ["", "path", "\\", "project", "123456789", "type", "ABCDEFG",
                     "name", "abcdefg", "step", "_V", "version", ".ma"]
        self.pathLays = []

    def reorderPath(self, bypassLoaded=False):
        if not (self.loaded or bypassLoaded):
            return

        prev = "FORM"
        for i, p in enumerate(self.pathLays):
            m = (7,7,-3,-3) if i % 2 == 0 else (5,5,-3,-3)
            prev = self.attach(p, top="FORM",bottom="FORM", left=prev, right=None, margin=m)
        self.attach(p, right="FORM", margin=(0,0,5,5))
        self.attach(self.pathLays[0], left="FORM", margin=(0,0,5,5))

    @callback
    def cb_remove(self, elem):
        print("removing {}".format(elem))

    @callback
    def cb_gapUpdateSize(self, gap, index):
        txt = cmds.textField(gap, q=True, tx=True)
        size = len(txt) * 7 + 11
        cmds.textField(gap, e=True, w=size)

        self.path[index] = txt

    @callback
    def cb_dragEvent(self, dragControl, x, y, modifiers):
        cmds.textField(dragControl, e=True, bgc=Module.Color.BLUE)

    @callback
    def cb_dropEvent(self, dragControl, dropControl, messages, x, y, dragType):
        print(messages, x, y, dragType)
        sep = max(x-7, 0)/7
        cmds.textField(dragControl, e=True, bgc=Module.Color.LIGHTGREY)
        dragIndex = self.pathLays.index(dragControl)
        dropIndex = self.pathLays.index(dropControl)
        dragTxt = self.path[dragIndex]
        dropTxt = self.path[dropIndex]
        # print(self.path)
        # print([cmds.textField(x, q=True, tx=True) for x in self.pathLays])
        # print(dragIndex, dropIndex)

        self.path[dragIndex - 1] = self.path[dragIndex - 1] + self.path[dragIndex + 1]
        self.path[dragIndex + 1] = dropTxt[sep:]
        self.path[dropIndex] = dropTxt[:sep]

        for v, l in zip(self.path, self.pathLays)[::2]:
            print(v, l)
            size = len(v) * 7 + 11
            cmds.textField(l, e=True, tx=v, w=size)

        for p in [self.path, self.pathLays]:
            label = p.pop(dragIndex)
            field = p.pop(dragIndex)
            i = 1 if dropIndex < dragIndex else -1
            p.insert(dropIndex + i, field)
            p.insert(dropIndex + i, label)


            # swapElem = (p[dragIndex + 1], p[dragIndex], p[dropIndex + 2], p[dropIndex + 1])
            # p[dropIndex + 2], p[dropIndex + 1], p[dragIndex + 1], p[dragIndex] = swapElem
        # self.pathLays[dragIndex + 1], self.pathLays[dragIndex] = self.pathLays[dropIndex + 1], self.pathLays[dropIndex]

        print("{} |{}| {}".format(dropTxt[:sep], dragTxt, dropTxt[sep:]))
        print(self.path)
        print([cmds.textField(x, q=True, tx=True) for x in self.pathLays])
        # cmds.textField(dropControl, e=True, bgc=Module.Color.ORANGE)
        self.reorderPath()
        self.applyAttach()

    # Loading methods
    def load(self):
        self.frame = cmds.formLayout(p=self.layout, bgc=Module.Color.DARKGREY)
        self.attach(self.frame, top="FORM", left="FORM", right="FORM")
        
        pm = cmds.popupMenu( parent=self.frame, button=3)
        labels = ["path","name","version","step"]
        for n in labels:
            cmds.menuItem(n, p=pm, i="addClip.png")
        ################
        # LOAD UI HERE #
        ################
        # self.ui_buttonA = cmds.button("buttonA", p=self.layout, l='a')
        # self.ui_buttonB = cmds.button("buttonB", p=self.layout, l='b')
        # self.ui_text = cmds.text("text", p=self.layout, l='plop')

        # self.attach(self.ui_buttonA, top="FORM", left="FORM")
        # self.attach(self.ui_buttonB, top=0, right="FORM")
        # self.attach(self.ui_text, top="FORM", left=self.ui_buttonA, right=self.ui_buttonB)

        if not self.pathLays:
            for i, label in enumerate(self.path):
                if i % 2 == 0:
                    text = str(label)
                    textWidth = len(text) * 7 + 11
                    tf = cmds.textField(tx=label, p=self.frame, ed=True, w=textWidth,
                                        bgc=Module.Color.DARKGREY, fn="fixedWidthFont",
                                        dpc=self.cb_dropEvent().getCommandArgument())
                    cmds.textField(tf, e=True, cc=self.cb_gapUpdateSize(tf, i))
                    self.pathLays.append(tf)
                else:
                    self.pathLays.append(None)

            for i, label in enumerate(self.path):
                if i % 2 == 1:
                    text = str(label)
                    textWidth = len(text) * 7 + 11
                    tf = cmds.textField(tx=label, p=self.frame, ed=False, w=textWidth, h=25,
                                        bgc=Module.Color.LIGHTGREY, fn="fixedWidthFont",
                                        dgc=self.cb_dragEvent().getCommandArgument())
                    self.pathLays[i] = tf
                    
        self.reorderPath(bypassLoaded=True)
        pass

    def unload():
        ##################
        # UNLOAD UI HERE #
        ##################
        pass

    def loadJobs(self):
        ##################
        # LOAD JOBS HERE #
        ##################
        pass

    def unloadEvent(self):
        ######################################
        # ACTION TO DO WHEN MODULE IS UNLOAD #
        ######################################
        pass

# ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

CURRENT_APP = labelDropper

if __name__ == "__main__":
    main()
