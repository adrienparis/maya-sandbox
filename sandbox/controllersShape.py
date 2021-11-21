#!/usr/bin/env python
# -- coding: utf-8 --

"""controllersShape.py: Tools to create CTRL shapes."""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "0.0.1-alpha"
__copyright__   = "Copyright 2021, Creative Seeds"

import ctypes
import sys
import math
import inspect

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
            import __main__
            __main__.cb_repeatLast = self
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast(cb_repeatLast=True)"); ''')
        return self.func(*ag, **self.kwargs)

class Module(object):
    BLUE = [0.32, 0.52, 0.65]
    TURQUOISE = [0.28, 0.66, 0.70]
    ORANGE = [0.86, 0.58, 0.34]

    increment = 0
    drag = None

    def __init__(self, parent, name=None):
        
        if name is None:
            name = self.__class__.__name__ + str(Module.increment)
            Module.increment += 1
        self.name = name
        self.childrens = []
        self.setParent(parent)
        self._scriptJobIndex = []
        self.childrenLayout = None
        self.layout = None
        self.bgc = None
        self.dragged = False
        self.af = []
        self.ac = []
        self.ap = []

    def __repr__(self):
        return str(self.childrenLayout)

    def __getattribute__(self, name):
        if name == "height":
            return cmds.layout(self.layout, q=True, h=True)
        if name == "width":
            return cmds.layout(self.layout, q=True, w=True)
        return object.__getattribute__(self, name)

    def setParent(self, parent):
        self.parent = parent
        if isinstance(self.parent, Module):
            self.parent.childrens.append(self)

    def attach(self, elem, top=None, bottom=None, left=None, right=None, margin=(0,0,0,0)):
        '''attach "FORM": string
                    elem : layout/control
                    pos : float
                    None
        '''
        for s, n, m in [(top, "top", margin[0]), (bottom, "bottom", margin[1]), (left, "left", margin[2]), (right, "right", margin[3])]: 
            if s == None:
                continue
            if isinstance(s, (str, unicode)):
                if s == "FORM":
                    self.af.append((elem, n, m))
                else:
                    self.ac.append((elem, n, m, s))
            if isinstance(s, (float, int)):
                self.ap.append((elem, n, m, float(s)))
        return elem

    def resetAttach(self):
        self.af = []
        self.ac = []
        self.ap = []
    
    def applyAttach(self, layout):
        cmds.formLayout(layout, e=True, af=self.af, ac=self.ac, ap=self.ap)

    def load(self):
        raise Exception('load function not implemented')

    def reload(self):
        self.unload()
        self.load()

    def unload(self):
        if self.layout == None:
            return self
        cmds.deleteUI(self.layout)
        return self

    def refresh(self):
        pass

    def move(self, other):
        parent = self.parent
        pos = parent.childrens.index(other)
        parent.childrens.remove(self)
        parent.childrens.insert(pos, self)
        parent.refresh()
        # tmp = cmds.formLayout(p=parent.layout)
        # for c in parent.childrens:
        #     cmds.layout(c.layout, e=True, p=tmp)
        # for c in parent.childrens:
        #     cmds.layout(c.layout, e=True, p=parent.childrenLayout)
        #     # c.reload()
        # cmds.deleteUI(tmp)

    # Jobs
    def _loadJobs(self):
        '''Load all jobs
        '''
        # Example : 
        # self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))
        raise Exception('_loadJobs function not implemented')

    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)
        self._scriptJobIndex = []

    def _dragCb(self, dragControl, x, y, modifiers):
        Module.drag = self
        
        if not self.dragged:
            self.bgc = cmds.layout(self.layout, q=True, bgc=True)
            self.ebg = cmds.layout(self.layout, q=True, ebg=True)
        self.dragged = True
        cmds.layout(self.layout, e=True, ebg=True)
        cmds.layout(self.layout, e=True, bgc=Module.BLUE)

    def _dropCb(self, dragControl, dropControl, messages, x, y, dragType):
        cmds.layout(Module.drag.layout, e=True, bgc=Module.drag.bgc)
        cmds.layout(Module.drag.layout, e=True, ebg=Module.drag.ebg)
        Module.drag.dragged = False
        Module.drag.move(self)
        Module.drag = None

class slider(Module):
    switchColor = False
    def __init__(self, parent, name=None, attr=None, defaultValue=1.0, minMax=None, changeFunc=None, type_=float):
        Module.__init__(self, parent, name=name)
        self.attr = attr
        self.step = 1.0
        self.max = self.step * 2
        self.changeFunc = changeFunc
        self.minMax = minMax
        self.defaultValue = defaultValue
        self.type = type_
        self._cmdsSlider = cmds.floatSlider if self.type == float else cmds.intSlider
        self._cmdsInputField = cmds.floatField if self.type == float else cmds.intField

    def sliderChangeEvent(self):
        v = self._cmdsSlider(self.slider, q=True, v=True)
        self._cmdsInputField(self.field, e=True, v=v)
        if self.changeFunc != None:
            self.changeFunc(self.attr, v)

    def inputFieldChangeEvent(self, diff=None):
        v = self._cmdsInputField(self.field, q=True, v=True)
        minV = self._cmdsSlider(self.slider, q=True, min=True)
        maxV = self._cmdsSlider(self.slider, q=True, max=True)
        gap = maxV - minV
        if diff is not None:
            if diff == "add":
                v = self.type(v + gap * 0.1)
            if diff == "sub":
                v = self.type(v - gap * 0.1)
        self._cmdsInputField(self.field, e=True, v=v)
        if self.changeFunc != None:
            self.changeFunc(self.attr, v)
        if minV <= v and v <= maxV:
            self._cmdsSlider(self.slider, e=True, v=v)

    def load(self):
        w, h = 20, 20
        bgc = [0.2, 0.2, 0.2,] if slider.switchColor else [0.25, 0.25, 0.25]
        slider.switchColor = not slider.switchColor
        self.layout = cmds.formLayout(p=self.parent, w=5, h=40, bgc=bgc)
        self.title = self.attach(cmds.text(l=self.name, p=self.layout), top="FORM", left="FORM", margin=(2, 2, 2, 2))
        self.btn_add = self.attach(cmds.iconTextButton(p=self.layout,
                                                       style='iconOnly',
                                                       ann="add", w=w, h=h,
                                                       image1="moveUVRight.png",
                                                       c=Callback(self.inputFieldChangeEvent, "add")),
                                   top="FORM", right="FORM", margin=(2, 2, 2, 2))
        self.field = self.attach(self._cmdsInputField(p=self.layout, 
                                                      w=60,
                                                      v=self.type(self.defaultValue),
                                                      ec=Callback(self.inputFieldChangeEvent)),
                                top="FORM", right=self.btn_add, margin=(2, 2, 2, 2))
        if self.type is float:
            self._cmdsInputField(self.field, e=True, pre=1)
        self.btn_sub = self.attach(cmds.iconTextButton(p=self.layout,
                                                       style='iconOnly',
                                                       ann="sub", w=w, h=h,
                                                       image1="moveUVLeft.png",
                                                       c=Callback(self.inputFieldChangeEvent, "sub")),
                                   top="FORM", right=self.field, margin=(2, 2, 2, 2))

        if self.minMax is None:
            self.slider = self.attach(self._cmdsSlider(p=self.layout, v=self.type(self.defaultValue), dc=Callback(self.sliderChangeEvent)), top=self.field, left="FORM", right="FORM", margin=(2, 2, 20, 2))
        else:
            self.slider = self.attach(self._cmdsSlider(p=self.layout, v=self.type(self.defaultValue), min=self.type(self.minMax[0]), max=self.type(self.minMax[1]), dc=Callback(self.sliderChangeEvent)), top=self.field, left="FORM", right="FORM", margin=(2, 2, 20, 2))

        self.applyAttach(self.layout)

class module_controlerShape(Module):
    class Shape(object):
        size = 10.0

        def __init__(self, joint=None):
            object.__init__(self)
            self.created = False
            self.joint = joint
            self.object = None
            self.name = "name" if self.joint is None else joint.replace("sk_", "FK_")
            self.ctrlName = "c_" + self.name
            self.create()
            attributes = inspect.getmembers(self.__class__, lambda a:not(inspect.isroutine(a)))
            self.attributes = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
            self.attributesName = [a[0] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
            self.created = True
            if self.object is None:
                raise Exception('The create function  must set the value of self.object')
            self.grp_pose = cmds.group(self.object, n="pose_" + self.name)
            self.grp_inf = cmds.group(self.grp_pose, n="inf_" + self.name)
            self.grp_root = cmds.group(self.grp_inf, n="root_" + self.name)
            if self.joint is not None:
                toDelete = cmds.parentConstraint(self.joint, self.grp_root)
                cmds.delete(toDelete)
            self.shape = cmds.listRelatives(self.object)
            h = cmds.listConnections(self.shape, s=True)
            self.history = h[0] if h is not None else None
            self.refresh()

        def create(self):
            raise Exception('create function not implemented')

        def connectParentCtrl(self):
            parJoint = cmds.listRelatives(self.joint, p=True, type="joint")
            if parJoint is None:
                return
            ctrl = cmds.parentConstraint(self.joint, q=True, tl=True)
            parCtrl = cmds.parentConstraint(parJoint, q=True, tl=True)
            if parCtrl is None:
                return
            par = cmds.listRelatives(ctrl, p=True)
            inf = None
            for _ in range(0, 50):
                if par == None:
                    break
                if par[0].startswith("inf_"):
                    inf = par
                    break
                par = cmds.listRelatives(par, p=True)
            if cmds.parentConstraint(inf, q=True, tl=True) != parCtrl:
                cmds.parentConstraint(parCtrl, inf, mo=True)
            
        def connectChildCtrl(self):
            ctrl = cmds.parentConstraint(self.joint, q=True, tl=True)
            childJoint = cmds.listRelatives(self.joint, c=True, type="joint")
            if childJoint is None:
                return
            for c in childJoint:
                childCtrl = cmds.parentConstraint(c, q=True, tl=True)
                if childCtrl is None:
                    continue
                childPar = cmds.listRelatives(childCtrl, p=True)
                infChild = None
                for _ in range(0, 50):
                    if childPar == None:
                        break
                    if childPar[0].startswith("inf_"):
                        infChild = childPar
                        break
                    childPar = cmds.listRelatives(childPar, p=True)
                if cmds.parentConstraint(infChild, q=True, tl=True) != ctrl:
                    cmds.parentConstraint(ctrl, infChild, mo=True)

        def apply(self):
            cmds.delete(self.object, constructionHistory = True)
            cmds.makeIdentity(self.object, apply=True, t=True, r=True, s=True)
            if self.joint is not None:
                cmds.parentConstraint(self.object, self.joint, mo=True)
                # cmds.scaleConstraint(self.object, self.joint, mo=True)
                self.connectChildCtrl()
                self.connectParentCtrl()

        def refresh(self):
            if not self.created:
                return
            cmds.undoInfo( swf=False)
            
            for attr in self.attributes:
                updateFunc = "update_" + attr[0]
                if hasattr(self, updateFunc) and callable(getattr(self, updateFunc)):
                    object.__getattribute__(self, updateFunc)(attr[1])
            cmds.undoInfo( swf=True)

        @classmethod
        def getListAttr(cls, *args):
            '''return a dict
            {"name of the attribut" : ["pretty name", type, value, "name of the attr that must be above", [min, max]]}
            '''
            if len(args) >= 1:
                if issubclass(args[0], cls):
                    cls = args[0]
            
            attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
            l = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
            l = {a[0] : [a[0].capitalize(), type(a[1]), a[1], None, None] for a in l}
            return l

        def __setattr__(self, name, value):
            object.__setattr__(self, name, value)
            vars()[name] = value
            # setattr(self.__class__, name, value)
            if self.created:
                if name not in self.attributesName:
                    return
                updateFunc = "update_" + name
                if hasattr(self, updateFunc) and callable(getattr(self, updateFunc)):
                    cmds.undoInfo( swf=False)
                    object.__getattribute__(self, updateFunc)(value)
                    cmds.undoInfo( swf=True)
                else:
                    cmds.warning("the function {} is not implemented".format(updateFunc))
        
        def update_size(self, value):
            if self.joint is not None:
                value = value * cmds.getAttr(self.joint + ".radius")
            cmds.setAttr(self.object + ".sx", value * 0.1)
            cmds.setAttr(self.object + ".sy", value * 0.1)
            cmds.setAttr(self.object + ".sz", value * 0.1)

    class ShapeCircle(Shape):
        sweep = 360.0
        sweepOffset = 0.0

        def create(self):
            self.object = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=self.__class__.sweep, r=self.__class__.size * 0.1,
                                      d=3, ut=0, tol=0.01, s=8, ch=1, n=self.ctrlName)[0]

        def update_sweep(self, value):
            cmds.setAttr(self.history + ".sweep", value)

        @classmethod
        def getListAttr(cls):
            attrs = module_controlerShape.Shape.getListAttr(cls)

            attrs["sweepOffset"][0] = "Sweep offset"

            attrs["sweepOffset"][3] = "sweep"
            
            attrs["sweep"][4] = [0, 360]
            attrs["sweepOffset"][4] = [0, 360]

            return attrs

    class ShapeStar(Shape):
        sweep = 360.0
        sweepOffset = 0.0
        hardness = 60.0
        section = 4
        def create(self):
            self.object = cmds.circle(c=[0, 0, 0], nr=[0, 1, 0], sw=self.__class__.sweep, r=self.__class__.size,
                                      d=3, ut=0, tol=0.01, s=self.__class__.section * 2, ch=1, n=self.ctrlName)[0]

        @classmethod
        def getListAttr(cls):
            attrs = module_controlerShape.Shape.getListAttr(cls)

            attrs["section"][0] = "Number of point"
            attrs["hardness"][0] = "Hardness %"

            attrs["sweepOffset"][3] = "sweep"
            attrs["hardness"][3] = "section"
            
            attrs["sweep"][4] = [0, 360]
            attrs["section"][4] = [3, 16]

            return attrs

        def update_hardness(self, value):
            vtx = ["{}.cv[{}]".format(self.object, x) for x in range(0, self.section * 2)]
            segment = self.sweep / float(self.section * 2)
            for i in range(0, self.section * 2):
                r = (segment * i * 2 * math.pi) / float(self.sweep)
                s = 1 if  i % 2 == 0 else 1 - value * 0.01
                cmds.xform(vtx[i], a=True, os=True, translation=(math.cos(r) * s, 0, math.sin(r) * s))

        def update_section(self, value):
            cmds.setAttr(self.history + ".sections", value * 2)
            self.hardness = self.hardness

        def update_sweep(self, value):
            cmds.setAttr(self.history + ".sweep", value)

    class ShapeCross(Shape):
        width = 20.0

        def create(self):
            close = 0.2
            far = 1.0
            
            pointPos = []
            for i in range(0, 13):
                i = i % 12
                j = (i + 2) % 12
                x = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))
                i = (i + 3) % 12
                j = (j + 3) % 12
                y = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))
                pointPos.append((x, 0, y))
            self.object = cmds.curve(d=1, p=pointPos, k=range(0, 13))

        @classmethod
        def getListAttr(cls):
            attrs = module_controlerShape.Shape.getListAttr(cls)

            attrs["width"][0] = "Width %"

            attrs["width"][4] = [0, 100]
            return attrs

        def update_width(self, value):
            close = value * 0.01
            far = 1.0

            for i in range(0, 13):
                cv = "{}.cv[{}]".format(self.object, i)
                i = i % 12
                j = (i + 2) % 12
                x = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))

                i = (i + 3) % 12
                j = (j + 3) % 12
                y = (i / 6 * -2 + 1) * (close + ((j % 6) / 4  + (j % 6) / 6) * (far - close))
                cmds.xform(cv, a=True, os=True, translation=(x, 0, y))

    class ShapeArrow(Shape):
        width = 50.0
        pointiness = 1.0
        def create(self):
            pointPos = [
                        (0, 0, 1),
                        (4, 0, 1),
                        (4, 0, 2),
                        (8, 0, 0),
                        ]
            pointPos = pointPos + [(x[0], x[1], x[2] * -1) for x in pointPos[::-1]] + [pointPos[0]]
            self.object = cmds.curve(d=1, p=pointPos, k=range(0, len(pointPos)), os=True)


    class ShapeDart(Shape):
        width = 50.0
        pointiness = 1.0
        def create(self):
            pointPos = [
                        (-2, 0, 0),
                        (0, 0, 4),
                        (0, 0, 4),
                        (2, 0, 4),
                        (0, 0, 0),
                        ]
            pointPos = pointPos + [(x[0], x[1], x[2] * -1) for x in pointPos[::-1]] + [pointPos[0]]
            self.object = cmds.curve(d=1, p=pointPos, k=range(0, len(pointPos)), os=True)

    class ShapePin(Shape):
        width = 50.0
        pointiness = 1.0
        def create(self):
            pointPos = [
                        (0, 0, 0),
                        (0, 0, 2),
                        (-1, 0, 3),
                        (0, 0, 4),
                        (1, 0, 3),
                        (0, 0, 2),
                        ]
            self.object = cmds.curve(d=1, p=pointPos, k=range(0, len(pointPos)), os=True)
    
    class ShapeText(Shape):
        pass
    def __init__(self, parent, name=None):
        Module.__init__(self, parent, name=name)
        self.winName = "Controller Adjustement"

    def _loadJobs(self):
        self._scriptJobIndex.append(cmds.scriptJob(event=["SelectionChanged", Callback(self.selectionChangeEvent)]))

    def selectionChangeEvent(self):
        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            self.closeWin()
        
    def closeWin(self):
        if cmds.workspaceControl(self.winName, exists=True):
            cmds.deleteUI(self.winName)
        for s in self.shapes:
            s.apply()
        cmds.undoInfo(cck=True)
        
    def update(self, name, value):
        for s in self.shapes:
            setattr(s, name, value)

    def window(self, shapeType):
        cmds.undoInfo(ock=True)

        self.winName 
        if cmds.workspaceControl(self.winName, exists=True):
            cmds.deleteUI(self.winName)
        self.win = cmds.workspaceControl(self.winName)

        cmds.scriptJob(ro=True, uid=[self.win, Callback(self._killJobs)])   
        self._loadJobs()

        cLay = cmds.columnLayout(p=self.win, w=200, adj=True)
        for k, v in shapeType.getListAttr().items():
            slider(cLay, name=v[0], attr=k, changeFunc=self.update, type_=v[1], defaultValue=v[2], minMax=v[4]).load()
        cmds.showWindow(self.win)

    def createShape(self, shape):
        name = "c_plop"
        sel = cmds.ls(sl=True)
        sel = [x for x in sel if cmds.objectType(x) == "joint" and cmds.getAttr(x + ".v")]
        if len(sel) <= 0:
            #TODO ask for name and create ctrl in center of the world
            return
        self.shapes = []
        shapeClass = module_controlerShape.Shape
        if shape[0] == "circle":
            shapeClass = module_controlerShape.ShapeCircle
        if shape[0] == "star":
            shapeClass = module_controlerShape.ShapeStar
        if shape[0] == "cross":
            shapeClass = module_controlerShape.ShapeCross
        if shape[0] == "arrow":
            shapeClass = module_controlerShape.ShapeArrow
        if shape[0] == "dart":
            shapeClass = module_controlerShape.ShapeDart
        if shape[0] == "pin":
            shapeClass = module_controlerShape.ShapePin

        for s in sel:
            self.shapes.append(shapeClass(s))

        cmds.select([x.object for x in self.shapes])
        self.window(type(self.shapes[0]))

    def load(self):
        self.layout = cmds.formLayout(p=self.parent, w=5, bgc=[0.25, 0.25, 0.25], en=True)
        h, w = 30, 30
        shapeButton = [["circle", "circle.png"],
                        ["star", "polyUltraShape.png"],
                        ["cross", "QR_add.png"],
                        ["arrow", "SP_FileDialogForward_Disabled.png"],
                        ["dart", "nodeGrapherNext.png"],
                        ["pin", "pinItem.png"],
                        ["text", "text.png"]]
                        
        lastSb = "FORM"
        for sb in shapeButton:
            annotation = "| simple clic:\tCreate a {} shape on world center\n| double clic:\tCreate a FK ctrl with a {} shape along selected joint".format(sb[0], sb[0])
            lastSb = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann=annotation, w=w, h=h, image1=sb[1], c=Callback(self.createShape, sb)), top="FORM", left=lastSb)
        lastSb = self.attach(cmds.iconTextButton(parent=self.layout, style='iconOnly', ann="Open Library", w=w, h=h, image1="Objects.png", en=False), top="FORM", right="FORM")

        self.applyAttach(self.layout)
        return self


class ControllerShape():
    def __init__(self):
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)

    def load(self):
        '''loading The window
        '''
        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=50, iw=250, retain=False, floating=True, h=50, w=250)
        
        module_controlerShape(self.win).load()

        return self

if __name__ == "__main__":
    if sys.executable.endswith(u"bin\maya.exe"):
        ControllerShape().load()
    else:
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)

def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    ControllerShape().load()

