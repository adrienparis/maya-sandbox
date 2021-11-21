#!/usr/bin/env python
# -- coding: utf-8 --


"""publisher.py: A little tool to help syncronise maya file for a CreativeSeeds pipeline"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "2.4.0-alpha"
__copyright__   = "Copyright 2021, Creative Seeds"


import os
import sys
import subprocess
import getpass
from datetime import datetime
import re
import shutil
import ctypes
try:
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


if __name__ == "__main__":
    ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport".format(__version__), "Publisher info", 0)


def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    window = Publisher()
    window.load()

class Publisher(object):
    BLUE = [0.32, 0.52, 0.65]
    TURQUOISE = [0.28, 0.66, 0.70]
    ORANGE = [0.86, 0.58, 0.34]
    DARKGREY = [0.21, 0.21, 0.21]
    GREY = [0.26, 0.26, 0.26]
    LIGHTGREY = [0.36, 0.36, 0.36]

    COLOR_SAVE = [0.32, 0.52, 0.65]
    COLOR_LOCAL = [0.28, 0.66, 0.70]
    COLOR_RELATIVE = [0.86, 0.58, 0.34]
    COLOR_SEC_BGC = [0.21, 0.21, 0.21]
    COLOR_MAIN_BGC = [0.26, 0.26, 0.26]
    COLOR_BUTTON = [0.36, 0.36, 0.36]

    class PathLine():
        def __init__(self, parent):
            self.parent = parent
            self.color = Publisher.BLUE
            self.path = ""
            self.textButton = None
            self.pathVisibility = True
            self.func = None
            self.load()
        
        def __setattr__(self, name, value):
            self.__dict__[name] = value
            if "field" in self.__dict__:
                if name == "path":
                    cmds.scrollField(self.field, e=True, text=self.path)
                if name == "color":
                    cmds.scrollField(self.field, e=True, bgc=self.color)
                if name == "pathVisibility":
                    cmds.scrollField(self.field, e=True, vis=self.pathVisibility)
            if "button" in self.__dict__:
                if name == "textButton":
                    if not self.textButton == None:
                        cmds.button(self.button, e=True, label=self.textButton)
                    else:
                        cmds.button(self.button, e=True, label=self.textButton, vis=False)
                if name == "func":
                    cmds.button(self.button, e=True, c=self.func)

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent, h=39)
            self.field = cmds.scrollField(parent=self.layout, editable=False, h=35, wordWrap=False, bgc=self.color, text=self.path, vis=self.pathVisibility)
            self.button = cmds.button(parent=self.layout, label=self.textButton, w=60, bgc=Publisher.LIGHTGREY, vis=(not self.textButton))


            cmds.formLayout(self.layout, e=True, af=[(self.field, "top", 2), (self.field, "left", 2), (self.field, "bottom", 2),
                                                     (self.button, "top", 2), (self.button, "right", 2), (self.button, "bottom", 2)],
                                                 ac=[(self.field, "right", 2 * 2, self.button)])

    __prefPath = os.path.expanduser('~/') + "maya/2020/prefs/cs"
    __prefName = "Publisher"
    @staticmethod
    def writePref(name, value):
        prefVars = {} 
        fPath = os.path.join(Publisher.__prefPath, Publisher.__prefName + ".pref")
        if not os.path.isdir(Publisher.__prefPath):
            os.makedirs(Publisher.__prefPath)
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
        fPath = os.path.join(Publisher.__prefPath, Publisher.__prefName + ".pref")
        if not os.path.isdir(Publisher.__prefPath):
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
        self.pathsLays = []
        self.savePaths = Publisher.readPref("savePaths")
        if self.savePaths is None:
            self.savePaths = {}
        self.scriptJobIndex = []
        self.wipRollback = None
    
    def attachPaths(self):
        '''Apply the change (or not) of the path layout to display all the fields
        '''
        top = None
        listPathLays = []
        listPathLays.append(self.localPath)
        listPathLays += self.pathsLays
        listPathLays.append(self.addPath)
        listPathLays.append(self.relativePath)
        af = []
        ac = []
        an = []
        for pl in listPathLays:
            if top is None:
                af.append((pl.layout, "top", 2))
            else:
                ac.append((pl.layout, "top", 2, top.layout))
            af.append((pl.layout, "left", 2))
            af.append((pl.layout, "right", 2))
            top = pl
        cmds.formLayout(self.pathLayout, e=True, af=af, ac=ac)

    def addPathLay(self, path):
        '''Add a line in the interface for a saving path (server, extrnal hdd, usb stick, etc)
        path: str of the path to a 'set project' of a maya project
        Use attachPaths() to apply change
        '''
        fieldPath = Publisher.PathLine(self.pathLayout)
        fieldPath.textButton = "Remove"
        fieldPath.color = Publisher.BLUE
        fieldPath.func = Callback(self.removePathEvent, fieldPath)
        fieldPath.path = path
        self.pathsLays.append(fieldPath)

    # Button event action
    #   Path panel Event
    def getProjectEvent(self, *args):
        path = cmds.workspace( q=True, rootDirectory=True )
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return
        self.localPath.path = path


    def addPathEvent(self, *args):
        path = cmds.fileDialog2(fm=2, cap="Set project on server or hdd")
        if path == None or len(path) < 1:
            return
        path = os.path.abspath(path[0])
        if self.localPath.path == path:
            return
        for pl in self.pathsLays:
            if pl.path == path:
                return
        self.addPathLay(path)
        self.attachPaths()

        if self.localPath.path in self.savePaths:
            self.savePaths[self.localPath.path].append(path)
        else:
            self.savePaths[self.localPath.path] = [path]
        Publisher.writePref("savePaths", self.savePaths)

    def removePathEvent(self, pf, *args):
        '''button action: Will remove the pathField (pf) from the interface
        '''
        self.pathsLays.remove(pf)
        cmds.deleteUI(pf.layout)

        self.attachPaths()
        if self.localPath.path in self.savePaths:
            self.savePaths[self.localPath.path].remove(pf.path)
        Publisher.writePref("savePaths", self.savePaths)
    
    def reloadPathEvent(self, *args):
        
        for pl in self.pathsLays:
            cmds.deleteUI(pl.layout)
        self.pathsLays = []

        if self.localPath.path in self.savePaths:
            for p in self.savePaths[self.localPath.path]:
                self.addPathLay(p)
        self.attachPaths()


    def getRelativePathEvent(self, *args):
        '''button action: will set the relative path
        to the value of the absolute filepath minus the local path
        '''
        localPath = self.localPath.path
        filepath = os.path.abspath(cmds.file(q=True, sn=True))
        relativePath = filepath.replace(localPath, "")
        if len(relativePath) > 0:
            if relativePath[0] == "/" or relativePath[0] == "\\":
                relativePath = relativePath[1:]
        self.relativePath.path = relativePath

    #   Action panel

    def backupEvent(self, *args):
        localPath = self.localPath.path
        relativePath = self.relativePath.path
        if self.localPath.path in self.savePaths:
            for savePath in self.savePaths[self.localPath.path]:
                savePathDir = os.path.dirname(os.path.join(savePath, relativePath))
                if not os.path.exists(savePath):
                    cmds.warning("This path no longer exists : {}".format(savePath))
                    continue
                if not os.path.exists(savePathDir):
                    os.makedirs(savePathDir)
                shutil.copy(os.path.join(localPath, relativePath), os.path.join(savePath, relativePath))


    #      default action panel Event
    def prepPubDefaultEvent(self, *args):
        '''save the file as a *.pub.ma
        And store the current file to wipRollback
        '''
        # switch button
        cmds.button(self.rollbackToWipDefaultBtn, e=True, en=True)
        cmds.button(self.prepPublishDefaultBtn, e=True, en=False)
        
        # increment and save
        mel.eval("incrementAndSaveScene 1;")
        
        # store current file
        self.wipRollback = os.path.abspath(cmds.file(q=True, sn=True))
        pubPath = self.wipRollback[:-3] + ".pub" + self.wipRollback[-3:]
        cmds.file(rename=pubPath)
        cmds.file(save=True, type='mayaAscii')
        

    def rollbackToWipDefaultEvent(self, *args):
        '''Create a new wip incrementation from wipRollback
        '''
        # switch button
        cmds.button(self.rollbackToWipDefaultBtn, e=True, en=False)
        cmds.button(self.prepPublishDefaultBtn, e=True, en=True)

        cmds.file(self.wipRollback, o=True, f=True)

    def checkDefaultEvent(self, *args):
        pass

    @staticmethod
    def getVersionFromName(name):
        n = name.split(".")
        if n == None or len(n) < 1:
            return 1
        n = n[0]
        n = re.findall('_v[0-9]{3}', n)[0].replace("_v", "")
        return int(n)

    @staticmethod
    def getLastVersion(path):
        i = 0
        if os.path.isdir(path + "/versions"):
            versions = os.listdir(path + "/versions")
            for v in versions:
                j = re.findall('[0-9]{3}', v)
                if len(j) == 1:
                    i = max(int(j[0]), i)
        return i
    
    def writeMetadata(self):
        if not cmds.objExists("publisher_metadata"):
            node = cmds.createNode('partition', n='publisher_metadata')
        else:
            return
        cmds.addAttr(node, longName="Comment", dataType="string")
        cmds.addAttr(node, longName="Author", dataType="string")
        cmds.addAttr(node, longName="Computer", dataType="string")
        cmds.addAttr(node, longName="Date", dataType="string")
        cmds.addAttr(node, longName="Version", dataType="string")
        

        relativePath = self.relativePath.path
        nVersion = "Unknown"
        if os.path.normpath(relativePath).split(os.sep)[-2] == "wip":
            _, fileNameWip = os.path.split(relativePath)
            nVersion = str(Publisher.getVersionFromName(fileNameWip))

        comment = cmds.textField(self.commentTextLay, q=True, text=True)
        cmds.setAttr("publisher_metadata.Comment", comment, type="string")
        cmds.setAttr("publisher_metadata.Author", getpass.getuser(), type="string")
        cmds.setAttr("publisher_metadata.Computer", os.environ['COMPUTERNAME'], type="string")
        cmds.setAttr("publisher_metadata.Date", datetime.now().strftime("%H:%M:%S"), type="string")
        cmds.setAttr("publisher_metadata.Version", nVersion, type="string")
        
        cmds.textField(self.commentTextLay, e=True, text="")

    def publishDefaultEvent(self, *args):
        cmds.button(self.rollbackToWipDefaultBtn, e=True, en=False)
        cmds.button(self.prepPublishDefaultBtn, e=True, en=True)


        # Write Metadata
        if self.wipRollback is None:
            self.prepPubDefaultEvent()
        self.writeMetadata()
        cmds.file( save=True, type='mayaAscii' )
        self.refreshUI()

        localPath = self.localPath.path
        relativePath = self.relativePath.path


        if os.path.normpath(relativePath).split(os.sep)[-2] != "wip":
            cmds.warning("The current file is not a WIP")
            return
        wipPath, fileNameWip = os.path.split(relativePath)
        publishPath, _ = os.path.split(wipPath)
        versionPath = os.path.join(publishPath, "versions")
        
        nVersion = Publisher.getVersionFromName(fileNameWip)
        
        fileName = "_".join(fileNameWip.split(".")[0].split("_")[:-1])
        fileNamePublish = fileName + "." + fileNameWip.split(".")[-1]
        fileNameVersion = fileName + "_v{0:0>3d}.".format(nVersion) + fileNameWip.split(".")[-1]
        fileNameNewWip = fileName + "_v{0:0>3d}.0001.ma".format(nVersion + 1)

        if not os.path.exists(os.path.join(localPath, versionPath)):
            os.makedirs(os.path.join(localPath, versionPath))
        shutil.copy(os.path.join(localPath, relativePath), os.path.join(localPath, versionPath, fileNameVersion))
        shutil.copy(os.path.join(localPath, relativePath), os.path.join(localPath, publishPath, fileNamePublish))
        

        if self.wipRollback is not None:
            cmds.file(self.wipRollback, o=True, f=True)
        self.wipRollback = None 
        cmds.file(rename="/".join([localPath, wipPath, fileNameNewWip]))
        cmds.file( save=True, type='mayaAscii' )

    def uploadLastVersionDefaultEvent(self, *args):
        localPath = self.localPath.path
        relativePath = self.relativePath.path

        if os.path.normpath(relativePath).split(os.sep)[-2] != "wip":
            cmds.warning("The current file is not a WIP")
            return
        wipPath, fileNameWip = os.path.split(relativePath)
        publishPath = os.path.dirname(wipPath)
        versionPath = os.path.join(publishPath, "versions")
        
        fileName = "_".join(fileNameWip.split(".")[0].split("_")[:-1])
        nVersion = Publisher.getLastVersion(os.path.join(localPath, publishPath))
        fileNameVersion = fileName + "_v{0:0>3d}.".format(nVersion) + fileNameWip.split(".")[-1]
        fileNamePublish = fileName + "." + fileNameWip.split(".")[-1]


        # check if folder exist and no problem in versionning
        if self.localPath.path in self.savePaths:
            for savePath in self.savePaths[self.localPath.path]:
                if not os.path.exists(savePath):
                    cmds.warning("this path is not accesible : {}".format(savePath))
                    continue
                svpf = os.path.join(savePath, versionPath, fileNameVersion)
                if not os.path.exists(os.path.join(savePath, versionPath)):
                    continue
                versions = os.listdir(os.path.join(savePath, versionPath))
                sNversion = 0
                for v in versions:
                    sNversion = max(sNversion, Publisher.getVersionFromName(v))
                if os.path.exists(svpf):
                    cmds.error("{} already exist".format(svpf))
                if nVersion < sNversion:
                    cmds.error("Time travel error: The version in {} is later than the current one".format(svpf))


        if self.localPath.path in self.savePaths:
            for savePath in self.savePaths[self.localPath.path]:
                svp = os.path.join(savePath, versionPath)
                spp = os.path.join(savePath, publishPath)
                svpf = os.path.join(svp, fileNameVersion)
                sppf = os.path.join(spp, fileNamePublish)

                savePathDir = os.path.dirname(os.path.join(savePath, relativePath))
                if not os.path.exists(savePath):
                    cmds.warning("path not found".format(savePath))
                    continue
                if not os.path.exists(svp):
                    os.makedirs(svp)
                if not os.path.exists(spp):
                    os.makedirs(spp)
                shutil.copy(os.path.join(localPath, versionPath, fileNameVersion), os.path.join(savePath, svpf))
                shutil.copy(os.path.join(localPath, publishPath, fileNamePublish), os.path.join(savePath, sppf))
    
    @staticmethod
    def cleanStudent(path):
        if path.split(".")[-1] != "ma":
            return
        with open(path,'r+') as f :
            try:
                new_f = f.readlines()
                f.seek(0)
                for line in new_f:
                    if 'fileInfo "license" "student";\n' not in line:
                        f.write(line)
                    f.truncate()
            except:
                pass

    def check(self, *_):
        
        localPath = self.localPath.path
        print(localPath)
        relativePath = self.relativePath.path
        print(relativePath)
        file = os.path.join(localPath, relativePath)
        result = Publisher.checkInteraction(localPath, file)
        print(len(result))
        for r in result:
            print("{} \t: {}".format(r['name'], r["status"]))
            for m in r['message']:
                t = (''.join(m)).encode('utf-8')
                print("\t{}".format(t))


    @staticmethod
    def checkInteraction(wkDir, file):
        inspector_path = r"S:\a.paris\Atelier\Gapalion\srcs\inspectors"
        sys.path.append(inspector_path) if inspector_path not in sys.path else None
        checker = __import__("maya2020")
        rsrcs_path = r"S:\a.paris\Atelier\Gapalion\resources\drills"
        result = []
        # return None
        drills_ls = checker.Drill.get_drills_from_tags(rsrcs_path, "#all")
        print(len(drills_ls))
        print("#"*50)
        if checker.Drill.execute_drills(drills_ls, file) == False:
            print("'ERROR - file does not exists - {}'".format(file))
            print(drills_ls)
        print(len(drills_ls))
        for d in drills_ls:
            result.append(d.to_dict())
        return result

    #       Anim action panel Event
    def confoAnimEvent(self, *args):
        ################
        #      WIP     #
        ################
        ''' Change all the ref of mod or rig to surf,
        publish it and increment the version
        '''
        #to hide the print of cmds.file in the terminal
        old_stdout = sys.stdout # backup current stdout

        localPath = self.localPath.path
        relativePath = self.relativePath.path
        
        # check if the current file is a WIP
        if os.path.normpath(relativePath).split(os.sep)[-2] != "wip":
            cmds.warning("The current file is not a WIP")
            return
        
        # defining Names and Paths
        wipPath, fileNameWip = os.path.split(relativePath)
        publishPath, _ = os.path.split(wipPath)
        versionPath = os.path.join(publishPath, "versions")
        fileName = "_".join(fileNameWip.split(".")[0].split("_")[:-1])
        fileNamePublish = fileName + "." + fileNameWip.split(".")[-1]
        nVersion = Publisher.getVersionFromName(fileNameWip)
        fileNameVersion = fileName + "_v{0:0>3d}.".format(nVersion) + fileNameWip.split(".")[-1]
        fileNameNewWip = fileName + "_v{0:0>3d}.0001.ma".format(nVersion + 1)
        fileNameWipConfo = fileNameWip.replace(".ma", ".confo.ma")
        
        
        # increment and save
        # mel.eval("incrementAndSaveScene 1;")
        cmds.file(rename="/".join([localPath, wipPath, fileNameWipConfo]))
        cmds.file( save=True, type='mayaAscii' )
        Publisher.cleanStudent("/".join([localPath, wipPath, fileNameWipConfo]))

        # store current wip file
        self.wipRollback = os.path.abspath(cmds.file(q=True, sn=True))

        #swap all rig/mod ref to surf ref
        l = cmds.ls(type="reference", dag=True)
        for e in l:
            try:
                if cmds.objectType(e) == "reference":
                    print(e)
                    try:
                        original_path = cmds.referenceQuery( e,filename=True )
                        p = original_path.replace("rig", "surf")
                        p = p.replace("mod", "surf")
                        print("\t {}".format(p))
                        if os.path.exists(p):
                            sys.stdout = open(os.devnull, "w")
                            cmds.file(p, loadReference=e, type="mayaAscii", options="v=0;")
                            sys.stdout = old_stdout # reset old stdout
                    except:
                        pass
            except:
                pass

        #publish version
        
        
        if not os.path.exists(os.path.join(localPath, versionPath)):
            os.makedirs(os.path.join(localPath, versionPath))
        

        # saving Publish
        cmds.file(rename="/".join([localPath, publishPath, fileNamePublish]))
        cmds.file( save=True, type='mayaAscii' )
        Publisher.cleanStudent("/".join([localPath, publishPath, fileNamePublish]))

        # copy Publish to version
        shutil.copy(os.path.join(localPath, publishPath, fileNamePublish), os.path.join(localPath, versionPath, fileNameVersion))
        

        # mute cmds.file from printing in the console
        sys.stdout = open(os.devnull, "w")

        # opening curent wip file
        cmds.file(self.wipRollback, o=True, f=True)
        cmds.file(rename="/".join([localPath, wipPath, fileNameNewWip]))
        cmds.file( save=True, type='mayaAscii' )

        # unmute
        sys.stdout = old_stdout 

    def uploadLastVersionAnimEvent(self, *args):
        pass

    # Jobs
    def refreshUI(self):
        self.getProjectEvent()
        self.getRelativePathEvent()
        self.reloadPathEvent()

    def loadJobs(self):
                
        self.scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.refreshUI)]))
        self.scriptJobIndex.append(cmds.scriptJob(event=["SceneSaved", Callback(self.refreshUI)]))
        self.scriptJobIndex.append(cmds.scriptJob(event=["workspaceChanged", Callback(self.refreshUI)]))

    def killJobs(self):
        '''Kill all jobs
        '''
        for i in self.scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)

        pass

    def load(self):
        '''load the interface of the Publisher
        '''
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)
        cmds.scriptJob(ro=True, uid=[self.name, Callback(self.killJobs)])
        # self.scrlLayout = cmds.scrollLayout(hst=16, vst=16, cr=True, h=20)
        self.layout = cmds.formLayout(p=self.win)
        self.pathLayout = cmds.formLayout(p=self.layout, bgc=Publisher.DARKGREY)
        self.actionLayout = cmds.formLayout(p=self.layout, bgc=Publisher.DARKGREY)
        margin = 3
        cmds.formLayout(self.layout, e=True, af=[(self.pathLayout, "top", margin), (self.pathLayout, "right", margin), (self.pathLayout, "left", margin),
                                                 (self.actionLayout, "right", margin), (self.actionLayout, "left", margin)],
                                             ac=[(self.actionLayout, "top", 2 * margin, self.pathLayout)])
        
        # Path layout
        #   local path layout
        self.localPath = Publisher.PathLine(self.pathLayout)
        self.localPath.textButton = None
        self.localPath.func = Callback(self.getProjectEvent)
        self.localPath.color = Publisher.TURQUOISE
        self.getProjectEvent()

        if self.localPath.path in self.savePaths:
            for p in self.savePaths[self.localPath.path]:
                self.addPathLay(p)

        #   add Path Layout
        self.addPath = Publisher.PathLine(self.pathLayout)
        self.addPath.textButton = "Add"
        self.addPath.color = Publisher.BLUE
        self.addPath.pathVisibility = False
        self.addPath.func = Callback(self.addPathEvent)
        
        #   relative path layout
        self.relativePath = Publisher.PathLine(self.pathLayout)
        self.relativePath.textButton = None
        self.relativePath.color = Publisher.ORANGE
        self.relativePath.func = Callback(self.getRelativePathEvent)

        # attach aboves' layout to self.pathLayout
        self.attachPaths()
        self.getProjectEvent()
        self.getRelativePathEvent()


        # Action Layout
        
        self.tabsLay = cmds.tabLayout(parent=self.actionLayout)

        #   default panel
        self.defaultActionLay = cmds.formLayout("Default", parent=self.tabsLay)
        
        self.prepPublishDefaultBtn = cmds.button(parent=self.defaultActionLay, label="Prep Pub", h=20, bgc=Publisher.LIGHTGREY, en=True, c=Callback(self.prepPubDefaultEvent))
        self.rollbackToWipDefaultBtn = cmds.button(parent=self.defaultActionLay, label="Back To Wip", h=20, bgc=Publisher.LIGHTGREY, en=False, c=Callback(self.rollbackToWipDefaultEvent))

        self.checkDefaultBtn = cmds.button(parent=self.defaultActionLay, label="Check", h=20, bgc=Publisher.LIGHTGREY, en=True, c=Callback(self.check))

        
        self.commentSectionLay = cmds.rowColumnLayout(parent=self.defaultActionLay, numberOfColumns=2, columnAttach=[(1, 'right', 0), (2, 'right', 0)], adjustableColumn=2)
        cmds.text(parent=self.commentSectionLay, label='Comment : ')
        self.commentTextLay = cmds.textField(parent=self.commentSectionLay)

        self.publishDefaultBtn = cmds.button(parent=self.defaultActionLay, label="Publish", h=20, bgc=Publisher.TURQUOISE, en=True, c=Callback(self.publishDefaultEvent))
        self.uploadLastVersionDefaultBtn = cmds.button(parent=self.defaultActionLay, label="Upload Last Version", h=20, bgc=Publisher.BLUE, en=True, c=Callback(self.uploadLastVersionDefaultEvent))
        
        cmds.formLayout(self.defaultActionLay, e=True, af=[(self.prepPublishDefaultBtn, "top", margin), (self.prepPublishDefaultBtn, "left", margin),
                                                           (self.rollbackToWipDefaultBtn, "top", margin), (self.rollbackToWipDefaultBtn, "right", margin),
                                                           (self.checkDefaultBtn, "left", margin), (self.checkDefaultBtn, "right", margin),
                                                           (self.publishDefaultBtn, "left", margin), (self.publishDefaultBtn, "right", margin),
                                                           (self.commentSectionLay, "left", margin), (self.commentSectionLay, "right", margin),
                                                           (self.uploadLastVersionDefaultBtn, "left", margin), (self.uploadLastVersionDefaultBtn, "right", margin)],
                                                       ac=[(self.checkDefaultBtn, "top", 2 * margin, self.prepPublishDefaultBtn),
                                                           (self.commentSectionLay, "top", 2 * margin, self.checkDefaultBtn),
                                                           (self.publishDefaultBtn, "top", 2 * margin, self.commentSectionLay),
                                                           (self.uploadLastVersionDefaultBtn, "top", 2 * margin, self.publishDefaultBtn)],
                                                       ap=[(self.prepPublishDefaultBtn, "right", margin, 50), (self.rollbackToWipDefaultBtn, "left", margin, 50)])
       
        #   Anim Panel
        self.animActionLay = cmds.formLayout("Animation", parent=self.tabsLay)

        self.confoAnimBtn = cmds.button(parent=self.animActionLay, label="Confo", h=20, bgc=Publisher.TURQUOISE, en=True, c=Callback(self.confoAnimEvent))
        self.uploadLastVersionAnimBtn = cmds.button(parent=self.animActionLay, label="Upload Last Version", h=20, bgc=Publisher.BLUE, en=True, c=Callback(self.uploadLastVersionDefaultEvent))

        cmds.formLayout(self.animActionLay, e=True, af=[(self.confoAnimBtn, "top", margin), (self.confoAnimBtn, "left", margin), (self.confoAnimBtn, "right", margin),
                                                       (self.uploadLastVersionAnimBtn, "left", margin), (self.uploadLastVersionAnimBtn, "right", margin)],
                                                   ac=[(self.uploadLastVersionAnimBtn, "top", 2 * margin, self.confoAnimBtn)])


        self.backupBtn = cmds.button(parent=self.actionLayout, label="Back up", w=60, bgc=Publisher.ORANGE, c=Callback(self.backupEvent))

        
        cmds.formLayout(self.actionLayout, e=True, af=[(self.tabsLay, "top", margin), (self.tabsLay, "left", margin), (self.tabsLay, "bottom", margin),
                                                       (self.backupBtn, "top", margin), (self.backupBtn, "bottom", margin), (self.backupBtn, "right", margin)],
                                                   ac=[(self.tabsLay, "right", 2 * margin, self.backupBtn)])

        self.loadJobs()

