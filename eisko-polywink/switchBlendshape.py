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
        self._getterVarUpdate = {}
        self.layout = None
        self.parent = None
        self._height = 100
        self._width = 500
        self.setParent(parent)
        self._scriptJobIndex = []
        self.childrenLayout = None
        self.bgc = False
        self._dragged = False
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
        if name in self._getterVarUpdate:
            for func in self._getterVarUpdate[name]:
                func()

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
                    print("FORM", s, e, n, m)
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

class Template(Module):

    def __init__(self):
        Module.__init__(self, None)
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)

        #example
        self.width = 100
        self.height = 200

    # Loading methods
    def load(self):
        ################
        # LOAD UI HERE #
        ################
        self.ui_buttonA = cmds.button("buttonA", p=self.layout, l='a')
        self.ui_buttonB = cmds.button("buttonB", p=self.layout, l='b')
        self.ui_text = cmds.text("text", p=self.layout, l='plop')

        self.attach(self.ui_buttonA, top="FORM", left="FORM")
        self.attach(self.ui_buttonB, top=0, right="FORM")
        self.attach(self.ui_text, top="FORM", left=self.ui_buttonA, right=self.ui_buttonB)

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

CURRENT_APP = Template

if __name__ == "__main__":
    main()



#####################################################
#                                                   #
#                       TMP                         #
#                                                   #
#####################################################



import re
NAME = "BS BOARD"
if cmds.workspaceControl(NAME, q=True, exists=True):
    cmds.deleteUI(NAME)
win = cmds.workspaceControl(NAME)
scrlLay = cmds.scrollLayout(p=win)
mainLay = cmds.formLayout(p=scrlLay)



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
        ''' Call this methode to make the function repeatable with 'g'
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


COLOR_BLUE = [0.32, 0.52, 0.65]
COLOR_LIGHTGREY = [0.36, 0.36, 0.36]



_jobIndex = []

def switchValue(attr, btn):
    v = cmds.getAttr("MASTER_BS_Node_cnt." + attr)
    cmds.setAttr("MASTER_BS_Node_cnt." + attr, not(v))
    color = COLOR_LIGHTGREY if v else COLOR_BLUE
    cmds.button(btn, e=True, bgc=color)

def updateColor(attr, btn):
    print("update " + attr)
    v = cmds.getAttr("MASTER_BS_Node_cnt." + attr)
    color = COLOR_LIGHTGREY if not v else COLOR_BLUE
    cmds.button(btn, e=True, bgc=color)

def killJob(jobIndex):
    for jobId in _jobIndex:
        cmds.scriptJob(kill=jobId, f=True)

lsBtn = []

for attr in cmds.listAttr("MASTER_BS_Node_cnt", k=True):
    side = True
    if attr.endswith("Left"):
        attrName = attr[:-4]
    elif attr.endswith("Right"):
        attrName = attr[:-5]
    else:
        side = False
        attrName = attr
    
    tmp = [i for i, j in lsBtn if i == attrName]
    if not len(tmp):
        lsBtn.append((attrName, side))

ac = []
af = []
ap = []

MARGIN = 3

prev = None
for name, sided in lsBtn:
    nameLabel = name[0].upper() + name[1:]
    nameLabel = " ".join(re.findall('[A-Z][^A-Z]*', nameLabel))
    if sided:
        print(name + " Left | " + name + " Right")
#        btnL = cmds.button(p=mainLay, l=name + " Left")
#        btnR = cmds.button(p=mainLay, l=name + " Right")
        btnL = cmds.button(p=mainLay, l=nameLabel,)
        btnR = cmds.button(p=mainLay, l=nameLabel, c=Callback(switchValue, name + " Right"))
        cmds.button(btnL, e=True, c=Callback(switchValue, name + "Left", btnL))
        cmds.button(btnR, e=True, c=Callback(switchValue, name + "Right", btnR))
        _jobIndex.append(cmds.scriptJob(attributeChange=("MASTER_BS_Node_cnt." + name + "Left", Callback(updateColor, name + "Left", btnL))))
        _jobIndex.append(cmds.scriptJob(attributeChange=("MASTER_BS_Node_cnt."+  name + "Right", Callback(updateColor, name + "Right", btnR))))
        af.append((btnL, "left", MARGIN))
        af.append((btnR, "right", MARGIN))
        ap.append((btnL, "right", int(MARGIN / 2), 50))
        ap.append((btnR, "left", int(MARGIN / 2), 50))
        if prev is None :
            af.append((btnR, "top", MARGIN))
            af.append((btnL, "top", MARGIN))
        else:
            ac.append((btnR, "top", MARGIN, prev))
            ac.append((btnL, "top", MARGIN, prev))
        prev = btnL
    else:
        print(name)
        btn = cmds.button(p=mainLay, l=nameLabel)
        cmds.button(btn, e=True, c=Callback(switchValue, name, btn))
        _jobIndex.append(cmds.scriptJob(attributeChange=("MASTER_BS_Node_cnt." + name, Callback(updateColor, name, btn))))
        if prev is None :
            af.append((btn, "top", MARGIN))
        else:
            ac.append((btn, "top", MARGIN, prev))
        af.append((btn, "left", MARGIN))
        af.append((btn, "right", MARGIN))
            
        prev = btn
print(_jobIndex)
#killJob(_jobIndex)
cmds.scriptJob(ro=True, uid=[mainLay, Callback(killJob, _jobIndex)])
cmds.formLayout(mainLay, e=True, af=af, ap=ap, ac=ac)