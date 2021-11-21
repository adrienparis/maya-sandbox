#!/usr/bin/env python

"""stretchNsquash.py: Tools to create the stretch and squash"""

__author__      = "Adrien PARIS"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
import math
# pylint: disable=F0401
import maya.cmds as cmds
import maya.mel as mel
# define the global local scale of the name object

class StretchNsquash(object):
    # Callback function
    __cbFuncNum = 0
    __cbFunc = {}
    @staticmethod
    def Callback(func, *args, **kwargs):
        '''callback function to be called when using maya interface system
        to keep object as an object and not as a string
        '''
        if callable(func):
            StretchNsquash.__cbFuncNum += 1
            StretchNsquash.__cbFunc[StretchNsquash.__cbFuncNum - 1] = [func, args, kwargs]
            return "StretchNsquashWin.Callback(" + str(StretchNsquash.__cbFuncNum)  + ")"
        StretchNsquash.__cbFunc[func - 1][0](*StretchNsquash.__cbFunc[func - 1][1], **StretchNsquash.__cbFunc[func - 1][2])

    # Name of the application
    name = u"Stretch & Squash"

    # Preset
    armPresets = [{"name":"arm#SIDE#", 
                   "WORLD":"c_WORLD",
                   "temp chain start":"ik_shoulder#SIDE#",
                   "temp chain end":"ik_wrist#SIDE#",
                   "template":"ik_*",
                   "ctrl chain temp": "c_FK_shoulder#SIDE#",
                   "dynamicPoint start":"c_IK_shoulder#SIDE#",
                   "dynamicPoint end":"grp_reversehand#SIDE#",
                   "switch":"c_switch_arm#SIDE#",
                   "end ik ctrl":"c_IK_hand#SIDE#"
                   },
                 {"controller attribut":"c_IK_hand#SIDE#",
                  "ik chain temp":"ik_shoulder#SIDE#",
                  "sk chain temp":"sk_shoulder#SIDE#",
                  }]
    legPresets = [{"name":"leg#SIDE#",
                   "WORLD":"c_WORLD",
                   "temp chain start":"ik_hip#SIDE#",
                   "temp chain end":"ik_ankle#SIDE#",
                   "template":"ik_*",
                   "ctrl chain temp": "c_FK_hip#SIDE#",
                   "dynamicPoint start":"c_IK_hip#SIDE#",
                   "dynamicPoint end":"grp_reversefoot#SIDE#",
                   "switch":"c_switch_leg#SIDE#",
                   "end ik ctrl":"c_IK_foot#SIDE#"
                   },
                 {"controller attribut":"c_IK_foot#SIDE#",
                  "ik chain temp":"ik_hip#SIDE#",
                  "sk chain temp":"sk_hip#SIDE#",
                  }]

    class Frame(object):
        '''
        '''
        def __init__(self, parent, layout, color=[0.32, 0.52, 0.65]):
            self.chain = []
            self.color = color
            self.parentClass = parent
            self.parentLay = layout
            self.layout = None
            self.frame = None
            self.tempValue = ""
            self.load()

        def load(self):
            if self.layout is None:
                self.layout = cmds.formLayout(p=self.parentLay, bgc=[0.32, 0.32, 0.32])
            if self.frame is not None and cmds.formLayout(self.frame, exists=1):
                cmds.deleteUI(self.frame)
            self.frame = cmds.formLayout(p=self.layout, bgc=[0.32, 0.32, 0.32])
            oldLine = None
            ac = []
            af = []
            an = []
            if self.chain is not None:
                for c in self.chain:
                    lay = cmds.text(p=self.frame, label=c, bgc=self.color, align='left')
                    if oldLine is None:
                        af.append((lay, "top", 3))
                    else:
                        ac.append((lay, "top", 3, oldLine))
                    af.append((lay, "left", 3))
                    af.append((lay, "right", 3))
                    oldLine = lay
            # an.append((oldLine, "bottom"))
            cmds.formLayout(self.frame, e=True, ac=ac, af=af, an=an)
            cmds.formLayout(self.layout, e=True, af=[(self.frame, "top", 0), (self.frame, "right", 0), (self.frame, "bottom", 0)], ap=(self.frame, "left", 0, 5))

        def setValue(self, value):
            self.chain = value
            self.load()

        def setColor(self, color):
            self.color = color
            cmds.formLayout(self.frame, e=True, bgc=self.color )


    class Line(object):
        ''' Piece of user interface that can be added to another UI element
            parent: Must be a StretchNsquash class object
            layout: may formLayout
            name: name of the attribute you want
            annotation: Explication text
            color: [r, g, b] where r,g,b are float between 0 and 1            
            type: "PICKER" / "TEXT" 
        '''
        def __init__(self, parent, layout, name, annotation="", color=[0.32, 0.52, 0.65], type="PICKER", callbackEvent=None):
            self.name = name
            self.color = color
            self.parentClass = parent
            self.parentLay = layout
            self.value = ""
            self.layout = None
            self.callback = callbackEvent
            self.valueText = None
            self.titleText = None
            self.annotations = annotation
            self.type = type
            self.load()

        def setValue(self, value):
            self.value = value
            if self.valueText == None:
                return
            if self.type == "PICKER":
                cmds.text(self.valueText, e=True, label=self.value )
            elif self.type == "TEXT":
                cmds.textField(self.valueText, e=True, text=self.value )
            if self.callback is not None:
                self.callback(self.name, self.value)

        def setColor(self, color):
            self.color = color
            if self.titleText == None:
                return
            cmds.text(self.titleText, e=True, bgc=self.color )

        def load(self):
            self.layout = cmds.formLayout(p=self.parentLay, bgc=[0.32, 0.32, 0.32], ann=self.annotations)
            self.titleText = cmds.text(p=self.layout, label=" " + self.name.capitalize() + " : ", bgc=self.color )
            if self.type == "PICKER":
                self.valueText = cmds.text(p=self.layout, label=self.value, bgc=[0.275, 0.275, 0.275], align='left')
                self.clsBtn = cmds.button(parent=self.layout, label="cls", c=StretchNsquash.Callback(self.clsBtnAct), en=True)
                self.setBtn = cmds.button(parent=self.layout, label="set", c=StretchNsquash.Callback(self.setBtnAct))
                cmds.formLayout(self.layout, e=True,
                                af=[(self.titleText, "left", 3), (self.titleText, "top", 3), (self.titleText, "bottom", 3),
                                    (self.valueText, "top", 3), (self.valueText, "bottom", 3),
                                    (self.clsBtn, "top", 3),  (self.clsBtn, "bottom", 3),
                                    (self.setBtn, "top", 3), (self.setBtn, "right", 3), (self.setBtn, "bottom", 3)
                                    ],
                                ac=[(self.valueText, "left", 3, self.titleText),(self.valueText, "right", 3, self.clsBtn),
                                    (self.clsBtn, "right", 3, self.setBtn)]
                )
            elif self.type == "TEXT":
                # self.valueText = cmds.textField(p=self.layout, text=self.value, bgc=[0.275, 0.275, 0.275], cc="print('plop')")
                self.valueText = cmds.textField(p=self.layout, text=self.value, bgc=[0.275, 0.275, 0.275], cc=StretchNsquash.Callback(self.valueTextCcAct))
                cmds.formLayout(self.layout, e=True,
                                af=[(self.titleText, "left", 3), (self.titleText, "top", 3), (self.titleText, "bottom", 3),
                                    (self.valueText, "top", 3), (self.valueText, "bottom", 3), (self.valueText, "right", 3),
                                    ],
                                ac=[(self.valueText, "left", 3, self.titleText)]
                )

        def valueTextCcAct(self):
            self.value = cmds.textField(self.valueText, q=True, text=True)
            self.callback(self.name, self.value)

        def setBtnAct(self):
            sl = cmds.ls(sl=True)
            if len(sl) == 1:
                self.value = sl[0]
            cmds.text(self.valueText, e=True, label=self.value)
            if self.callback is not None:
                self.callback(self.name, self.value)

        def clsBtnAct(self):
            self.value = ""
            cmds.text(self.valueText, e=True, label=self.value)
            if self.callback is not None:
                self.callback(self.name, self.value)

    def __init__(self):
        self.win = None
        self.inputsLays = []
        self.outputsLays = []
        self.inputs = {}
        self.chains = {}

        self.chainDisplayFrame = {}

        #presets
        self.presetSide = "L"

    @staticmethod
    def fupper(string):
        return string[:1].upper() + string[1:]

    @staticmethod
    def drivenKey(inputNode, outputNode, keysInput, keysOutput):
        if len(keysInput) != len(keysOutput):
            return
        for i in range(0, len(keysInput)):
            cmds.setAttr(inputNode, keysInput[i])
            cmds.setAttr(outputNode, keysOutput[i])
            cmds.setDrivenKeyframe(outputNode, cd=inputNode, itt="linear", ott="linear")
            cmds.setAttr(inputNode, 0)

    def lineUpdate(self, name, value):
        print(name, value)

    def fillChainElemDisplay(self, name, value):
        self.loadToDict()
        chainName = name.rsplit(' ', 1)[0]
        chain = []
        if name in self.inputs:
            if chainName + " start" in self.inputs:
                if chainName + " end" in self.inputs:
                    chain = StretchNsquash.getChain(self.inputs[chainName + " start"], self.inputs[chainName + " end"])
        self.chainDisplayFrame[chainName].setValue(chain)

    def checkNecessariesInOut(self):
        necessaries = ["dynamicPoint start", "dynamicPoint end", "controller attribut", "ik chain temp", "temp chain start", "temp chain end", "template"]

        for n in necessaries:
            if not n in self.inputs:
                cmds.error("You must fill [" + n.capitalize() + "] attribute")

    def createCtrlAttributes(self):
        if not "controller attribut" in self.inputs:
            return
        c = self.inputs["controller attribut"]
        cmds.addAttr(c, longName='attrs', attributeType='enum', en=" ", k=True)
        cmds.addAttr(c, longName='stretch', defaultValue=0, minValue=0, maxValue=10, k=True)
        for i in range(0, len(self.chains["template"]) - 1):
            cmds.addAttr(c, longName='slide' + str(i + 1), defaultValue=0, minValue=-10, maxValue=10, k=True)
        # cmds.addAttr(c, longName='slide2', defaultValue=0, minValue=-10, maxValue=10, k=True)
        cmds.addAttr(c, longName='squash', defaultValue=0, minValue=0, maxValue=10, k=True)
        cmds.addAttr(c, longName='volume', defaultValue=0, minValue=-10, maxValue=10, k=True)

    def defineRatio(self):
        #naming
        pma = "pma_distance" + StretchNsquash.fupper(self.inputs["name"])
        loc1 = "loc_" + self.chains["template"][0]
        loc2 = "loc_" + self.chains["template"][-1]
        db = "db_" + self.inputs["name"]
        mdRatio = "md_ratio" + StretchNsquash.fupper(self.inputs["name"])
        cdn = "cdn_" + self.inputs["name"]

        # Get sum of all member length
        cmds.createNode("plusMinusAverage", n=pma)
        i = 0
        for c, ik in zip(self.chains["template"], self.chains["ik"])[1:]:
            mdl = "mdl_distance" + StretchNsquash.fupper(c)
            cmds.createNode("multDoubleLinear", n=mdl)
            pos = abs(cmds.getAttr(ik + ".ty"))
            cmds.setAttr(mdl + ".input1", pos)
            cmds.connectAttr(self.inputs["WORLD"] + ".globalScale", mdl + ".input2")
            cmds.connectAttr(mdl + ".output", pma + ".input1D[" + str(i) + "]")
            i += 1

        #dynamics points
        cmds.spaceLocator(n=loc1)
        cmds.spaceLocator(n=loc2)
        cmds.pointConstraint(self.inputs["dynamicPoint start"], loc1)
        cmds.pointConstraint(self.inputs["dynamicPoint end"], loc2)

        #distance between dynamics points
        cmds.createNode("distanceBetween", n=db)
        cmds.connectAttr(loc1 + ".worldMatrix[0]", db + ".inMatrix1")
        cmds.connectAttr(loc2 + ".worldMatrix[0]", db + ".inMatrix2")

        #ratio node
        cmds.createNode("multiplyDivide", n=mdRatio)
        cmds.connectAttr(db + ".distance", mdRatio + ".input1X")
        cmds.connectAttr(pma + ".output1D", mdRatio + ".input2X")
        cmds.setAttr(mdRatio + ".operation", 2)

        #Condition Node (If member is short or stretch)
        cmds.createNode("condition", n=cdn)
        cmds.connectAttr(db + ".distance", cdn + ".firstTerm")
        cmds.connectAttr(pma + ".output1D", cdn + ".secondTerm")
        cmds.connectAttr(mdRatio + ".outputX", cdn + ".colorIfTrueR")
        cmds.setAttr(cdn + ".operation", 2)

        return cdn

    def stretchSquashSlideVolumCN(self, cdn):  
        # Naming      
        md_attrs = "md_attrs" + StretchNsquash.fupper(self.inputs["name"])
        mdPow_squash = "mdPow_squash" + StretchNsquash.fupper(self.inputs["name"])
        mdDiv_squash = "mdDiv_squash" + StretchNsquash.fupper(self.inputs["name"])
        md_volume = "md_volume" + StretchNsquash.fupper(self.inputs["name"])
        bc_squash = "bc_squash" + StretchNsquash.fupper(self.inputs["name"])
        bc_stretch = "bc_stretch" + StretchNsquash.fupper(self.inputs["name"])
        ctrl = self.inputs["controller attribut"]

        # Creating nodes
        cmds.createNode("multiplyDivide", n=md_attrs)
        cmds.createNode("multiplyDivide", n=mdPow_squash)
        cmds.createNode("multiplyDivide", n=mdDiv_squash)
        cmds.createNode("multiplyDivide", n=md_volume)
        cmds.createNode("blendColors", n=bc_squash)
        cmds.createNode("blendColors", n=bc_stretch)

        # Connecting nodes
        cmds.connectAttr(ctrl + ".stretch", md_attrs + ".input1X")
        cmds.connectAttr(ctrl + ".squash", md_attrs + ".input1Y")
        cmds.connectAttr(md_attrs + ".outputX", bc_stretch + ".blender")
        cmds.connectAttr(cdn + ".outColorR", bc_stretch + ".color1R")
        cmds.connectAttr(cdn + ".outColorR", mdPow_squash + ".input1X")
        cmds.connectAttr(mdPow_squash + ".outputX", mdDiv_squash + ".input2X")
        cmds.connectAttr(mdDiv_squash + ".outputX", bc_squash + ".color1R")
        cmds.connectAttr(mdDiv_squash + ".outputX", bc_squash + ".color1B")
        cmds.connectAttr(md_attrs + ".outputY", bc_squash + ".blender")
        cmds.connectAttr(bc_squash + ".output", md_volume + ".input1")

        # setting node mode to division
        cmds.setAttr(mdDiv_squash + ".operation", 2)
        # setting node mode to power
        cmds.setAttr(mdPow_squash + ".operation", 3)
        # Setting attributes values
        cmds.setAttr(md_attrs + ".input2X", 0.1)
        cmds.setAttr(md_attrs + ".input2Y", 0.1)
        cmds.setAttr(bc_stretch + ".color2R", 1)
        cmds.setAttr(bc_stretch + ".color2B", 1)
        cmds.setAttr(mdPow_squash + ".input2X", 0.5)
        cmds.setAttr(mdDiv_squash + ".input1X", 1)
        cmds.setAttr(bc_squash + ".color1G", 1)
        cmds.setAttr(bc_squash + ".color2R", 1)
        cmds.setAttr(bc_squash + ".color2G", 1)
        cmds.setAttr(bc_squash + ".color2B", 1)

        # Creating driven key
        StretchNsquash.drivenKey(ctrl + ".volume", md_volume +".input2X", [-10,0,10], [0.01,1,2])
        StretchNsquash.drivenKey(ctrl + ".volume", md_volume +".input2Z", [-10,0,10], [0.01,1,2])

        # Create node connection link for each link of the ik chain (execpt the first one)
        i = 1
        chain = [self.chains["template"], self.chains["ik"]]
        for c, ik in zip(self.chains["template"], self.chains["ik"])[1:]:
            # Naming
            stretch = "mdl_stretch" + StretchNsquash.fupper(c)
            slide = "mdl_slide" + StretchNsquash.fupper(c)
            # Creating nodes
            cmds.createNode("multDoubleLinear", n=stretch)
            cmds.createNode("multDoubleLinear", n=slide)
            # Connecting nodes
            cmds.connectAttr(bc_stretch + ".outputR", stretch + ".input2")
            cmds.connectAttr(stretch + ".output", slide + ".input1")
            # Setting attribute value
            cmds.setAttr(stretch + ".input1", cmds.getAttr(ik + ".ty"))
            # Creating driven key
            StretchNsquash.drivenKey(ctrl + ".slide" + str(i), slide + ".input2", [-10,0,10], [0.01,1,2])
            cmds.connectAttr(slide + ".output", ik + ".translateY")
            i += 1

        for ik in self.chains["ik"][:-1]:
            cmds.connectAttr(md_volume + ".output", ik + ".scale")
        cmds.connectAttr(self.inputs["end ik ctrl"] + ".scale", self.chains["ik"][-1] + ".scale")
        

    def connectToSk(self):
        for t, sk, ik, ctrl in zip(self.chains["template"], self.chains["sk"], self.chains["ik"], self.chains["ctrl"]):
            # Naming
            bc = "bc_scale_" + t
            switch = self.inputs["switch"]
            # Creating nodes
            cmds.createNode("blendColors", n=bc)
            # Connecting nodes
            cmds.connectAttr(ik + ".scale", bc + ".color2")
            cmds.connectAttr(ctrl + ".scale", bc + ".color1")
            cmds.connectAttr(switch + ".IKtoFK", bc + ".blender")

            cmds.connectAttr(bc + ".output", sk + ".scale")
        # if "ori" in self.chains:
        #     for ori in self.chains["ori"]:
        #         print(ori)


    @staticmethod
    def getChain(start, end):
        ikChain = []
        ikChain.insert(0, end)
        c = cmds.listRelatives(ikChain[0], p=True, type="joint")
        while c is not None:
            ikChain.insert(0, c[0])
            if c[0] == start:
                break
            c = cmds.listRelatives(ikChain[0], p=True, type="joint")
        return ikChain

    def template(self, name, value):
        self.loadToDict()
        chain = []
        if not "template" in self.inputs or not "temp chain start" in self.inputs or not "temp chain end" in self.inputs:
            self.chains["template"] = chain
            self.chainDisplayFrame["temp chain"].setValue(chain)
            return
        chain = StretchNsquash.getChain(self.inputs["temp chain start"], self.inputs["temp chain end"])
        substr = self.inputs["template"].split("*")
        for i in range(0, len(chain)):
            for s in substr:
                chain[i] = chain[i].replace(s, "")
        self.chains["template"] = chain
        self.chainDisplayFrame["temp chain"].setValue(chain)
        self.chainDisplayFrame["temp chain"].tempValue = substr
        # for frame in self.chainDisplayFrame:
        #     if frame == "temp chain":
        #         continue
        #     f = self.chainDisplayFrame[frame]
        #     for c in f.chain:
        #         v = f.tempValue.replace("*", c)
        #         if cmds.objExists(v):
        #             newChain.append(v)
        #     self.chains[name.replace(" ", "").replace("temp", "").replace("chain", "")] = newChain
        #     f.setValue(newChain)
            

    def swapTemplate(self, name, value):
        if not "template" in self.chains:
            return
        chain = self.chains["template"]
        for i, v in enumerate(chain):
            if v in value:
                break
        presufix = value.replace(chain[i], "*")
        newChain = []
        if presufix == value:
            self.chains[name.replace(" ", "").replace("temp", "").replace("chain", "")] = newChain
            self.chainDisplayFrame[name.replace("temp", "").rstrip()].setValue(newChain)
            self.chainDisplayFrame[name.replace("temp", "").rstrip()].tempValue = ""
            return
        for c in chain:
            v = presufix.replace("*", c)
            if cmds.objExists(v):
                newChain.append(v)
        self.chains[name.replace(" ", "").replace("temp", "").replace("chain", "")] = newChain
        self.chainDisplayFrame[name.replace("temp", "").rstrip()].setValue(newChain)
        self.chainDisplayFrame[name.replace("temp", "").rstrip()].tempValue = presufix

    def executeSS(self):
        '''Apply the stretch and squash
        '''
        # get all link of the chain
        self.checkNecessariesInOut()
        cdn = self.defineRatio()
        self.createCtrlAttributes()
        self.stretchSquashSlideVolumCN(cdn)
        self.connectToSk()

    def loadToDict(self):
        self.inputs = {}
        for i in self.inputsLays:
            if type(i) != StretchNsquash.Line:
                continue
            if i.value == "":
                continue
            self.inputs[i.name] = i.value
        for o in self.outputsLays:
            if type(o) != StretchNsquash.Line:
                continue
            if o.value == "":
                continue
            self.inputs[o.name] = o.value

    def executeSsBtn(self):
        '''Is executed when th UI button is pressed
        to load all value that are setted
        '''
        self.loadToDict()
        self.executeSS()

    def presetLoad(self, preset):
        for a in self.inputsLays:
            if type(a) != StretchNsquash.Line:
                continue
            if a.name in preset[0]:
                a.setValue(preset[0][a.name].replace("#SIDE#", "_" + self.presetSide))
        for a in self.outputsLays:
            if type(a) != StretchNsquash.Line:
                continue
            if a.name in preset[1]:
                a.setValue(preset[1][a.name].replace("#SIDE#", "_" + self.presetSide))

    def presetDropListUpdate(self):
        item = cmds.optionMenu(self.presetDropList, q=True, v=True)
        if item == "Arm":
            self.presetLoad(self.armPresets)
        if item == "Leg":
            self.presetLoad(self.legPresets)

    def presetSwitchSide(self, side):
        for a in self.inputsLays:
            if type(a) != StretchNsquash.Line:
                continue
            if a.value.endswith("_" + self.presetSide):
                a.setValue(a.value[:-1] + side)
        for a in self.outputsLays:
            if type(a) != StretchNsquash.Line:
                continue
            if a.value.endswith("_" + self.presetSide):
                a.setValue(a.value[:-1] + side)

        self.presetSide = side
        if side == "L":
            cmds.button(self.presetBtnL, e=True, bgc=[0.75,0.25,0.25], en=False)
            cmds.button(self.presetBtnR, e=True, bgc=[0,0,1], en=True)
        elif side == "R":
            cmds.button(self.presetBtnL, e=True, bgc=[1,0,0], en=True)
            cmds.button(self.presetBtnR, e=True, bgc=[0.25,0.25,0.75], en=False)

    def loadPreset(self):
        self.presetLay = cmds.formLayout(p=self.layout)
        self.presetBtnReset = cmds.button(parent=self.presetLay, label="Reset", c=StretchNsquash.Callback(self.executeSsBtn), en=False)

        self.presetDropList = cmds.optionMenu( label='Presets : ', changeCommand=StretchNsquash.Callback(self.presetDropListUpdate), p=self.presetLay)
        cmds.menuItem( label='-', p=self.presetDropList )
        cmds.menuItem( label='Arm', p=self.presetDropList )
        cmds.menuItem( label='Leg', p=self.presetDropList )
        self.presetBtnL = cmds.button(parent=self.presetLay, w=20, label="L", c=StretchNsquash.Callback(self.presetSwitchSide, "L"), bgc=[0.75,0.25,0.25], en=False)
        self.presetBtnR = cmds.button(parent=self.presetLay, w=20, label="R", c=StretchNsquash.Callback(self.presetSwitchSide, "R"), bgc=[0,0,1], en=True)

        af = []
        ac = []
        ap = []
        af.append((self.presetBtnReset, "top", 3))
        af.append((self.presetBtnReset, "left", 3))
        af.append((self.presetBtnReset, "bottom", 3))

        af.append((self.presetDropList, "top", 3))
        ac.append((self.presetDropList, "left", 3,self.presetBtnReset))
        af.append((self.presetDropList, "bottom", 3))

        af.append((self.presetBtnR, "top", 3))
        ac.append((self.presetBtnR, "left", 3, self.presetDropList))
        af.append((self.presetBtnR, "bottom", 3))

        af.append((self.presetBtnL, "top", 3))
        ac.append((self.presetBtnL, "left", 0, self.presetBtnR))
        af.append((self.presetBtnL, "bottom", 3))

        cmds.formLayout(self.presetLay, e=True, ac=ac, af=af, ap=ap)

    @staticmethod
    def attach(main, childrens):
        ac = []
        af = []
        old = None
        for c in childrens:
            if old == None:
                af.append((c.layout, "top", 3))
            else:
                ac.append((c.layout, "top", 1, old.layout))
            af.append((c.layout, "left", 3))
            af.append((c.layout, "right", 3))
            old = c

        cmds.formLayout(main, e=True, ac=ac, af=af)

    def addFrameToArray(self, array, frame, type):
        array.append(frame)
        self.chainDisplayFrame[type] = frame

    def loadInput(self):
        self.inputLay = cmds.formLayout(p=self.layout, bgc=[0.2, 0.2, 0.2])
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "name", "le nom du membre", type="TEXT"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "WORLD", "ctrl qui doit avoir un attribut globalScale"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "temp chain start", callbackEvent=self.template))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "temp chain end", callbackEvent=self.template))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "template", "to be removed from template name", type="TEXT", callbackEvent=self.template))
        self.addFrameToArray(self.inputsLays, StretchNsquash.Frame(self, self.inputLay), "temp chain")
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "ctrl chain temp", callbackEvent=self.swapTemplate))
        self.addFrameToArray(self.inputsLays, StretchNsquash.Frame(self, self.inputLay), "ctrl chain")
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "dynamicPoint start", "transforme qui controle la position du debut de la chaine IK"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "dynamicPoint end", "transforme qui controle la position de la fin de la chaine IK"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "switch", "doit contenir un attribut boolean iktofk"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "end ik ctrl", "le controleur IK qui est en bout de chaine"))
        for i in self.inputsLays:
            i.setColor([0.86, 0.58, 0.34])
        StretchNsquash.attach(self.inputLay, self.inputsLays)

    def loadOutput(self):
        self.outputLay = cmds.formLayout(p=self.layout, bgc=[0.2, 0.2, 0.2])
        self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "controller attribut", "le controleur sur lequel les attributs de stretch and squash seront ajoutes"))
        self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "ik chain temp", callbackEvent=self.swapTemplate))
        self.addFrameToArray(self.outputsLays, StretchNsquash.Frame(self, self.outputLay), "ik chain")
        # self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "ik chain end", callbackEvent=self.fillChainElemDisplay))
        self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "sk chain temp", "la chaine qui skin", callbackEvent=self.swapTemplate))
        self.addFrameToArray(self.outputsLays, StretchNsquash.Frame(self, self.outputLay), "sk chain")
        # self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "ori chain temp", "les sk des joint Ori", callbackEvent=self.swapTemplate))
        # self.addFrameToArray(self.outputsLays, StretchNsquash.Frame(self, self.outputLay), "ori chain")
        # self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "0 chain temp", "les sk de joint 0", callbackEvent=self.swapTemplate))
        # self.addFrameToArray(self.outputsLays, StretchNsquash.Frame(self, self.outputLay), "0 chain")
        # self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "sk chain end", "le controleur sur lequel les attributs de stretch and squash seront ajoutes", callbackEvent=self.fillChainElemDisplay))
        
        # tmp.setValue(["j'aime les citron", "et puis les tartes aussi", "donc j'aime les tartes au citron"])

        for i in self.outputsLays:
            i.setColor([0.37, 0.68, 0.53])
        StretchNsquash.attach(self.outputLay, self.outputsLays)

    def loadWin(self):
        '''Load the UI in a window
        '''

        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=400, iw=600, retain=False, floating=True)
        self.layout = cmds.formLayout(p=self.win)
        
        self.loadPreset()
        self.loadInput()
        self.loadOutput()

        self.goBtn = cmds.button(parent=self.layout, label="Go!", c=StretchNsquash.Callback(self.executeSsBtn))

        af = []
        ac = []
        ap = []
        af.append((self.presetLay, "top", 3))
        af.append((self.presetLay, "left", 3))
        af.append((self.presetLay, "right", 3))

        af.append((self.goBtn, "bottom", 3))
        af.append((self.goBtn, "left", 3))
        af.append((self.goBtn, "right", 3))

        ac.append((self.inputLay, "top", 3, self.presetLay))
        af.append((self.inputLay, "left", 3))
        ap.append((self.inputLay, "right", 3, 50))
        ac.append((self.inputLay, "bottom", 3, self.goBtn))

        ac.append((self.outputLay, "top", 3, self.presetLay))
        ap.append((self.outputLay, "left", 3, 50))
        af.append((self.outputLay, "right", 3))
        ac.append((self.outputLay, "bottom", 3, self.goBtn))

        cmds.formLayout(self.layout, e=True, ac=ac, af=af, ap=ap)

def onMayaDroppedPythonFile(*args):
    '''Drag and drop function
    '''
    current_path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    sys.path.append(current_path)
    cmd = '''from ''' + __name__ + ''' import StretchNsquash;'''
    cmd += '''StretchNsquashWin = StretchNsquash();'''
    cmd += '''StretchNsquashWin.loadWin()'''
    mel.eval('''python("'''+ cmd + '''")''')
    # win = StretchNsquash()
    # win.start()

if __name__ == "__main__":
    win = StretchNsquash()
    win.loadWin()
