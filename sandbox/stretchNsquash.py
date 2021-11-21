#!/usr/bin/env python

"""stretchNsquash.py: Tools to create the stretch and squash"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.0.0"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
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
    StretchNsquash().loadWin()


class StretchNsquash(object):
    name = u"Stretch & Squash"

    #preset
    armPresets = [{"controlleur":"c_IK_hand", "WORLD":"c_WORLD"}]
    legPresets = [{"controlleur":"c_IK_foot", "WORLD":"c_WORLD"}]

    class Line(object):
        def __init__(self, parent, layout, name):
            self.name = name
            self.parentClass = parent
            self.parentLay = layout
            self.value = ""
            self.layout = None
            self.callback = parent.lineUpdate
            self.valueText = None
            self.load()

        def setValue(self, value):
            self.value = value
            if self.valueText == None:
                return
            cmds.text(self.valueText, e=True, label=self.value )


        def load(self):
            self.layout = cmds.formLayout(p=self.parentLay, bgc=[0.32, 0.32, 0.32])
            self.titleText = cmds.text(p=self.layout, label=" " + self.name.capitalize() + " : ", bgc=[0.32, 0.52, 0.65] )
            self.valueText = cmds.text(p=self.layout, label=self.value )
            self.setBtn = cmds.button(parent=self.layout, label="set", c=Callback(self.setBtnAct))
            cmds.formLayout(self.layout, e=True,
                            af=[(self.titleText, "left", 5), (self.titleText, "top", 5), (self.titleText, "bottom", 5),
                                (self.valueText, "top", 5), (self.valueText, "bottom", 5),
                                (self.setBtn, "top", 5), (self.setBtn, "right", 5), (self.setBtn, "bottom", 5)
                                ],
                            ac=[(self.valueText, "left", 5, self.titleText),(self.valueText, "right", 5, self.setBtn)]
            )

        def setBtnAct(self):
            sl = cmds.ls(sl=True)
            if len(sl) == 1:
                self.value = sl[0]
            cmds.text(self.valueText, e=True, label=self.value)
            self.callback(self.name, self.value)

    def __init__(self):
        self.win = None
        self.inputsLays = []
        self.outputsLays = []
        self.inputs = {}
        self.outputs = {}

        #presets
        self.presetSide = "L"

    def createCtrlAttributes(self):
        if not "Controler" in self.inputs:
            return
        c = self.inputs["Controler"]
        cmds.addAttr(c, longName='attrs', attributeType='enum', en=" ", k=True)
        cmds.addAttr(c, longName='stretch', defaultValue=0, minValue=0, maxValue=10, k=True)
        cmds.addAttr(c, longName='slide1', defaultValue=0, minValue=-10, maxValue=10, k=True)
        cmds.addAttr(c, longName='slide2', defaultValue=0, minValue=-10, maxValue=10, k=True)
        cmds.addAttr(c, longName='squash', defaultValue=0, minValue=0, maxValue=10, k=True)
        cmds.addAttr(c, longName='volume', defaultValue=0, minValue=-10, maxValue=10, k=True)

    def checkNecessariesInOut(self):
        necessariesInput = ["controlleur"]
        necessariesOutput = []
        necessaries = [[necessariesInput, self.inputs], [necessariesOutput, self.outputs]]

        for cat in necessaries:
            for n in cat[0]:
                if not n in cat[1]:
                    cmds.error("You must fill [" + n + "] attribute")

    def lineUpdate(self, name, value):
        print(name, value)

    def executeSS(self):
        '''Apply the stretch and squash
        '''
        self.checkNecessariesInOut()
        print("createNode", "mdl_distance" + self.inputs["IK 2nd art"])
        print("createNode", "mdl_distance" + self.inputs["IK 3rd art"])
        print("setAttr", "mdl_distance" + self.inputs["IK 2nd art"] + ".input1x", cmds.getAttr(self.inputs["IK 2nd art"] + ".ty"))
        print("setAttr", "mdl_distance" + self.inputs["IK 3rd art"] + ".input1x", cmds.getAttr(self.inputs["IK 3rd art"] + ".ty"))

        print("connectAttr", self.inputs["WORLD"] + ".globalScale", "mdl_distance" + self.inputs["IK 2nd art"] + ".input2x")
        print("connectAttr", self.inputs["WORLD"] + ".globalScale", "mdl_distance" + self.inputs["IK 3rd art"] + ".input2x")





    def executeSsBtn(self):
        '''Is executed when th UI button is pressed
        to load all value that are setted
        '''
        for i in self.inputsLays:
            if i.value == "":
                continue
            print(i.name, i.value)
            self.inputs[i.name] = i.value
        for o in self.outputsLays:
            if o.value == "":
                continue
            print(o.name, o.value)
            self.outputs[o.name] = o.value
        self.executeSS()

    @staticmethod
    def attach(main, childrens):
        ac = []
        af = []
        old = None
        for c in childrens:
            if old == None:
                af.append((c.layout, "top", 5))
            else:
                ac.append((c.layout, "top", 5, old.layout))
            af.append((c.layout, "left", 5))
            af.append((c.layout, "right", 5))
            old = c

        cmds.formLayout(main, e=True, ac=ac, af=af)

    def presetLoad(self, preset):
        pass

    def presetDropListUpdate(self, *item):
        print(item)
        print(self.presetDropList)
        if item == "Arm":
            self.pre

    def presetSwitchSide(self, side):
        self.presetSide = side
        if side == "L":
            cmds.button(self.presetBtnL, e=True, bgc=[0.75,0,0], en=False)
            cmds.button(self.presetBtnR, e=True, bgc=[0,0,1], en=True)
        elif side == "R":
            cmds.button(self.presetBtnL, e=True, bgc=[1,0,0], en=True)
            cmds.button(self.presetBtnR, e=True, bgc=[0,0,0.75], en=False)



    def loadPreset(self):
        self.presetLay = cmds.formLayout(p=self.layout)
        self.presetBtnReset = cmds.button(parent=self.presetLay, label="Reset", c=Callback(self.executeSsBtn))

        self.presetDropList = cmds.optionMenu( label='Presets : ', changeCommand=Callback(self.presetDropListUpdate).getCommandArgument(), p=self.presetLay)
        cmds.menuItem( label='-', p=self.presetDropList )
        cmds.menuItem( label='Arm', p=self.presetDropList )
        cmds.menuItem( label='Leg', p=self.presetDropList )
        self.presetBtnL = cmds.button(parent=self.presetLay, label="L", c=Callback(self.presetSwitchSide, "L"), bgc=[1,0,0], en=False)
        self.presetBtnR = cmds.button(parent=self.presetLay, label="R", c=Callback(self.presetSwitchSide, "R"), bgc=[0,0,1], en=True)

        af = []
        ac = []
        ap = []
        af.append((self.presetBtnReset, "top", 5))
        af.append((self.presetBtnReset, "left", 5))
        af.append((self.presetBtnReset, "bottom", 5))

        af.append((self.presetDropList, "top", 5))
        ac.append((self.presetDropList, "left", 5,self.presetBtnReset))
        af.append((self.presetDropList, "bottom", 5))

        af.append((self.presetBtnL, "top", 5))
        ac.append((self.presetBtnL, "left", 5, self.presetDropList))
        af.append((self.presetBtnL, "bottom", 5))

        af.append((self.presetBtnR, "top", 5))
        ac.append((self.presetBtnR, "left", 0, self.presetBtnL))
        af.append((self.presetBtnR, "bottom", 5))

        cmds.formLayout(self.presetLay, e=True, ac=ac, af=af, ap=ap)

    def loadInput(self):
        self.inputLay = cmds.formLayout(p=self.layout, bgc=[0.86, 0.58, 0.34])
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "controlleur"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "WORLD"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "IK 2nd art"))
        self.inputsLays.append(StretchNsquash.Line(self, self.inputLay, "IK 3rd art"))
        StretchNsquash.attach(self.inputLay, self.inputsLays)

    def loadOutput(self):
        self.outputLay = cmds.formLayout(p=self.layout, bgc=[0.37, 0.68, 0.53])
        self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "IK"))
        self.outputsLays.append(StretchNsquash.Line(self, self.outputLay, "SK"))
        StretchNsquash.attach(self.outputLay, self.outputsLays)

    def loadWin(self):
        '''Load the UI in a window
        '''

        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=150, retain=False, floating=True)
        self.layout = cmds.formLayout(p=self.win)
        
        self.loadPreset()
        self.loadInput()
        self.loadOutput()

        self.goBtn = cmds.button(parent=self.layout, label="Go!", c=Callback(self.executeSsBtn))

        af = []
        ac = []
        ap = []
        af.append((self.presetLay, "top", 5))
        af.append((self.presetLay, "left", 5))
        af.append((self.presetLay, "right", 5))

        af.append((self.goBtn, "bottom", 5))
        af.append((self.goBtn, "left", 5))
        af.append((self.goBtn, "right", 5))

        ac.append((self.inputLay, "top", 5, self.presetLay))
        af.append((self.inputLay, "left", 5))
        ap.append((self.inputLay, "right", 5, 50))
        ac.append((self.inputLay, "bottom", 5, self.goBtn))

        ac.append((self.outputLay, "top", 5, self.presetLay))
        ap.append((self.outputLay, "left", 5, 50))
        af.append((self.outputLay, "right", 5))
        ac.append((self.outputLay, "bottom", 5, self.goBtn))


        cmds.formLayout(self.layout, e=True, ac=ac, af=af, ap=ap)
