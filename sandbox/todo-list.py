#!/usr/bin/env python
# -- coding: utf-8 --

"""WipRollback.py: A little tool to help syncronise maya file for a CreativeSeeds pipeline"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "0.0.1"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
import ctypes
import datetime
try:
# pylint: disable=F0401
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

class Callback():
    def __init__(self, func, *args):
        '''Use for maya interface event, because it send you back your argument as strings
        func : the function you want to call
        *args : your arguments
        '''
        self.func = func
        self.args = args
    def __call__(self, *args):
        ag = self.args +  args
        self.func(*ag)


class ToDoList(object):
    __prefPath = os.path.expanduser('~/') + "maya/2020/prefs/cs"
    __prefName = "todo-list"
    @staticmethod
    def writePref(name, value):
        prefVars = {} 
        fPath = os.path.join(ToDoList.__prefPath, ToDoList.__prefName + ".pref")
        if not os.path.isdir(ToDoList.__prefPath):
            os.makedirs(ToDoList.__prefPath)
        if os.path.isfile(fPath):   
            with open(fPath, "r") as f:
                l = f.readline()
                while l:
                    try:
                        res = eval(l)
                        prefVars[res[0]] = res[1]
                    except:
                        pass
                    l = f.readline()
        prefVars[name] = value
        with open(fPath, "w+") as f:
            for key in prefVars:
                f.writelines(str([key, prefVars[key]]) + "\n")

    @staticmethod
    def readPref(name):
        fPath = os.path.join(ToDoList.__prefPath, ToDoList.__prefName + ".pref")
        if not os.path.isdir(ToDoList.__prefPath):
            return None
        if not os.path.isfile(fPath):
            return None
        prefVars = {}    
        with open(fPath, "r") as f:
            l = f.readline()
            try:
                while l:
                    res = eval(l)
                    prefVars[res[0]] = res[1]
                    if res[0] == name:
                        return(res[1])
                    l = f.readline()
            except:
                pass
        return None

    def __init__(self):
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)
        # self.savePaths = ToDoList.readPref("savePaths")

    class Note():
        drag = None

        def __init__(self, parent, name=None):

            self.name = name
            self.status = [] # sould give tuple (datetime, status_name)
            
            #relatives
            self.parent = None
            self.setParent(parent)
            self.children = []
            
            self.events = {}

            self.name_CTF = ""
            self.childrens_LC = ""
        
        # Parenting methodes
        def setParent(self, parent, pos=-1):
            oldParent = self.parent
            self.parent = parent
            
            if oldParent is not None and isinstance(oldParent, ToDoList.Note):
                oldParent._delChildren(self)
            if self.parent is not None and isinstance(self.parent, ToDoList.Note):
                self.parent._addChildren(self, pos)

        def _addChildren(self, child, pos=-1):
            if pos < 0:
                self.children.append(child)
            else:
                print(pos, child)
                self.children.insert(pos, child)
        def addChildren(self, child, pos=-1):
            child.setParent(self, pos)

        def _delChildren(self, child):
            self.children.remove(child)
        def delChildren(self, child):
            child.setParent(None)

        # events
        def eventHandler(self, e, c, *args):
            if not e in self.events:
                self.events[e] = []
            self.events[e].append((c, args))
            return self
        def runEvent(self, event, *args):
            if not event in self.events:
                return
            for c in self.events[event]:
                if c[0] is None:
                    continue
                a = c[1] + args
                c[0](*a)

        def open(self):
            if cmds.iconTextButton(self.open_CB, q=True, image1=True) == 'moveUVRight.png':
                cmds.iconTextButton(self.open_CB, e=True, image1='moveUVDown.png')
                cmds.columnLayout(self.childrens_LC, e=True, vis=True)
            elif cmds.iconTextButton(self.open_CB, q=True, image1=True) == 'moveUVDown.png':
                cmds.iconTextButton(self.open_CB, e=True, image1='moveUVRight.png')
                cmds.columnLayout(self.childrens_LC, e=True, vis=False)

        def setName(self, *arg):
            print(arg)
            newName = cmds.textField(self.name_CTF, q=True, text=True)
            if not newName:
                cmds.textField(self.name_CTF, e=True, text=self.name)
                return
            if self.name == None:
                self.name = newName
                # cmds.deleteUI(self.name_CTF)
                cmds.deleteUI(self.newNote_CB)
                self._loadNote()
                self.setStatus("created")
                self.runEvent("newNote")
            else:
                self.name = newName

        def _higlightStatus(self, status=None):
            for sb in self.statusButton.values():
                cmds.iconTextButton(sb, e=True, ebg=False)

            if status in self.statusButton.keys():
                cmds.iconTextButton(self.statusButton[status], e=True, ebg=True)

        def setStatus(self, status):
            if self.status:
                if status == self.status[-1][1]:
                    return self
            self.status.append((datetime.datetime.now(), status))
            self._higlightStatus(status)
            self.printStatus()
            return self

        def howManyParents(self):
            if isinstance(self.parent, ToDoList.Note):
                return self.parent.howManyParents() + 1
            return 0
        
        def isParentOf(self, child):
            child.isChildOf(self)

        def isChildOf(self, parent):
            if isinstance(self.parent, ToDoList.Note):
                if parent == self.parent:
                    return True
                return self.parent.isChildOf(parent)
            return False
            


        def _addEmptyNote(self):
            ToDoList.Note(self).load().eventHandler("newNote", self._addEmptyNote)

        def _loadNew(self):
            if not cmds.textField(self.name_CTF, exists=True):
                self.name_CTF = cmds.textField(p=self.layout, bgc=[0.2, 0.2, 0.2], cc=Callback(self.setName), w=1)
                
            tabulation = 15 * self.howManyParents()
            self.newNote_CB = cmds.iconTextButton(p=self.layout, image1='QR_add.png', c=Callback(self.setName))
            
            cmds.formLayout(self.layout, e=True, af=[(self.name_CTF, "top", 2), (self.name_CTF, "left", tabulation),
                                                     (self.newNote_CB, "top", 2), (self.newNote_CB, "right", 2)],
                                                 ac=[(self.name_CTF, "right", 2, self.newNote_CB)])

        def _loadNote(self):
            cmds.formLayout(self.layout, e=True, dgc=Callback(self._dragCb), dpc=Callback(self._dropCb))

            self.open_CB = cmds.iconTextButton(p=self.layout, image1='moveUVRight.png', c=Callback(self.open))
            if not cmds.textField(self.name_CTF, exists=True):
                self.name_CTF = cmds.textField(p=self.layout, text=self.name, ebg=False, bgc=[0.27, 0.27, 0.27], cc=Callback(self.setName), w=1)
            else:
                cmds.textField(self.name_CTF, e=True, text=self.name, ebg=False, bgc=[0.27, 0.27, 0.27], w=1)

            bi = {
                "WIP" : ('weightHammer.png', "WIP"),
                "Done" : ('confirm.png', ""),
                "Abort" : ('error.png', ""),
                "caution" : ('caution.png', ""),
                "help" : ('QR_help.png', ""),
                "delete" : ('QR_delete.png', "")
            }
            
            self.statusButton = {}
            for n in ["WIP", "Done", "Abort", "caution", "help"]:
                self.statusButton[n] = cmds.iconTextButton(p=self.layout, image1=bi[n][0], ann=bi[n][1], ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.setStatus, n))
            self.statusButton["delete"] = cmds.iconTextButton(p=self.layout,  image1='QR_delete.png',    ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.delete))

            # TODO change to dictionary
            self.statusButton = {}
            self.statusButton["WIP"] = cmds.iconTextButton(p=self.layout,     image1='weightHammer.png', ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.setStatus, "WIP"))
            self.statusButton["Done"] = cmds.iconTextButton(p=self.layout,    image1='confirm.png',      ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.setStatus, "Done"))
            self.statusButton["Abort"] = cmds.iconTextButton(p=self.layout,   image1='error.png',        ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.setStatus, "Abort"))
            self.statusButton["caution"] = cmds.iconTextButton(p=self.layout, image1='caution.png',      ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.setStatus, "caution"))
            self.statusButton["help"] = cmds.iconTextButton(p=self.layout,    image1='QR_help.png',      ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.setStatus, "help"))
            self.statusButton["delete"] = cmds.iconTextButton(p=self.layout,  image1='QR_delete.png',    ebg=False, bgc=[0.32, 0.52, 0.65], c=Callback(self.delete))

            tmp_sb_l = ["WIP", "Done", "Abort", "caution", "help", "delete"]

            if self.status:
                self._higlightStatus(self.status[-1][1])

            self._loadChildrens()

            tabulation = 15 * self.howManyParents()
            print(tabulation)
            ac = [(self.name_CTF, "right", 2, self.statusButton[tmp_sb_l[0]]), (self.name_CTF, "left", 2, self.open_CB)]
            af = [(self.open_CB, "top", 2), (self.open_CB, "left", tabulation), (self.name_CTF, "top", 2)]

            ac.append((self.childrens_LC, "top", 2, self.name_CTF))
            af.append((self.childrens_LC, "right", 0))
            af.append((self.childrens_LC, "left", 0))

            prev = self.statusButton[tmp_sb_l[-1]]
            af.append((prev, "right", 0))
            for sb in tmp_sb_l[-2::-1]:
                print(sb)
                af.append((self.statusButton[sb], "top", 2))
                ac.append((self.statusButton[sb], "right", 2, prev))
                prev = self.statusButton[sb]
            cmds.formLayout(self.layout, e=True, af=af, ac=ac)

        def _loadChildrens(self):
            
            if cmds.columnLayout(self.childrens_LC, exists=1):
                cmds.deleteUI(self.childrens_LC)
            self.childrens_LC = cmds.columnLayout(p=self.layout, adj=True, vis=False, w=1)
            for c in self.children:
                c.load()
            self._addEmptyNote()

        def printStatus(self):
            for s in self.status:
                print(s)

        def hideNew(self, v=True):
            if not self.name:
                cmds.formLayout(self.layout, e=True, vis=v)
            for c in self.children:
                c.hideNew(v)

        def moveFolder(self, newParent):
            pass

        def movePos(self, pos):
            pass

        def move(self, newparent, pos=-1):
            if newparent.isChildOf(self):
                print("{} is the child of {}".format(newparent.name, self.name))
                return
            if newparent.isParentOf(self):
                print("{} is the parent of {}".format(newparent.name, self.name))
                return
            if self == newparent:
                print("{} is himself".format(self.name))
                return
            print("{} and {} are not relatives".format(newparent.name, self.name))

            print(pos)
            self.setParent(newparent, pos)
            cmds.formLayout(self.layout, e=True, p=self.parent.childrens_LC)
            tabulation = 15 * self.howManyParents()
            cmds.formLayout(self.layout, e=True, af=[(self.open_CB, "left", tabulation)])

            # for c in self.parent.children:
            #     print(self.parent.layout, self.parent.name, self.parent, self)
            #     cmds.formLayout(c, e=True, p=self.parent.layout)
            # # self.parent._loadChildrens()

            tmp = cmds.formLayout(p=self.parent.layout)
            for c in self.parent.children:
                cmds.layout(c.layout, e=True, p=tmp)
            for c in self.parent.children:
                cmds.layout(c.layout, e=True, p=self.parent.childrens_LC)
            cmds.deleteUI(tmp)


            pass

        def delete(self):
            self.setParent(None)
            if cmds.formLayout(self.layout, exists=1):
                cmds.deleteUI(self.layout)

        def _dragCb(self, dragControl, x, y, modifiers):
            ToDoList.Note.drag = self
            
            cmds.formLayout(self.layout, e=True, bgc=[0.32, 0.52, 0.65])
            cmds.formLayout(self.layout, e=True, ebg=True)
        def _dropCb(self, dragControl, dropControl, messages, x, y, dragType):
            cmds.formLayout(ToDoList.Note.drag.layout, e=True, bgc=[0, 0, 0])
            cmds.formLayout(ToDoList.Note.drag.layout, e=True, ebg=False)
            print(x, y)
            if x < self.howManyParents() * 15 + 5:
                print(self.parent.children.index(self))
                ToDoList.Note.drag.move(self.parent, self.parent.children.index(self))
                print("move to parent")
            else:
                ToDoList.Note.drag.move(self)
                print("move to him")
            ToDoList.Note.drag = None


        def load(self):
            if isinstance(self.parent, ToDoList.Note):
                self.layout = cmds.formLayout(p=self.parent.childrens_LC, w=1)
            else:
                self.layout = cmds.formLayout(p=self.parent, w=1)

            if self.name == None:
                self._loadNew()
            else:
                self._loadNote()
            return self


    def switch_button(self):
        if cmds.iconTextButton(self.switch, q=True, image1=True) == 'switchOn.png':
            cmds.iconTextButton(self.switch, e=True, image1='switchOff.png')
            self.topNote.hideNew(False)
        elif cmds.iconTextButton(self.switch, q=True, image1=True) == 'switchOff.png':
            cmds.iconTextButton(self.switch, e=True, image1='switchOn.png')
            self.topNote.hideNew(True)


    def saveNote(self):
        self.topNote.printStatus()
        # ToDoList.writePref()

    def load(self):

        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)

        # cmds.iconTextButton(p=self.win, image1='error.png')
        # cmds.iconTextButton(p=self.win, image1='confirm.png')
        # cmds.iconTextButton(p=self.win, image1='caution.png')
        # cmds.iconTextButton(p=self.win, image1='SP_DirIcon.png')
        # cmds.iconTextButton(p=self.win, image1='SP_FileIcon.png')
        # cmds.iconTextButton(p=self.win, image1='polyPasteUV.png')
        # cmds.iconTextButton(p=self.win, image1='teDownArrow.png')
        # cmds.iconTextButton(p=self.win, image1='teRightArrow.png')

        # cmds.iconTextButton(p=self.win, image1='SP_MessageBoxQuestion.png')
        # cmds.iconTextButton(p=self.win, image1='QR_help.png')
        # cmds.iconTextButton(p=self.win, image1='SP_TrashIcon.png')
        # cmds.iconTextButton(p=self.win, image1='QR_delete.png')
        # cmds.iconTextButton(p=self.win, image1='weightHammer.png')
        # cmds.iconTextButton(p=self.win, image1='QR_add.png')
        # cmds.iconTextButton(p=self.win, image1='SP_FileDialogStart.png')
        # cmds.iconTextButton(p=self.win, image1='out_time.png')
        # cmds.iconTextButton(p=self.win, image1='rvPauseIprTuning.png')


        cmds.scriptJob(ro=True, uid=[self.win, Callback(self.saveNote)])

        self.column_LC = cmds.columnLayout(p=self.win, adj=True)
        self.topNote = ToDoList.Note(self.column_LC, name="Macaru")
        ToDoList.Note(self.topNote, name="Skin")
        ToDoList.Note(self.topNote, name="leg")
        ToDoList.Note(self.topNote, name="arm")
        ToDoList.Note(self.topNote, name="head")
        ToDoList.Note(self.topNote, name="jaw")
        self.topNote.load()

        self.switch = cmds.iconTextButton(p=self.win, image1='switchOn.png', c=Callback(self.switch_button))

if __name__ == "__main__":
    if sys.executable.endswith(u"bin\maya.exe"):
        ToDoList().load()
    else:
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport".format(__version__), "{} info".format(__file__), 0)


def onMayaDroppedPythonFile(*_):
    '''Just to get rid of the anoying warning message of maya
    '''
    ToDoList().load()