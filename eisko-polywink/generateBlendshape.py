

# ###_________________________________________________________________####
# ##__select_all_BS__##
# BS_list = []
# for x in pm.ls(selection=True):
#     BS_list.append(str(x))
# ###_________________________________________________________________####
# BS_list=pm.listAttr('BS_Node.w',m=1)
# ###_________________________________________________________________####
# ##__select_all_Mesh_to_combine__##
# msh_to_combine = []
# for x in pm.ls(selection=True):
#     msh_to_combine.append(str(x))
# ###_________________________________________________________________####
# ##__FOR_SPECIFIC_EXISTING_BS_##
# print(BS_list)
# Prefixe = ""
# meshs_duplicated = []
# for b in BS_list:
#     for m in msh_to_combine:
#         pm.duplicate(m, n = m + "_duplicated")
#         meshs_duplicated.append(str(m + "_duplicated"))
#     pm.polyUnite(meshs_duplicated, n = Prefixe+b, ch = False)
#     for x in meshs_duplicated:
#         pm.delete(x)
# ###_________________________________________________________________####
# ##__FOR_SPECIFIC_NON-EXISTING_BS_##
# Prefixe = ""
# newBS = "Neutral"
# newBS = "tongueOut"
# meshs_duplicated = []
# for m in msh_to_combine:
#     pm.duplicate(m, n = m + "_duplicated")
#     meshs_duplicated.append(str(m + "_duplicated"))
# pm.polyUnite(meshs_duplicated, n = Prefixe+newBS, ch = False)
# for x in meshs_duplicated:
#     if pm.objExists(x):
#         pm.delete(x)
# ###_________________________________________________________________####
# ##__fill_BS_list__check_names__and_execute__##
# BS_Node = "MASTER_BS_Node_cnt"
# Prefixe = "XXX_"
# BS_Grp="BS_tmp_GRP"
# aim_constraint=pm.aimConstraint('Jaw_01_jnt', q=1)
# aim_constraint=aim_constraint+'.jawAimW0'
# for b in BS_list:
#     print("processing shape: "+b)
#     #reset BS value to zero to avoid interference
#     for w in BS_list:
#         pm.setAttr(BS_Node+'.'+w, 0)
#     #set BS value of list to 1
#     pm.setAttr(BS_Node+'.'+b, 1)
#     if "jaw" in b:
#         pm.setAttr(aim_constraint,1)
#     else:
#         pm.setAttr(aim_constraint,0)
#     #duplicate all mesh with 1 activated blendshape, combine and delete history
#     meshs_duplicated = []
#     for m in msh_to_combine:
#         meshs_duplicated.append(pm.duplicate(m, n = m + "_duplicated"))
#     if len(msh_to_combine) > 1 :
#         pm.polyUnite(meshs_duplicated, n = b, ch = False)
#         for x in meshs_duplicated:
#             if pm.objExists(x):
#                 pm.delete(x)
#     elif len(msh_to_combine) == 1 :
#         pm.rename(meshs_duplicated[0], b)
#     pm.rename(BS_Grp+'|'+b,Prefixe+b)
#     pm.hide(b)
#     #reset all BS value to zero
#     for w in BS_list:
#         pm.setAttr(BS_Node+'.'+w, 0)
# pm.setAttr(aim_constraint,1)
# ###_________________________________________________________________####
# ##__fill_BS_list__check_names__and_execute__##
# BS_Node = "BS_Node"
# Prefixe = "XXX_"
# BS_Grp="BS_tmp_GRP"
# for b in BS_list:
#     print("processing shape: "+b)
#     #reset BS value to zero to avoid interference
#     for w in BS_list:
#         pm.setAttr(BS_Node+'.'+w, 0)
#     #set BS value of list to 1
#     pm.setAttr(BS_Node+'.'+b, 1)
#     #duplicate all mesh with 1 activated blendshape, combine and delete history
#     meshs_duplicated = []
#     for m in msh_to_combine:
#         meshs_duplicated.append(pm.duplicate(m, n = m + "_duplicated"))
#     if len(msh_to_combine) > 1 :
#         pm.polyUnite(meshs_duplicated, n = b, ch = False)
#         for x in meshs_duplicated:
#             if pm.objExists(x):
#                 pm.delete(x)
#     elif len(msh_to_combine) == 1 :
#         pm.rename(meshs_duplicated[0], b)
#     #pm.rename(BS_Grp+'|'+b,Prefixe+b)
#     #pm.hide(b)
#     #reset all BS value to zero
#     for w in BS_list:
#         pm.setAttr(BS_Node+'.'+w, 0)
		
# ###_____________________________________________________
# ###Connect all new blendshapes to the rig Node with all blendshapes selected
# ###_____________________________________________________
# BSNode = "BS_Node"
# BSLoc = "MASTER_BS_Node_cnt"
# for x in BS_list:
#     if pm.objExists(BSLoc+"."+x):
#         pm.connectAttr(BSLoc+"."+x, BSNode+"."+x, force = True)
#         print (x + "  connected")
#     else:
#         print (str(BSLoc+"."+x) + '  not found')


# -- coding: utf-8 --
#!/usr/bin/env python


"""generateBlendshape.py: A little tool to help fuse mesh according to blendshapes"""

__author__      = "Adrien PARIS"
__email__       = "adrien.paris@eisko.com"
__version__     = "0.0.0-alpha"
__copyright__   = "Copyright 2022, EISKO"

import sys
import os
import ctypes
import threading
import time
import random
import webbrowser
import urllib
import shutil
import re
import getpass
import io
import subprocess
import re
from datetime import datetime
from maya import cmds
import pymel.core as pm


try:
    import maya.cmds as cmds
    import maya.mel as mel
    import pymel.core as pm
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

# Decorator
def callback(func):
    def wrapper(*args, **kwargs):
        return Callback(func, *args, **kwargs)
    return wrapper

def thread(func):
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return wrapper

def singleton(class_):
    class class_w(class_):
        __doc__ = class_.__doc__
        _instance = None
        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w,
                                    class_).__new__(class_,
                                                    *args,
                                                    **kwargs)
                class_w._instance._sealed = False
            return class_w._instance
        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
    class_w.__name__ = class_.__name__
    return class_w

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
    COLOR_WHITE = [1, 1, 1]
    COLOR_BLACK = [0, 0, 0]
    COLOR_BLUE = [0.32, 0.52, 0.65]
    COLOR_TURQUOISE = [0.28, 0.66, 0.70]
    COLOR_EUCALYPTUS = [0.37,0.68,0.53]
    COLOR_ORANGE = [0.86, 0.58, 0.34]
    COLOR_DARKESTGREY = [0.16, 0.16, 0.16]
    COLOR_DARKGREY = [0.21, 0.21, 0.21]
    COLOR_GREY = [0.26, 0.26, 0.26]
    COLOR_LIGHTGREY = [0.36, 0.36, 0.36]
    COLOR_GREEN = [0.48, 0.67, 0.27]
    COLOR_RED = [0.85, 0.34, 0.34]
    COLOR_YELLOW = [0.86,0.81,0.53]
    COLOR_LIGHTGREYGREEN = [0.42, 0.51, 0.49]
    COLOR_LIGHTGREYBLUE = [0.39, 0.47, 0.54]
    COLOR_LIGHTGREYRED = [0.51, 0.42, 0.42]

    increment = 0
    drag = None

    def __init__(self, parent, name=None):

        Module.increment += 1
        self.increment = Module.increment
        if name is None:
            name = self.__class__.__name__ + str(Module.increment)
        self.name = name
        self.childrens = []
        self.command = {}
        self.parent = None
        self.setParent(parent)
        self._scriptJobIndex = []
        self.childrenLayout = None
        self.layout = None
        self.bgc = None
        self.bgc = False
        self.dragged = False
        self.childrenAttach = {}
        self.af = []
        self.ac = []
        self.ap = []
        self.an = []

    def __str__(self):
        return str(self.childrenLayout)

    def __getattribute__(self, name):
        if name == 'load':
            return object.__getattribute__(self, "_load")
        if name == 'unload':
            return object.__getattribute__(self, "_unload")
        if name == "height":
            if self.layout is not None:
                return cmds.layout(self.layout, q=True, h=True)
            else:
                 return 0
        if name == "width":
            if self.layout is not None:
                return cmds.layout(self.layout, q=True, w=True)
            else:
                 return 0
        return object.__getattribute__(self, name)

    def setParent(self, parent):
        if self.parent is not None:
            if isinstance(self.parent, Module):
                self.parent.childrens.remove(self)
        self.parent = parent
        if isinstance(self.parent, Module):
            self.parent.childrens.append(self)

    def attach(self, elem, top=False, bottom=False, left=False, right=False, margin=(0,0,0,0)):
        if isinstance(elem, Module):
            e = elem.layout
        else:
            e = elem
        new_info = [top, bottom, left, right, margin]
        if e in self.childrenAttach:
            info = self.childrenAttach[e]
        else:
            info = [False, False, False, False, (0,0,0,0)]
        info = [i if n is False else n for i, n in zip(info, new_info)]
        self.childrenAttach[e] = info
        return elem

    def detach(self, elem):
        self.an = [e for e in self.an if e[0] != elem]
        self.af = [e for e in self.af if e[0] != elem]
        self.ap = [e for e in self.ap if e[0] != elem]
        self.ac = [e for e in self.ac if e[0] != elem and e[3] != elem]

    def clearAttach(self):
        self.af = []
        self.ac = []
        self.ap = []
        self.an = []

    @staticmethod
    def _getParentLayout(attachList):
        parLayout = {}
        for af in attachList:
            e = af[0]
            if isinstance(e, Module):
                parLayout[e.parent] = [af] if e.parent not in parLayout else parLayout[e.parent] + [af]
            elif e is None:
                continue
            else:
                if cmds.layout(e, exists=True):
                    parent = cmds.layout(e, q=True, p=True)
                elif cmds.control(e, exists=True):
                    parent = cmds.control(e, q=True, p=True)
                else:
                    continue
                parLayout[parent] = [af] if parent not in parLayout else parLayout[parent] + [af]
        return parLayout
    
    def fillAttachForm(self):
        for elem, info in self.childrenAttach.items():
            if isinstance(elem, Module):
                e = elem.layout
            else:
                e = elem
            for s, n, m in [(info[0], "top", info[4][0]), (info[1], "bottom", info[4][1]), (info[2], "left", info[4][2]), (info[3], "right", info[4][3])]:
                if s is False:
                    continue
                if s is None:
                    self.an.append((e, n))
                if s is True:
                    self.af.append((e, n, m))
                if isinstance(s, (str, unicode)):
                    if s.upper() == "FORM":
                        self.af.append((e, n, m))
                    else:
                        self.ac.append((e, n, m, s))
                if isinstance(s, Module):
                    self.ac.append((e, n, m, s.layout))
                if isinstance(s, (float, int)):
                    self.ap.append((e, n, m, float(s)))
        return elem

    def applyAttach(self):
        self.clearAttach()
        self.fillAttachForm()

        parLayoutAf = Module._getParentLayout(self.af)
        parLayoutAc = Module._getParentLayout(self.ac)
        parLayoutAp = Module._getParentLayout(self.ap)
        parLayoutAn = Module._getParentLayout(self.an)
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
            self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)
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
            self.attach(self.childrenLayout, top=True, bottom=True, left=True, right=True)

        if self.layout != defaultLayout:
            if cmds.layout(defaultLayout, q=True, ex=True):
                cmds.deleteUI(defaultLayout)

        # Apply Attach to the form Layout
        self.applyAttach()

        # log UnloadEvent
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self.unloadEvent)])

        # manage ScriptJob events
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self._killJobs)])
        self._loadJobs()

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
        pass

    def unloadEvent(self):
        pass

    def refresh(self):
        pass

    def move(self, other):
        parent = self.parent
        pos = parent.childrens.index(other)
        parent.childrens.remove(self)
        parent.childrens.insert(pos, self)
        parent.refresh()


    # Jobs
    def _loadJobs(self):
        '''Load all jobs
        '''
        pass
        # Example :
        # self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))
        # raise Exception('_loadJobs function not implemented')
    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)
        self._scriptJobIndex = []

    # drag&Drop
    def _dragCb(self, dragControl, x, y, modifiers):
        Module.drag = self

        if not self.dragged:
            self.bgc = cmds.layout(self.layout, q=True, bgc=True)
            self.ebg = cmds.layout(self.layout, q=True, ebg=True)
        self.dragged = True
        cmds.layout(self.layout, e=True, ebg=True)
        cmds.layout(self.layout, e=True, bgc=Module.COLOR_BLUE)
    def _dropCb(self, dragControl, dropControl, messages, x, y, dragType):
        cmds.layout(Module.drag.layout, e=True, bgc=Module.drag.bgc)
        cmds.layout(Module.drag.layout, e=True, ebg=Module.drag.ebg)
        Module.drag.dragged = False
        Module.drag.move(self)
        Module.drag = None

    # Events
    def eventHandler(self, event, c, *args):
        if not event in self.command:
            self.command[event] = []
        self.command[event].append((c, args))
    def runEvent(self, event, *args):
        if not event in self.command:
            return
        for c in self.command[event]:
            if c[0] is None:
                continue
            a = c[1] + args
            c[0](*a)

def Info(message):
    mel.eval('trace -where ""; print "{}\\n"; trace -where "";'.format(message))


class BlendshapeGenerator(Module):
    class MC_getChain(Module):
        def __init__(self, parent, name=None, color=Module.COLOR_TURQUOISE, filter=lambda x: True):
            Module.__init__(self, parent, name=name)
            self.chain = []
            self.chainLay = []
            self.color = color
            self.filter = filter

        def load(self):

            self.layout = cmds.formLayout(p=self.parent, w=5, bgc=[0.25, 0.25, 0.25])
            self.c_btn = self.attach(cmds.button(p=self.layout, l="Get " + self.name, c=Callback(self._setChain), bgc=Module.COLOR_LIGHTGREY), top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))
            self.scrlLay = self.attach(cmds.scrollLayout(p=self.layout, verticalScrollBarThickness=16, h=150, cr=True), top=self.c_btn, bottom="FORM", left="FORM", right="FORM")
            self.midLay = cmds.formLayout(p=self.scrlLay, w=5, bgc=[0.25, 0.25, 0.25])

            # self.attach(self.c_btn, top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))

            self.loadChain()
            self.applyAttach()

        def dragCb(self, dragControl, x, y, modifiers):
            cmds.control(dragControl, e=True, ebg=True)
            cmds.control(dragControl, e=True, bgc=Module.COLOR_BLUE)

        def dropCb(self, dragControl, dropControl, messages, x, y, dragType):
            if not dragControl in self.chainLay:
                return
            cmds.control(dragControl, e=True, bgc=self.color)
            old, new = self.chainLay.index(dragControl), self.chainLay.index(dropControl)
            self.chain.insert(new, self.chain.pop(old))
            self.chainLay.insert(new, self.chainLay.pop(old))

            self.refresh()

        def refresh(self):
            # self.attach(self.c_btn, top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))

            last = "FORM"
            for c in self.chainLay:
                last = self.attach(c, top=last, left="FORM", right="FORM", margin=(1,1,2,2))

            self.applyAttach()

        def deleteElem(self, elem, name):
            #WARNING - very hazardous (fatal error when clicking too quicly)
            if elem in self.chainLay:
                cmds.deleteUI(elem)
                self.chainLay.remove(elem)
                self.chain.remove(name)
                self.detach(elem)
            
            self.refresh()

        def loadChain(self):
            for c in self.chainLay:
                cmds.deleteUI(c)
            self.chainLay = []
            # self.attach(self.c_btn, top="FORM", left="FORM", right="FORM", margin=(4,20,1,1))

            last = "FORM"
            for c in self.chain:
                last = self.attach(cmds.text("Text" + c.capitalize(), p=self.midLay, bgc=self.color, l=c,
                                             dgc=Callback(self.dragCb).getCommandArgument(),
                                             dpc=Callback(self.dropCb).getCommandArgument()),
                                   top=last, left="FORM", right="FORM", margin=(1,1,2,2))
                self.gmc = cmds.popupMenu("gmc_{}_{}".format(last, c), parent=last, button=3, pmc=Callback(self.deleteElem, last, c))
                self.chainLay.append(last)

        def _setChain(self):
            sel = cmds.ls(sl=True)
            sel = [s for s in sel if self.filter(s)]
            self.setChain(sel)

        def setChain(self, sel):
            self.chain = sel
            self.clearAttach()
            self.loadChain()
            self.applyAttach()

    def __init__(self):
        Module.__init__(self, None)
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)

    @callback
    def cb_nonExisting(self):
        Prefixe = ""
        newBS = cmds.textField(self.tf_SpecNonBS, q=True, tx=True)
        meshs_duplicated = []
        for m in self.meshLay.chain:
            pm.duplicate(m, n = m + "_duplicated")
            meshs_duplicated.append(str(m + "_duplicated"))
        pm.polyUnite(meshs_duplicated, n = Prefixe+newBS, ch = False)
        for x in meshs_duplicated:
            if pm.objExists(x):
                pm.delete(x)

    @callback
    def cb_execJaw(self):
        BS_list = self.bsLay.chain
        msh_to_combine = self.meshLay.chain
        BS_Node = "MASTER_BS_Node_cnt"
        Prefixe = "XXX_"
        BS_Grp="BS_tmp_GRP"
        if not cmds.objExists("Jaw_01_jnt"):
            raise Exception("Jaw_01_jnt does not exists")
        aim_constraint=pm.aimConstraint('Jaw_01_jnt', q=1)
        aim_constraint=aim_constraint+'.jawAimW0'
        cmds.progressWindow(title="Execute + Jaw", progress=0, status="Starting")

        for i, b in enumerate(BS_list):
            cmds.progressWindow(e=True, progress=(float(i)/float(len(BS_list)) * 100), status=b)

            print("processing shape: "+b)
            #reset BS value to zero to avoid interference
            for w in BS_list:
                pm.setAttr(BS_Node+'.'+w, 0)
            #set BS value of list to 1
            pm.setAttr(BS_Node+'.'+b, 1)
            if "jaw" in b:
                pm.setAttr(aim_constraint,1)
            else:
                pm.setAttr(aim_constraint,0)
            #duplicate all mesh with 1 activated blendshape, combine and delete history
            meshs_duplicated = []
            for m in msh_to_combine:
                meshs_duplicated.append(pm.duplicate(m, n = m + "_duplicated"))
            if len(msh_to_combine) > 1 :
                pm.polyUnite(meshs_duplicated, n = b, ch = False)
                for x in meshs_duplicated:
                    if pm.objExists(x):
                        pm.delete(x)
            elif len(msh_to_combine) == 1 :
                pm.rename(meshs_duplicated[0], b)
            pm.rename(BS_Grp+'|'+b,Prefixe+b)
            pm.hide(b)
            #reset all BS value to zero
            for w in BS_list:
                pm.setAttr(BS_Node+'.'+w, 0)
        pm.setAttr(aim_constraint,1)
        cmds.progressWindow(endProgress=True)

    def load(self):
        '''loading The window
        '''
        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)
        self.layout = cmds.formLayout("BSGen_layout",parent=self.win)
        self.childrenLayout = self.attach(cmds.formLayout("BSGen_childLay", parent=self.layout), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,0,0,0))


        self.meshLay = self.attach(BlendshapeGenerator.MC_getChain(self, "mesh to combine", filter=BlendshapeGenerator.isMesh, color=Module.COLOR_LIGHTGREY).load(), top="FORM", left="FORM", right=50, margin=(3,3,3,3))
        self.bsLay = self.attach(BlendshapeGenerator.MC_getChain(self, "blendshapes", filter=BlendshapeGenerator.isMesh, color=Module.COLOR_LIGHTGREY).load(), top="FORM", left=50, right="FORM", margin=(3,3,3,3))
        self.btn_SpecBS = self.attach(cmds.button(p=self, l="For specific existing bs", en=False), top=self.meshLay, left="FORM", right="FORM", margin=(4,20,1,1))
        self.btn_SpecNonBS = self.attach(cmds.button(p=self, l="For specific non-existing bs", c=self.cb_nonExisting()), top=self.btn_SpecBS, left=None, right="FORM", margin=(4,20,1,1))
        self.tf_SpecNonBS = self.attach(cmds.textField(p=self, text="Neutral"), top=self.btn_SpecBS, left="FORM", right=self.btn_SpecNonBS, margin=(4,20,1,1))
        self.btn_ExecJaw = self.attach(cmds.button(p=self, l="fill BS list check names and execute + JAW", c=self.cb_execJaw()), top=self.btn_SpecNonBS, left="FORM", right="FORM", margin=(4,20,1,1))
        self.btn_Exec = self.attach(cmds.button(p=self, l="fill BS list check names and execute", en=False), top=self.btn_ExecJaw, left="FORM", right="FORM", margin=(4,20,1,1))
        # print(cmds.textField(self.tf_SpecNonBS, q=True, disableButtons=True))


    @staticmethod
    def isMesh(node):
        if cmds.objectType(node) == "transform":
            mesh = cmds.listRelatives(node, children=True, shapes=True, noIntermediate=True, type="mesh")
            if mesh is None:
                return False        
            return cmds.objectType(mesh, isType="mesh")
        return False        

if __name__ == "__main__":
    if sys.executable.endswith(u"bin\maya.exe"):
        BlendshapeGenerator().load()
    else:
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)

def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    BlendshapeGenerator().load()
    if os.path.exists(__file__ + "c"):
        os.remove(__file__ + "c")


