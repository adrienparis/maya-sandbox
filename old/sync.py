#!/usr/bin/env python

"""sync.py: A little tool to help syncronise maya file for a CreativeSeeds pipeline"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "1.0"
__copyright__   = "Copyright 2021, Creative Seeds"

import os
import sys
import getpass
import shutil
from datetime import datetime
import re
import maya.cmds as cmds
import maya.mel as mel


__cbFuncNum_sync = 0
__cbFunc_sync = {}
def Callback_sync(func, *args, **kwargs):
    global __cbFuncNum_sync
    global __cbFunc_sync
    if callable(func):
        __cbFuncNum_sync += 1
        __cbFunc_sync[__cbFuncNum_sync - 1] = [func, args, kwargs]
        return "Callback_sync(" + str(__cbFuncNum_sync)  + ")"
    __cbFunc_sync[func - 1][0](*__cbFunc_sync[func - 1][1], **__cbFunc_sync[func - 1][2])

def onMayaDroppedPythonFile(*args):
    current_path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    sys.path.append(current_path)
    cmd = '''string $cmd = "from ''' + __name__ + ''' import *"; python($cmd);'''
    mel.eval(cmd)
    sync()

localPath = ""
serverPath = ""
relativePath = ""
comment = ""

def sync():
    #Interaction with the preference file
    # __prefPath = "C:/Users/" + getpass.getuser() + "/Documents/maya/2020/prefs/cs"
    __prefPath = "C:/Users/" + "LABOI" + "/Documents/maya/2020/prefs/cs"
    __prefName = "sync"
    def writePref(name, value):
        prefVars = {} 
        fPath = os.path.join(__prefPath, __prefName + ".txt")
        print(__prefPath)
        if not os.path.isdir(__prefPath):
            os.makedirs(__prefPath)
        if os.path.isfile(fPath):   
            with open(fPath, "r") as f:
                l = f.readline()
                while l:
                    res = eval(l)
                    prefVars[res[0]] = res[1]
                    l = f.readline()
        prefVars[name] = value
        with open(fPath, "w+") as f:
            for key in prefVars:
                f.writelines(str([key, prefVars[key]]) + "\n")

    def readPref(name):
        fPath = os.path.join(__prefPath, __prefName + ".txt")
        if not os.path.isdir(__prefPath):
            return None
        if not os.path.isfile(fPath):
            return None
        prefVars = {}    
        with open(fPath, "r") as f:
            l = f.readline()
            while l:
                res = eval(l)
                prefVars[res[0]] = res[1]
                if res[0] == name:
                    return(res[1])
                l = f.readline()
        return None

    def setPaths():
        global localPath
        global serverPath
        global relativePath
        localPath = readPref("localPath")
        if localPath == None:
            if os.path.exists("D:/"):
                localPath = "D:/"
            elif os.path.exists("S:/"):
                localPath = "S:/"
            localPath += getpass.getuser()

        serverPath = readPref("serverPath")
        if serverPath == None:
            serverPath = 'Q:/'
        relativePath = "click get button"

    def definePath(field):
        global localPath
        global serverPath
        if field.split("|")[-1] == "localPath":
            path = localPath 
        elif field.split("|")[-1] == "serverPath":
            path = serverPath
        else:
            path = ""
        if path == "":
            v = cmds.fileDialog2(fm=2, cap="Set path")
        else:
            v = cmds.fileDialog2( dir=path, fm=2, cap="Set path")
        if v == None or len(v) < 1:
            return
        v = v[0]
        if field.split("|")[-1] == "localPath":
            localPath = v
            writePref("localPath", localPath)
        elif field.split("|")[-1] == "serverPath":
            serverPath = v
            writePref("serverPath", serverPath)
        cmds.text(field, e=True, label=v)

    def btnGetRelative(field):
        global relativePath
        
        filepath = cmds.file(q=True, sn=True)
        filename = os.path.basename(filepath)
        raw_name, extension = os.path.splitext(filename)
        relativePath = filepath.replace(localPath, "")
        if len(relativePath) > 0:
            if relativePath[0] == "/" or relativePath[0] == "\\":
                relativePath = relativePath[1:]
        cmds.text(field, e=True, label=relativePath)
        
    def getVersion(topPath, middlePath):
        i = 0
        if os.path.isdir(topPath + "/" + middlePath + "/versions"):
            versions = os.listdir(topPath + "/" + middlePath + "/versions")
            for v in versions:
                j = re.findall('[0-9]{3}', v)
                if len(j) == 1:
                    i = max(int(j[0]), i)
        return i

    def getVersionFromName(name):
        n = name.split(".")
        if n == None or len(n) < 1:
            return 1
        n = n[0]
        n = re.findall('[0-9]{3}', n)[0]
        return int(n)


    def btnPublish(relativeField):
        global serverPath
        global localPath
        global relativePath
        global comment
        if relativePath.split("/")[-2] != "wip":
            cmds.warning("The current file is not a WIP")
            return
        middlePath = "/".join(relativePath.split("/")[:-2])
        # nVersion = getVersion(localPath, middlePath) + 1
        fileNameWip = relativePath.split("/")[-1]
        nVersion = getVersionFromName(fileNameWip)

        noteUtilities = getpass.getuser() + "\n"
        noteUtilities += os.environ['COMPUTERNAME'] + "\n"
        noteUtilities += datetime.now().strftime("%H:%M:%S") + "\n"
        noteUtilities += str(nVersion) + "\n"

        # cmds.createNode('partition', n='sync_versionComment')
        # cmds.createNode('partition', n='sync_versionUtilities')
        # cmds.setAttr("sync_versionComment.notes", "plip", type="string")
        # cmds.setAttr("sync_versionUtilities.notes", noteUtilities, type="string")

        fileNameShort = fileNameWip.split(".")[0]
        fileNameShort = "_".join(fileNameShort.split("_")[:-1])
        fileNamePublish = fileNameShort + "." + fileNameWip.split(".")[-1]
        fileNameVersion = fileNameShort + "_v{0:0>3d}.".format(nVersion) + fileNameWip.split(".")[-1]
        if not os.path.exists("/".join([localPath, middlePath, "versions"])):
            os.makedirs("/".join([localPath, middlePath, "versions"]))
        shutil.copy("/".join([localPath, relativePath]), "/".join([localPath, middlePath, "versions", fileNameVersion]))
        shutil.copy("/".join([localPath, relativePath]), "/".join([localPath, middlePath, fileNamePublish]))
        cmds.file(rename="/".join([localPath, middlePath, "wip", fileNameShort + "_v{0:0>3d}.0001.ma".format(nVersion + 1)]))
        cmds.file( save=True, type='mayaAscii' )
        btnGetRelative(relativeField)

    def btnDnLastVersion():
        global serverPath
        global localPath
        global relativePath
        if relativePath.split("/")[-2] != "wip":
            cmds.warning("The current file is not a WIP")
            return
        middlePath = "/".join(relativePath.split("/")[:-2])
        nVersion = getVersion(serverPath, middlePath)
        fileNameWip = relativePath.split("/")[-1]
        fileNameShort = fileNameWip.split(".")[0]
        fileNameShort = "_".join(fileNameShort.split("_")[:-1])
        fileNamePublish = fileNameShort + "." + fileNameWip.split(".")[-1]
        fileNameVersion = fileNameShort + "_v{0:0>3d}.".format(nVersion) + fileNameWip.split(".")[-1]
        if not os.path.exists("/".join([localPath, middlePath, "versions"])):
            os.makedirs("/".join([localPath, middlePath, "versions"]))
        shutil.copy("/".join([serverPath, middlePath, "versions", fileNameVersion]), "/".join([localPath, middlePath, "versions", fileNameVersion]))
        shutil.copy("/".join([serverPath, middlePath, fileNamePublish]), "/".join([localPath, middlePath, fileNamePublish]))
        
    def btnUpLastVersion():
        global serverPath
        global localPath
        global relativePath
        if relativePath.split("/")[-2] != "wip":
            cmds.warning("The current file is not a WIP")
            return
        middlePath = "/".join(relativePath.split("/")[:-2])
        nVersion = getVersion(localPath, middlePath)
        fileNameWip = relativePath.split("/")[-1]
        fileNameShort = fileNameWip.split(".")[0]
        fileNameShort = "_".join(fileNameShort.split("_")[:-1])
        fileNamePublish = fileNameShort + "." + fileNameWip.split(".")[-1]
        fileNameVersion = fileNameShort + "_v{0:0>3d}.".format(nVersion) + fileNameWip.split(".")[-1]
        if not os.path.exists("/".join([serverPath, middlePath, "versions"])):
            os.makedirs("/".join([serverPath, middlePath, "versions"]))
        shutil.copy("/".join([localPath, middlePath, "versions", fileNameVersion]), "/".join([serverPath, middlePath, "versions", fileNameVersion]))
        shutil.copy("/".join([localPath, middlePath, fileNamePublish]), "/".join([serverPath, middlePath, fileNamePublish]))

    def btnSync():
        pass

    def btnBackup():
        global serverPath
        global localPath
        global relativePath
        shutil.copy("/".join([localPath, relativePath]), "/".join([serverPath, relativePath]))

    def createWindow():
        global serverPath
        global localPath
        global relativePath
        name = u"Sync"
        if cmds.workspaceControl(name, exists=1):
            cmds.deleteUI(name)
        win = cmds.workspaceControl(name, ih=100, iw=200, retain=False, floating=True, h=30, w=30)
        fLay = cmds.formLayout(p=win)

        pathLay = cmds.formLayout(p=fLay, bgc=[0.36, 0.36, 0.36])
        serverPathField = cmds.text("serverPath", label=serverPath, p=pathLay, bgc=[0.32, 0.52, 0.65], h=30)
        localPathField = cmds.text("localPath", label=localPath, p=pathLay, bgc=[0.28, 0.66, 0.70], h=30)
        relativePathField = cmds.text("relativePath", label="click [get] button", p=pathLay, bgc=[0.86, 0.58, 0.34], h=30, rs=True)
        localPathBtn = cmds.button(parent=pathLay, label="set local", c=Callback_sync(definePath, localPathField))
        serverPathBtn = cmds.button(parent=pathLay, label="set server", c=Callback_sync(definePath, serverPathField))
        getRelativeBtn = cmds.button(parent=pathLay, label="get", c=Callback_sync(btnGetRelative, relativePathField))

        cmds.formLayout(pathLay, e=True, af=[(localPathField, "left", 5), (localPathField, "top", 5),
                                        (serverPathField, "left", 5),
                                        (serverPathBtn, "right", 5), (localPathBtn, "top", 5),
                                        (localPathBtn, "right", 5),
                                        (relativePathField, "left", 5), (relativePathField, "right", 5),
                                        (relativePathField, "bottom", 5),
                                        (getRelativeBtn, "right", 5)],
                                    ac=[(serverPathField, "top", 5, localPathField), (serverPathField, "right", 5, serverPathBtn),
                                        (serverPathBtn, "top", 5, localPathField), (localPathField, "right", 5, localPathBtn),
                                        (localPathBtn, "bottom", 5, serverPathField),
                                        (relativePathField, "top", 5, serverPathField), (relativePathField, "right", 5, getRelativeBtn),
                                        (getRelativeBtn, "top", 5, serverPathField)],
                                    an=[(serverPathField, "bottom"), 
                                        (localPathField, "bottom"),
                                        (serverPathBtn, "bottom"), (serverPathBtn, "left"), 
                                        (localPathBtn, "bottom"), (localPathBtn, "left"),
                                        (getRelativeBtn, "bottom"), (getRelativeBtn, "left"),
                                        ])

        syncLay = cmds.formLayout(p=fLay, bgc=[0.25, 0.25, 0.25])
        publishBtn = cmds.button(parent=syncLay, label="Publish", c=Callback_sync(btnPublish, relativePathField))

        loadLay = cmds.formLayout(p=syncLay, bgc=[0.3, 0.3, 0.3])
        dnLastVersionBtn = cmds.button(parent=loadLay, label="Download last version", c=Callback_sync(btnDnLastVersion), en=False)
        upLastVersionBtn = cmds.button(parent=loadLay, label="Upload last version", c=Callback_sync(btnUpLastVersion))
        syncBtn = cmds.button(parent=loadLay, label="Synchronize", c=Callback_sync(btnDnLastVersion), en=False)
        cmds.formLayout(loadLay, e=True, af=[(dnLastVersionBtn, "left", 5), (dnLastVersionBtn, "top", 5),
                                            (upLastVersionBtn, "right", 5), (upLastVersionBtn, "top", 5),
                                            (syncBtn, "left", 5), (syncBtn, "bottom", 5),(syncBtn, "right", 5)],
                                        ap=[(dnLastVersionBtn, "right", 2.5, 50),
                                            (upLastVersionBtn, "left", 2.5, 50)],
                                        ac=[(dnLastVersionBtn, "bottom", 2.5, syncBtn), 
                                            (upLastVersionBtn, "bottom", 2.5, syncBtn)],
                                        an=[(syncBtn, "top")]
                                        )

        backupWipBtn = cmds.button(parent=syncLay, label="Backup", c=Callback_sync(btnBackup))

        cmds.formLayout(syncLay, e=True, af=[(publishBtn, "left", 5), (publishBtn, "top", 5), (publishBtn, "right", 5),
                                            (backupWipBtn, "right", 5), (backupWipBtn, "bottom", 5), 
                                            (loadLay, "bottom", 5), (loadLay, "left", 5)],
                                        ac=[(backupWipBtn, "top", 5, publishBtn),
                                            (loadLay, "right", 5, backupWipBtn), (loadLay, "top", 5, publishBtn)],
                                        an=[(publishBtn, "bottom"),
                                            (backupWipBtn, "left")])


        cmds.formLayout(fLay, e=True, af=[(pathLay, "left", 5), (pathLay, "top", 5), (pathLay, "right", 5),
                                        (syncLay, "left", 5), (syncLay, "bottom", 5), (syncLay, "right", 5)],
                                        ac=[(syncLay, "top", 5, pathLay)],
                                        an=[(pathLay, "bottom")])

    setPaths()
    createWindow()

if __name__ == "__main__":
    sync()