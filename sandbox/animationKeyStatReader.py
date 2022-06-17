# -- coding: utf-8 --

__author__ = "Adrien PARIS"
__email__ = "a.paris.cs@gmail.com"

import os
import sys
import importlib
import maya.cmds as cmds
from PySide2 import QtGui


FOLDER_PATH = "images"
FOLDER_PATH = "TurnTable"

def importmaya(mayapy_path):

    MAYA_LOCATION = os.path.dirname(os.path.dirname(mayapy_path))
    PYTHON_LOCATION = os.path.join(MAYA_LOCATION, "/Python/Lib/site-packages")

    os.environ["MAYA_LOCATION"] = MAYA_LOCATION
    os.environ["PYTHONPATH"] = PYTHON_LOCATION

    sys.path.append(MAYA_LOCATION)
    sys.path.append(PYTHON_LOCATION)
    sys.path.append(MAYA_LOCATION+"/bin")
    sys.path.append(MAYA_LOCATION+"/lib")
    sys.path.append(MAYA_LOCATION+"/Python")
    sys.path.append(MAYA_LOCATION+"/Python/DLLs")
    sys.path.append(MAYA_LOCATION+"/Python/Lib")
    sys.path.append(MAYA_LOCATION+"/Python/Lib/site-packages")
    sys.path.append(MAYA_LOCATION+"/Python/Lib/plat-win")
    sys.path.append(MAYA_LOCATION+"/Python/Lib/lib-tk")
    
    with open(os.devnull,"w") as devNull:
        original = sys.stdout
        sys.stdout = devNull
        import maya.standalone
        maya.standalone.initialize(name='python')
        sys.stdout = original

def getAllMayaFile(path):
    mayaFiles = []
    for (root,dirs,files) in os.walk(path):
        for f in files:
            if f.endswith(".ma"):
                mayaFiles.append(os.path.join(root, f))
    return mayaFiles

def analyzeFile(file):
    print(file)
    cmds.file(file, o=True, f=True)
    ctrlsTr = [c for c in cmds.ls() if c.split(':')[-1].split('|')[-1].startswith("c_")]
    print(len(ctrlsTr))
    for c in ctrlsTr:
        print(c, cmds.objectType(c))
    ctrls = [c for c in ctrlsTr if True in [cmds.objectType(s, i="nurbsCurve") for s in cmds.listRelatives(c, c=True)]]
    print(len(ctrls))
    for c in ctrls:
        print(c)


def main(*argv):
    # path = filedialog.askdirectory(title="Sélectionnez un dossier de shots", filetypes=[("maya ascii files", "ma")])
    path = r"S:\a.paris\Atelier\goodHuman\03_work\maya\scenes\shots"
    print(path)
    mayaFiles = getAllMayaFile(path)
    for f in mayaFiles[:1]:
        print(f)
        analyzeFile(f)


    



if __name__ == "__main__":
    mayapy_path = sys.executable
    argv = sys.argv
    importmaya(mayapy_path)
    main(*argv)
