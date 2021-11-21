#!/usr/bin/env python

"""skinner.py: Tools to present the joints in an efficient view
   version: alpha 0.9
"""

__author__      = "Adrien PARIS"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
import math
# pylint: disable=F0401
import maya.cmds as cmds
import maya.mel as mel
from pymel.core import Callback

def hexToRGB(hexa):
    """
    :hexa:
    """
    rgb = []
    rgb.append((round(hexa / 0x10000) % 0x100) / 0x100)
    rgb.append((round(hexa / 0x100) % 0x100) / 0x100)
    rgb.append(float(hexa % 0x100) / 0x100)
    return rgb

class Attach(object):
    NONE = 0
    FORM = 1
    POS = 2
    CTRL = 3

    def __init__(self, parent):
        self.parent = parent
        self.margin = [0,0,0,0]
        self.none = 0
        self.form = 0
        self.position = 0
        self.controller = 0
        self._attachs = {}
        self._an = []
        self._af = []
        self._ap = []
        self._ac = []

    def __getattribute__(self,name):
        if name == 'none' or name == 'form' or name == 'position' or name == 'controller':
            self._createAttach()
            if name == 'none':
                return object.__getattribute__(self, "_an")
            elif name == 'form':
                return object.__getattribute__(self, "_af")
            elif name == 'position':
                return object.__getattribute__(self, "_ap")
            elif name == 'controller':
                return object.__getattribute__(self, "_ac")
        else:
            return object.__getattribute__(self, name)

    @staticmethod
    def __sideToValue(side):
        if side == "top" : return 0
        if side == "bottom" : return 1
        if side == "left" : return 2
        if side == "right" : return 3

    def _createAttach(self):
        self._an = []
        self._af = []
        self._ap = []
        self._ac = []
        for key, value in self._attachs.items():
            if type(value) is int:
                if value == Attach.NONE:
                    self._an.append((self.parent.layout, key))
                if value == Attach.FORM:
                    self._af.append((self.parent.layout, key, self.margin[Attach.__sideToValue(str(key))]))
            elif type(value) is tuple and len(value) == 2:
                if value[0] == Attach.POS:
                    self._ap.append((self.parent.layout, key, self.margin[Attach.__sideToValue(str(key))], value[1]))
                if value[0] == Attach.CTRL:
                    if type(value[1]) is str or type(value[1]) is unicode:
                        self._ac.append((self.parent.layout, key, self.margin[Attach.__sideToValue(str(key))], value[1]))
                    else:
                        try:
                            self._ac.append((self.parent.layout, key, self.margin[Attach.__sideToValue(str(key))], value[1].layout))
                        except AttributeError:
                            log.debug.warning(value[1] + "is not supported")

    def attach(self, margin, attachs):
        #check if margin is (0), (0,0) or (0,0,0,0)

        # self.margin = [0,0,0,0]
        if margin != -1:
            if type(margin) is int:
                self.margin = [margin, margin, margin, margin]
            if type(margin) is tuple and len(margin) == 2:
                self.margin = [margin[0], margin[0], margin[1], margin[1]]
            if type(margin) is tuple and len(margin) == 4:
                self.margin = [margin[0], margin[1], margin[2], margin[3]]
        self._attachs.update(attachs)

class UserControl(object):
    """ 
    Creating a userControl
    """

    class Event():
        LOAD = 1
        UNLOAD = 2
        REFRESH = 3
        RELOAD = 4
        SELFKILL = 5
        APPLYATTACH = 6
        CLICK = 7



    increment = 0

    def __init__(self, parent=None, name="UC", width=30, height=30):
        """Initialize
        
        :parent: str formlayout
        """
        # super(UserControl, self).__init__()
        self.update = []
        self.parentUC = None
        self.parentLay = None
        self.layout = None
        self.color = {"background" : "background"}
        self.colorTheme = {"main": 0x404040,
                           "secondary": 0x454545,
                           "button": 0x606060,
                           "highlight": 0x5285a6,
                           "background":0x444444,
                           "backgroundSecondary":0x494949,
                           "font": 0xeeeeee
                           }
        self.setParent(parent)
        self._childrens = []
        self._events = {}
        self._clicksEvents = []
        self._clicksEventsLoaded = []
        self.name = name
        self.visible = True
        self.width = width
        self.height = height
        self.loaded = False
        self.pins = Attach(self)
        self.layout = None

    def _load(self):
        if self.name == "UC":
            name = self.__class__.__name__ + str(UserControl.increment)
            UserControl.increment += 1
        else:
            name = self.name
        # log.debug.info("loading " + self.__class__.__name__ + "...")
        if not self.loaded:
            if self.parentLay is None:
                if cmds.workspaceControl(name, exists=1):
                    cmds.deleteUI(name)
                self.parentLay = cmds.workspaceControl(name, retain=False, iw=self.width, ih=self.height, floating=True)
            self.layout = cmds.formLayout(name + "Lay", parent=self.parentLay, bgc=hexToRGB(self.colorTheme[self.color["background"]]), h=self.height, w=self.width, vis=self.visible)
            self.loaded = True
            for c in self._childrens:
                c.parentLay = self.layout
            object.__getattribute__(self, "load")()
        else:
            # log.debug.warning(name + " is already loaded")
            if self.height == -1 or self.width == -1:
                cmds.formLayout(self.layout, e=True, parent=self.parentLay)
            else:
                cmds.formLayout(self.layout, e=True, parent=self.parentLay, h=self.height, w=self.width)
        self._eventClickLoading()
        for c in self._childrens:
            c.load()
        # if self.parentUC is not None:
        #     self.parentUC.applyAttach()
        self.applyAttach()
        self.runEvent(self.Event.LOAD)

    def _refresh(self):
        if self.loaded:
            # log.debug.info("refresh " + self.__class__.__name__ + "...")
            self.update = []
            object.__getattribute__(self, "refresh")()
            for c in self._childrens:
                c.refresh()
            self.runEvent(self.Event.REFRESH)
  
    def _unload(self):
        if self.layout is None:
            return
        # log.debug.info("unload " + self.__class__.__name__ + "...")
        self.loaded = False
        for c in self._childrens:
            c.unload()
        object.__getattribute__(self, "unload")()
        if cmds.formLayout(self.layout, exists=1):
            cmds.deleteUI(self.layout)
        if cmds.workspaceControl(self.parentLay, exists=1):
            cmds.deleteUI(self.parentLay)
        self.loaded = False
        self.runEvent(self.Event.UNLOAD)

    def load(self):
        if self.__class__.__name__ is "UserControl":
            return
        # log.debug.warning("[" + self.__class__.__name__ + "][load] method is not implemented")

    def refresh(self):
        if self.__class__.__name__ is "UserControl":
            return
        # log.debug.warning("[" + self.__class__.__name__ + "][refresh] method is not implemented")

    def unload(self):
        if self.__class__.__name__ is "UserControl":
            return
        # log.debug.warning("[" + self.__class__.__name__ + "][unload] method is not implemented")

    def reload(self):
        # log.debug.info("reload " + self.__class__.__name__ + "...")
        self.unload()
        self.load()
        self.runEvent(self.Event.RELOAD)

    def killSelf(self):
        
        if not self.loaded:
            if cmds.workspaceControl(name, exists=1):
                cmds.deleteUI(name)
            self.runEvent(self.Event.SELFKILL)

    def __getattribute__(self,name):
        if name == 'load':
            return object.__getattribute__(self, "_load")
        elif name == 'refresh':
            return object.__getattribute__(self, "_refresh")
        elif name == 'unload':
            return object.__getattribute__(self, "_unload")
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name != "update":
            self.update.append(name)
        object.__setattr__(self, name, value)

    def visibility(self, vis):
        """Set the vibility of the UserControl

        :vis: boolean True=Visible False=Invisible
        """
        self.visible = vis
        if self.loaded:
            cmds.formLayout(self.layout, e=True, vis=vis)

    def attach(self, margin=(-1), **kwargs):
        """Attach the form to his parent

        Use Attach.NONE or Attach.FORM or (Attach.POS, [pos]) or (Attach.CTRL, [ctrl]) where [pos] is an Int and [ctrl] is a UserControl or a layout to the followings arguments

        :top:
        :bottom:
        :left:
        :right:

        :margin: 0 or (0,0) or (0,0,0,0) -> all or (top, bottom) or (top, bottom, left, right)
        """
        at = kwargs.items()
        keys = ["top", "bottom", "left", "right"]
        at = { k:v for k,v in at if k in keys }
        self.pins.attach(margin, at)


    def applyAttach(self):
        if len(self._childrens) == 0:
            return
        af = []
        ap = []
        ac = []
        an = []

        for ch in self._childrens:
            af += ch.pins.form
            ap += ch.pins.position
            ac += ch.pins.controller
            an += ch.pins.none
        if not(af == [] and af == [] and af == [] and af == []):
            cmds.formLayout(self.layout, edit=True, attachForm=af,attachPosition=ap,attachControl=ac,attachNone=an)
        self.runEvent(self.Event.APPLYATTACH)

    def setParent(self, parent):
        if parent is None:
            self.parentLay = parent
            self.parentUC = parent
        elif type(parent) is str or type(parent) is unicode:
            self.parentLay = parent
        else:
            try:
                if self.parentUC is not None:
                    self.parentUC.delChildren(self)
                self.parentUC = parent
                self.parentLay = parent.layout
                self.parentUC.addChildren(self)
                self.colorTheme = parent.colorTheme
                if parent.color["background"] == "background":
                    self.color["background"] = "backgroundSecondary"
            except:
                log.debug.error(str(parent) + " of type " + str(type(parent)) + " is unreadable")
        if self.layout is not None and self.parentLay is not None:
            cmds.formLayout(self.layout, edit=True, parent=self.parentLay)

    def addChildren(self, child):
        self._childrens.append(child)

    def delChildren(self, child):
        self._childrens.remove(child)


    def eventHandler(self, event, function, *args):
        """Execute the given command when the UC call an [Event]
            event: type of Event
            function : function you want to call (some event might send more argument than your function ask)
            *args: Other argument you want to give
        """
        if not event in self._events:
            self._events[event] = []
        self._events[event].append((function, args))
    def runEvent(self, event, *args):
        """Manually run an event
        """
        if not event in self._events:
            return
        for c in self._events[event]:
            if c[0] is None:
                # cmds.error("Event \"" + event + "\" call a function not implemented yet -WIP-")
                log.debug.warning("Event \"" + event + "\" call a function not implemented yet -WIP-")
                continue
            a = c[1] + args
            c[0](*a)
    def eventClickHandler(self, buttonMouse, function, *args, **kwargs):
        """Execute the given command when the UC call an [Event]
            buttonMouse: (1)Left click (2)Midlle click (3)Right click
            function : function you want to call (some event might send more argument than your function ask)
            ctrl, alt, shift: modifier you want to apply
            *args: Other argument you want to give
            /!\ Must be loaded
        """
        kwargs["ctrl"] = kwargs.get("ctrl", False)
        kwargs["alt"] = kwargs.get("alt", False)
        kwargs["shift"] = kwargs.get("shift", False)
        name = "Left" * (buttonMouse == 1) + "Middle" * (buttonMouse == 2) + "Right" * (buttonMouse == 3)
        name += "ctrl" * kwargs["ctrl"] + "alt" * kwargs["alt"] + "shift" * kwargs["shift"]
        self.eventHandler(name, function, *args)
        if not [buttonMouse, kwargs["ctrl"], kwargs["alt"], kwargs["shift"]] in self._clicksEvents:
            self._clicksEvents.append([buttonMouse, kwargs["ctrl"], kwargs["alt"], kwargs["shift"]]) 
        # if self.loaded:
        #     self.reload()
    def _eventClickLoading(self):
        """
        """
        for i in range(0, len(self._clicksEvents)):
            ce = self._clicksEvents[0]
            name = "Left" * (ce[0] == 1) + "Middle" * (ce[0] == 2) + "Right" * (ce[0] == 3)

            name += "ctrl" * ce[1] + "alt" * ce[2] + "shift" * ce[3]
            cmds.popupMenu("EvClk" + name + self.layout, parent=self.layout, button=ce[0],
                                                      ctl=ce[1], alt=ce[2], sh=ce[3],
                                                      pmc=Callback(self.runClickEvent, ce[0], ce[1], ce[2], ce[3]))
            self._clicksEventsLoaded.append(self._clicksEvents.pop(0))
    def runClickEvent(self, buttonMouse, ctrl, alt, shift):
        """Manually run a click mouse event
        """
        name = "Left" * (buttonMouse == 1) + "Middle" * (buttonMouse == 2) + "Right" * (buttonMouse == 3)
        name += "ctrl" * ctrl + "alt" * alt + "shift" * shift
        self.runEvent(name, buttonMouse, ctrl, alt, shift)

    def __str__(self):
        return str(self.layout)

class ButtonText(UserControl):
    def __init__(self, parent=None, text="button"):
        UserControl.__init__(self, parent)
        self.text = text
        self.pressed = False
        self.color["background"] = "button"
        self.align = "center"
        self.adaptiveSize = True
    def load(self):
        self.textLay = cmds.text(parent=self.layout, label=self.text, align=self.align)
        if self.adaptiveSize:
            cmds.formLayout(self.layout, e=True, w=cmds.text(self.textLay, q=True, w=True))
        cmds.formLayout(self.layout, e=True, af=[(self.textLay, "top", 0), (self.textLay, "bottom", 0), (self.textLay, "left", 0), (self.textLay, "right", 0)])
        cmds.formLayout(self.layout, e=True, bgc=hexToRGB(self.colorTheme["highlight" if self.pressed else "button"]))
    
    def refresh(self):
        cmds.text(self.textLay, e=True, label=self.text)
        if self.adaptiveSize:
            cmds.formLayout(self.layout, e=True, w=cmds.text(self.textLay, q=True, w=True))
        cmds.formLayout(self.layout, e=True, bgc=hexToRGB(self.colorTheme["highlight" if self.pressed else "button"]))
    
    def select(self):
        self.pressed = True
        self.color["background"] = "highlight"
        if self.loaded:
            cmds.formLayout(self.layout, e=True, bgc=hexToRGB(self.colorTheme[self.color["background"]]))

    def unselect(self):
        self.pressed = False
        self.color["background"] = "button"
        if self.loaded:
            cmds.formLayout(self.layout, e=True, bgc=hexToRGB(self.colorTheme[self.color["background"]]))
    
    def switch(self):
        if self.pressed:
            self.unselect()
        else:
            self.select()

class WarpPanel(UserControl):
    def __init__(self, parent=None, items = []):
        UserControl.__init__(self, parent)
        self.items = items
        self.OrientHoriz = True
        self.itemsLay = []
        self.innerMarge = 1

    def attachItems(self):
        af = []
        ac = []
        an = []
        old = None

        sideStern = "left" if self.OrientHoriz else "top"
        sideBow = "right" if self.OrientHoriz else "bottom"
        sidePort = "top" if self.OrientHoriz else "left"
        SideStarboard = "bottom" if self.OrientHoriz else "right"

        for c in self.items:
            c.parentLay = self.scrlFormLay
            c.load()
            an.append((c.layout, sideBow))
            if old == None:
                af.append((c.layout, sideStern, self.innerMarge))
            else:
                ac.append((c.layout, sideStern, self.innerMarge, old))
            af.append((c.layout, sidePort, self.innerMarge))
            af.append((c.layout, SideStarboard, self.innerMarge))
            old = c
            self.itemsLay.append(c)
            c.load()
        cmds.formLayout(self.scrlFormLay, e=True, af=af, ac=ac, an=an)

    def autoResizeFormLayout(self):
        if self.OrientHoriz:
            cmds.formLayout(self.scrlFormLay, e=True, h=cmds.scrollLayout(self.scrlLay, q=True, h=True) - 16)
        else:
            cmds.formLayout(self.scrlFormLay, e=True, w=cmds.scrollLayout(self.scrlLay, q=True, w=True) - 16)

    def load(self):
        self.scrlLay = cmds.scrollLayout(p=self.layout, cr=True, rc=Callback(self.autoResizeFormLayout))
        self.scrlFormLay = cmds.formLayout(p=self.scrlLay)
        cmds.formLayout(self.layout, e=True, af=[(self.scrlLay, "top", 3), (self.scrlLay, "bottom", 3), (self.scrlLay, "left", 3), (self.scrlLay, "right", 3)])
        self.attachItems()
    
    def clearList(self):
        pass

    def setList(self, list):
        for c in self.itemsLay:
            c.unload()

        self.items = list
        self.attachItems()
        pass

    def refreshList(self):
        pass
    
    def refresh(self):
        pass

class listJointsPannel(UserControl):
    def __init__(self, parent=None):
        UserControl.__init__(self, parent)
        self.sk = []
        self.selectedSk = []
        self.sideOn = [True, True, False]
        self.width = 200

    def load(self):
        self.getSkeletonBtn = ButtonText(text = "Get Skeleton", parent=self)

        self.leftBtn = ButtonText(text = "L", parent=self)
        self.middleBtn = ButtonText(text = "M", parent=self)
        self.rightBtn = ButtonText(text = "R", parent=self)

        self.getVtxSelBtn = ButtonText(text = "S", parent=self)
        self.autoSelBtn = ButtonText(text = "A", parent=self)

        self.leftBtn.pressed = True
        self.middleBtn.pressed = True

        self.leftBtn.eventClickHandler(1, self.sideFilter, self.leftBtn)
        self.middleBtn.eventClickHandler(1, self.sideFilter, self.middleBtn)
        self.rightBtn.eventClickHandler(1, self.sideFilter, self.rightBtn)

        self.getVtxSelBtn.eventClickHandler(1, self.getClosestJointBtn, self.getVtxSelBtn)
        self.autoSelBtn.eventClickHandler(1, self.runEvent, "autoSelectClick", self.autoSelBtn)

        self.leftBtn.adaptiveSize = False
        self.leftBtn.width = 30
        self.middleBtn.adaptiveSize = False
        self.middleBtn.width = 30
        self.rightBtn.adaptiveSize = False
        self.rightBtn.width = 30
        self.getVtxSelBtn.adaptiveSize = False
        self.getVtxSelBtn.width = 30
        self.autoSelBtn.adaptiveSize = False
        self.autoSelBtn.width = 30

        self.jointOutliner = WarpPanel(parent=self)
        self.jointOutliner.OrientHoriz = False

        self.getSkeletonBtn.attach(top=Attach.FORM, left=Attach.FORM, margin=3)
        self.leftBtn.attach(top=(Attach.CTRL, self.getSkeletonBtn), left=Attach.FORM, margin=1)
        self.middleBtn.attach(top=(Attach.CTRL, self.getSkeletonBtn), left=(Attach.CTRL, self.leftBtn), margin=1)
        self.rightBtn.attach(top=(Attach.CTRL, self.getSkeletonBtn), left=(Attach.CTRL, self.middleBtn), margin=1)
        self.autoSelBtn.attach(top=(Attach.CTRL, self.getSkeletonBtn), right=Attach.FORM, margin=1)
        self.getVtxSelBtn.attach(top=(Attach.CTRL, self.getSkeletonBtn), right=(Attach.CTRL, self.autoSelBtn), margin=1)
        self.jointOutliner.attach(top=(Attach.CTRL, self.leftBtn), bottom=Attach.FORM, left=Attach.FORM, right=Attach.FORM, margin=3)

        self.getSkeletonBtn.eventClickHandler(1, self.changeSkinnerBone)

        # self.loadList()
    
    def sideFilter(self, btn, *args):
        print(args)
        btn.switch()
        self.sideOn[0] = self.leftBtn.pressed
        self.sideOn[1] = self.middleBtn.pressed
        self.sideOn[2] = self.rightBtn.pressed
        self.loadList()

    def getClosestJointBtn(self, btn, *args):
        self.runEvent("clickClosestPoint")

    def selectBone(self, btn, sk, clck, ctrl, alt, shift):
        if not shift:
            for i in self.jointOutliner.items:
                i.unselect()
            self.selectedSk = []
        btn.switch()
        if sk in self.selectedSk:
            self.selectedSk.remove(sk)
        else:
            self.selectedSk.append(sk)
        selection = [i for i in self.jointOutliner.items if i.pressed]
        self.runEvent("selectionUpdate", self.selectedSk)

    def changeSkinnerBone(self, click, ctrl, alt, shift):
        sel = cmds.ls(sl=True, type="joint")
        if len(sel) != 1:
            return
        firstBone = SkJoin(sel[0])
        self.sk = SkJoin.treeToList(firstBone)
        print(self.sk)
        self.loadList()

    def sorteByProximity(self, pos):
        self.sk = sorted(self.sk, key=lambda j: j.getDistFrom(pos))
        self.loadList()


    def loadList(self):
        l = []
        for s in self.sk:
            if s.particule != "":
                continue
            if not ((s.side == "L" and self.sideOn[0]) or (s.side == "" and self.sideOn[1]) or (s.side == "R" and self.sideOn[2])):
                continue
            btn = ButtonText(text=(s.name)) # + " " + s.particule + " " + s.side))
            if s.side == "L":
                btn.align = "left"
            if s.side == "":
                btn.align = "center"
            if s.side == "R":
                btn.align = "right"
            if s in self.selectedSk:
                btn.select()
            btn.eventClickHandler(1, self.selectBone, btn, s)
            btn.eventClickHandler(1, self.selectBone, btn, s, shift=True)
            l.append(btn)
        self.jointOutliner.setList(l)

class grpJointsPanel(UserControl):
    def __init__(self, parent=None):
        UserControl.__init__(self, parent)
        self.mainJoint = None
        self.sideJoints = []
        self.width = 150
        self.color = {"background" : "main"}

    def selectionUpdate(self, sk, btn, clck, ctrl, alt, shift):
        self.runEvent("selectionUpdate", sk, btn, ctrl, shift)

    def load(self):
        self.mainJointBtn = ButtonText(self, text=self.mainJoint.name + " " + self.mainJoint.side)

        self.mainJointBtn.attach(top=Attach.FORM, left=Attach.FORM, right=Attach.FORM, margin=2)
        self.mainJointBtn.eventClickHandler(1, self.selectionUpdate, self.mainJoint, self.mainJointBtn)
        self.mainJointBtn.eventClickHandler(1, self.selectionUpdate, self.mainJoint, self.mainJointBtn, ctrl=True)
        self.mainJointBtn.eventClickHandler(1, self.selectionUpdate, self.mainJoint, self.mainJointBtn, shift=True)
        self.mainJointBtn.eventClickHandler(1, self.selectionUpdate, self.mainJoint, self.mainJointBtn, ctrl=True, shift=True)
        self.sideJointsBtn = []
        sideL = self.mainJointBtn
        sideR = self.mainJointBtn
        for i, j in enumerate(self.sideJoints):
            b = ButtonText(self, text=j.particule)
            b.eventClickHandler(1, self.selectionUpdate, j, b)
            b.eventClickHandler(1, self.selectionUpdate, j, b, ctrl=True)
            b.eventClickHandler(1, self.selectionUpdate, j, b, shift=True)
            b.eventClickHandler(1, self.selectionUpdate, j, b, ctrl=True, shift=True)
            self.sideJointsBtn.append(b)
            if i % 2 == 0:
                b.attach(left=Attach.FORM, right=(Attach.POS, 50), top=(Attach.CTRL, sideL), margin=2)
                sideL = b
            else:
                b.attach(right=Attach.FORM, left=(Attach.POS, 50), top=(Attach.CTRL, sideR), margin=2)
                sideR = b

class jointsPannel(UserControl):
    def __init__(self, parent=None):
        UserControl.__init__(self, parent)
        self.boneParentList = []
        self.boneList = []
        self.boneChildrenList = []
    def load(self):
        self.bonePanel = WarpPanel(self)
        self.boneParentPanel = WarpPanel(self)
        self.boneChildrensPanel = WarpPanel(self)


        self.boneParentPanel.attach(top=Attach.FORM, left=Attach.FORM, right=Attach.FORM, bottom=(Attach.POS, 33), margin=3)
        self.bonePanel.attach(top=(Attach.POS, 33), left=Attach.FORM, right=Attach.FORM, bottom=(Attach.POS, 66), margin=3)
        self.boneChildrensPanel.attach(top=(Attach.POS, 66), left=Attach.FORM, right=Attach.FORM, bottom=Attach.FORM, margin=3)

    def updateWarpPanel(self, warpPanel, list):
        l = []
        if list is None:
            return
        for i in list:
            if i is None:
                continue
            if i.particule != "":
                continue
            gjp = grpJointsPanel()
            gjp.mainJoint = i
            gjp.sideJoints = [x for x in i.getSibblings() if x.side == i.side]
            # b.eventClickHandler(1, self.selectBone, b)
            gjp.eventHandler("selectionUpdate", self.runEvent, "selectionUpdate")
            l.append(gjp)
        warpPanel.setList(l)
        # warpPanel.update()

        # if sk in self.selectedSk:
        #     self.selectedSk.remove(sk)
        # else:
        #     self.selectedSk.append(sk)
        # selection = [i for i in self.jointOutliner.items if i.pressed]
        # self.runEvent("selectionUpdate", self.selectedSk)

    def setJointsList(self, list):
        self.boneList = list

        self.boneParentList = []
        for i in self.boneList:
            if i.parent not in self.boneParentList and i.parent not in self.boneList:
                self.boneParentList.append(i.parent)

        self.boneChildrensList = []
        for i in self.boneList:
            children = [x for x in i.children if x not in self.boneList]
            children = [x for x in children if x not in self.boneParentList]
            self.boneChildrensList += children

        self.updateWarpPanel(self.boneParentPanel, self.boneParentList)
        self.updateWarpPanel(self.bonePanel, self.boneList)
        self.updateWarpPanel(self.boneChildrensPanel, self.boneChildrensList)

class SkinnerUI(UserControl):
    def __init__(self):
        UserControl.__init__(self, None)
        self.name = "Skinner"
        self.joints = []
        self.vtxSelection = GrpVTX()
        # self.vtxSelection.enableAutoSelect()
        self.vtxSelection.eventHandler("SelectionUpdated", self.updateVtxSelection)
        self.weightJointsSelected = []
        self.weightJointsSelectedBtn = []
        self.weights = {}
        self.autoSelect = False

    def updateSelection(self, sel):
        self.mainJointsPanel.setJointsList(sel)

    def updateVtxSelection(self, *args):
        print(self.vtxSelection.center)

    def weightUpdate(self, sk, btn, ctrl, shift):
        if not shift:
            print("reset")
            self.weightJointsSelected = []
            self.weights = {}
            for b in self.weightJointsSelectedBtn:
                b.unselect()
            self.weightJointsSelectedBtn = []
        self.weightJointsSelected.append(sk)
        btn.switch()
        if btn.pressed:
            self.weightJointsSelectedBtn.append(btn)
        else:
            self.weightJointsSelectedBtn.remove(btn)
        
        if not ctrl:
            self.weights[sk] = 0.0
            portion = 1.0 / len(self.weights)
            for s, w in self.weights.items():
                self.weights[s] = portion
            self.vtxSelection.setInfluentJoints(self.weights)
        print("~-~-~-~-~-~-")
        print(self.weights)
        print(self.vtxSelection.vtxs)
        # for v in self.vtxSelection.vtxs:
        #     print(self.vtxSelection.getInfluentJoints(v, self.vtxSelection.getSkinCluster(v)))

        print(sk, ctrl, shift)
        print(self.weightJointsSelected, self.weightJointsSelectedBtn)

    def sortByProximity(self, *args):
        self.vtxSelection.updateSelection()
        print(self.vtxSelection.getCenter())
        self.listPanel.sorteByProximity(self.vtxSelection.center)

    def switchAutoVtxSelect(self, btn, *args):
        print(args)
        self.autoSelect = not self.autoSelect
        btn.switch()
        if self.autoSelect:
            self.vtxSelection.enableAutoSelect()
        else:
            self.vtxSelection.disableAutoSelect()

    def load(self):
        self.listPanel = listJointsPannel(parent=self)
        self.mainJointsPanel = jointsPannel(parent=self)
        self.adjustPanel = UserControl(parent=self)

        self.listPanel.eventHandler("selectionUpdate", self.updateSelection)
        self.listPanel.eventHandler("clickClosestPoint", self.sortByProximity)
        self.listPanel.eventHandler("autoSelectClick", self.switchAutoVtxSelect)
        
        self.mainJointsPanel.eventHandler("selectionUpdate", self.weightUpdate)

        self.listPanel.attach(top=Attach.FORM, bottom=Attach.FORM, left=Attach.FORM, right=Attach.NONE, margin=3)
        self.mainJointsPanel.attach(top=Attach.FORM, bottom=(Attach.POS, 75), left=(Attach.CTRL, self.listPanel), right=Attach.FORM, margin=3)
        self.adjustPanel.attach(top=(Attach.CTRL, self.mainJointsPanel), bottom=Attach.FORM, left=(Attach.CTRL, self.listPanel), right=Attach.FORM, margin=3)

class SkJoin():
    def __init__(self, name, parent=None):
        #attrs
        self.longName = name
        if cmds.attributeQuery("liw", node=self.longName, ex=True):
            cmds.setAttr(self.longName + ".liw",  0)
        self.visibility = cmds.getAttr(name + ".v")

        self.side = "L" if self.longName.endswith("_L") else "R" if self.longName.endswith("_R") else  ""
        self.particule = ""
        self.pos = cmds.xform(name,q=1,ws=1,rp=1)

        #relatives
        self.parent = None
        self.setParent(parent)
        self.children = []
        self.mirror = None
        self.__getChildren()

        self.name = name

    def __getChildren(self):
        allChildren = cmds.listRelatives(self.longName, typ="joint")
        if allChildren is None:
            return None
        for c in allChildren:
            j = SkJoin(c, parent=self)
            j.setParent(self)
        for c in self.children:
            c.getShortName()

    # Parenting methodes
    def setParent(self, parent):
        oldParent = self.parent
        self.parent = parent
        if oldParent is not None:
            oldParent.__delChildren(self)
        if self.parent is not None:
            self.parent.__addChildren(self)

    def __addChildren(self, child):
        self.children.append(child)
    def addChildren(self, child):
        child.setParent(self)

    def __delChildren(self, child):
        self.children.remove(child)
    def delChildren(self, child):
        child.setParent(None)

    def getShortName(self):
        if self.name.startswith("sk_"):
            self.name = self.name[3:]
        if self.name.endswith("_L") or self.name.endswith("_R"):
            self.name = self.name[:-2]
        if not self.visibility:
            if self.parent is not None:
                for s in self.parent.children:
                    if s == self:
                        continue
                    if s.name in self.longName and s.particule == "" and s.side == self.side:
                        self.particule = self.name.replace(s.name, "").replace("_", "")
                        self.name = s.name

    def getSibblings(self):
        if self.parent == None:
            return []
        siblings = self.parent.children[:]
        siblings.remove(self)
        siblings = [x for x in siblings if x.name == self.name]
        return siblings

    @staticmethod
    def printTree(sk, depth=0):
        print("  " * depth + sk.name + "   " + sk.particule + "   " + sk.side + " ")
        for c in sk.children:
            SkJoin.printTree(c, depth + 1)

    @staticmethod
    def treeToList(tree):
        childs = [tree]
        for c in tree.children:
            # childs.append(c)
            childs += SkJoin.treeToList(c)
        return childs

    def getDistFrom(self, pos):
        return math.sqrt((self.pos[0] - pos[0])**2 + (self.pos[1] - pos[1])**2 + (self.pos[2] - pos[2])**2)

    def __repr__(self):
        return self.longName

class GrpVTX(object):
    def __init__(self):
        self.vtxs = []
        self.autoSelect = False
        self.center = [0, 0, 0]
        self._events = {}

    def enableAutoSelect(self):
        self.job = cmds.scriptJob(e=["SelectionChanged", self.updateSelection])
        self.autoSelect = True

    def disableAutoSelect(self):
        if not self.autoSelect:
            return
        cmds.scriptJob(kill=self.job)
        self.autoSelect = False

    def getSkinCluster(self, vtx):
        obj = vtx.split(".")[0]
        shp = obj.split("|")[-1]+ "Shape"
        shapeNode = obj + "|" + shp
        # histList = cmds.listHistory(shapeNode)
        histList = cmds.listHistory(obj)
        if histList:
            for histItem in histList:
                if cmds.objectType(histItem) == "skinCluster":
                    return histItem


    def getInfluentJoints(self, vtx, skinCluster):
        weights = cmds.skinPercent( skinCluster, vtx, query=True, value=True)
        joints = cmds.skinCluster( skinCluster, q=True, inf=True)
        jointWeight = {}
        for j, w in zip(joints, weights):
            if w < 0.001:
                continue
            jointWeight[j] = w
        return jointWeight

    def setInfluentJoints(self, joints):
        w = []
        for k, v in joints.items():
            w.append((str(k), v))
            cmds.setAttr(k.longName + ".liw",  0)
        for v in self.vtxs:
            skCls = self.getSkinCluster(v)
            # cmds.skinCluster(skCls, e=True, lw=False)
            cmds.skinPercent( skCls, v, transformValue=w)

    def updateSelection(self):
        sel = cmds.ls(sl=True, o=True)
        self.vtxs = []
        for s in sel:
            self.vtxs += GrpVTX.selectVertices(s)
        self.getCenter()
        self.runEvent("SelectionUpdated", self)

    def eventHandler(self, event, function, *args):
        """Execute the given command when the UC call an [Event]
            event: type of Event
            function : function you want to call (some event might send more argument than your function ask)
            *args: Other argument you want to give
        """
        if not event in self._events:
            self._events[event] = []
        self._events[event].append((function, args))
    def runEvent(self, event, *args):
        """Manually run an event
        """
        if not event in self._events:
            return
        for c in self._events[event]:
            if c[0] is None:
                # cmds.error("Event \"" + event + "\" call a function not implemented yet -WIP-")
                log.debug.warning("Event \"" + event + "\" call a function not implemented yet -WIP-")
                continue
            a = c[1] + args
            c[0](*a)

    @staticmethod
    def selectVertices(sel):
        sel_vtx = cmds.ls('{}.vtx[:]'.format(sel), fl=True, sl=True)
        sel_edg = cmds.ls('{}.e[:]'.format(sel), fl=True, sl=True)
        if len(sel_vtx) == 0:
            sel_vtx = cmds.polyListComponentConversion( sel_edg, tv=True)
        new_list = []
        for vtx in sel_vtx:
            if not(vtx.find(':') == -1):
                num_vtx = vtx[vtx.find('[') + 1:vtx.find(']')]
                # print(num_vtx)
                if ':' in num_vtx:
                    start = int(num_vtx[num_vtx.find('[') + 1:num_vtx.find(':')])
                    end = int(num_vtx[num_vtx.find(':') + 1:num_vtx.find(']')])
                else:
                    start = int(num_vtx)
                    end = start
                name = vtx[0:vtx.find('[') + 1]
                l = []
                for i in range(start, end + 1):
                    l.append((name + str(i) + ']').decode('unicode-escape'))
                new_list = new_list + l
            else:
                new_list.append(vtx)
        return new_list

    def getCenter(self):
        bb = cmds.exactWorldBoundingBox(self.vtxs)
                
        self.center = [bb[i] + (bb[3 + i] / 2) for i in range(3)]

        return self.center
        # OLD
        vmax = [-99999,-99999,-99999]
        vmin = [99999,99999,99999]
        
        for vtx in self.vtxs:
            tmp = cmds.xform(vtx, q=True, ws=True, t=True)[:3]
            vmin = [min(vmin[i], tmp[i]) for i in range(len(vmin))]
            vmax = [max(vmax[i], tmp[i]) for i in range(len(vmax))]

        self.center = [vmax[i] + vmin[i] for i in range(len(vmax))]
        self.center = [self.center[i] / 2 for i in range(len(self.center))]
        return self.center


window = SkinnerUI()
window.load()