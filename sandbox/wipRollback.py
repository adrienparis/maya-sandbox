#!/usr/bin/env python
# -- coding: utf-8 --


"""WipRollback.py: A little tool to help syncronise maya file for a CreativeSeeds pipeline"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "0.2.1"
__copyright__   = "Copyright 2021, Creative Seeds"


import os
import ctypes
try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

if __name__ == "__main__":
    ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport".format(__version__), "{} info".format(__file__), 0)

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

def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    window = WipRollback()
    window.load()

class WipRollback():

    class Tile():

        def __init__(self, parent, name, path):
            self.file = name
            self.path = path
            self.topLayout = cmds.formLayout(p=parent)
            self.layout = cmds.formLayout(p=self.topLayout, bgc=[0.5,0.5,0.5])
            cmds.formLayout(self.topLayout, e=True, af=[(self.layout, "top", 1), (self.layout, "bottom", 1), (self.layout, "left", 1), (self.layout, "right", 1)])
            
            i_p = os.path.join(path, "images", name[:-3] + ".jpg")
            if not os.path.exists(i_p):
                i_p = "cube"
            self.iconTextBtn = cmds.iconTextButton(parent=self.layout, image1=i_p, h=80, w=80, c=Callback(self.OpenUp))
            self.title = cmds.text(parent=self.layout, label=name.split('_')[-1][:-3])
            cmds.formLayout(self.layout, e=True, af=[(self.iconTextBtn, "top", 0), (self.iconTextBtn, "left", 0), (self.iconTextBtn, "right", 0),
                                                    (self.title, "left", 0), (self.title, "right", 0), (self.title, "bottom", 0)],
                                                ac=[(self.title, "top", 5, self.iconTextBtn)])
        
        def SaveCurrent(self):
            pass
            mel.eval("incrementAndSaveScene 1;")

        def OpenUp(self):
            cmds.file(self.wipRollback, o=True, f=True)
            print(self.file)
        
        def SaveFront(self):
            pass
            cmds.file(rename=pubPath)
            cmds.file(save=True, type='mayaAscii')
            self.OpenUp()
            mel.eval("incrementAndSaveScene 1;")

    def __init__(self):
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)
        self.scriptJobIndex = []
        self.win = None
        self.tiles = []
        
        self.fileUpdate()

    def resizeTilesView(self):
        '''Re-ajust rows and columns from grids, if the windows is resized
        '''
        h = cmds.scrollLayout(self.scrLay, q=True, h=True)
        w = cmds.scrollLayout(self.scrLay, q=True, w=True)
        size = int((w - 4) / 120)
        if size == 0:
            return

        nbChild = cmds.gridLayout(self.grdLay, q=True, nch=True )
        rows = max((nbChild - 1) / size + 1, 1)
        if h < rows * 120:
            size = int((w) / 120)
            if size == 0:
                return

            nbChild = cmds.gridLayout(self.grdLay, q=True, nch=True )
            rows = max((nbChild - 1) / size + 1, 1)

        cmds.gridLayout(self.grdLay, e=True, numberOfColumns=size )
        cmds.gridLayout(self.grdLay, e=True, numberOfRows= rows )

    # Jobs
    def loadJobs(self):
        '''Load all jobs
        '''
        self.scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.openingSceneJob)]))
        self.scriptJobIndex.append(cmds.scriptJob(event=["SceneSaved", Callback(self.savingSceneJob)]))

    def killJobs(self):
        '''Kill all jobs
        '''
        for i in self.scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)

    def openingSceneJob(self):
        self.fileUpdate()
        self.loadTiles()

    def savingSceneJob(self):
        self.fileUpdate()
        self.takeScreenShot()
        self.loadTiles()

    def fileUpdate(self):
        self.filepath = os.path.abspath(cmds.file(q=True, sn=True))
        self.dirpath = os.path.dirname(self.filepath)
        self.image_name = os.path.split(self.filepath)[-1][:-3]

    def takeScreenShot(self, width=480, height=270):
        print(self.dirpath, "images", self.image_name + ".jpg")
        if not os.path.exists(os.path.join(self.dirpath, "images")):
            os.makedirs(os.path.join(self.dirpath, "images"))
        img_path = os.path.join(self.dirpath, "images", self.image_name + ".jpg")
        print("\nscreenshot taken :\n\t {}".format(img_path))
        cmds.playblast(fr=0, v=False, fmt="image", c="jpg", orn=False, cf=img_path, wh=[width,height], p=100)

    def loadTiles(self):
        self.unloadTiles()

        ls = os.listdir(self.dirpath)
        ls = [x for x in ls if x.endswith(".ma")]
        ls.reverse()
        for maya_file in ls[:60]:
            self.tiles.append(WipRollback.Tile(self.grdLay, maya_file, self.dirpath))
        cmds.scrollLayout(self.scrLay, e=True, rc=Callback(self.resizeTilesView))
    
    def unloadTiles(self):
        t = [x.topLayout for x in self.tiles]
        if not t:
            return
        cmds.deleteUI(t)
        for i in self.tiles:
            del i
        self.tiles = []

    def load(self):

        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)

        # Call self.killJobs if the windows is killed
        cmds.scriptJob(ro=True, uid=[self.win, Callback(self.killJobs)])
        self.loadJobs()

        # Creating the grid
        self.scrLay = cmds.scrollLayout(parent=self.win,
                                    horizontalScrollBarThickness=160,
                                    verticalScrollBarThickness=16,
                                    cr=True, rc=Callback(self.resizeTilesView))
        self.grdLay = cmds.gridLayout(p=self.scrLay, numberOfColumns=3, cr=False, ag=True, cellWidthHeight=(120, 120))

        self.loadTiles()
