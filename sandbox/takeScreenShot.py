# -- coding: utf-8 --

__author__ = "Adrien PARIS"
__email__ = "a.paris.cs@gmail.com"

import os
import sys
import importlib
import maya.cmds as cmds

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
    sys.path.append(MAYA_LOCATION+"/Python/Lib/plat-win")
    sys.path.append(MAYA_LOCATION+"/Python/Lib/lib-tk")
    with open(os.devnull,"w") as devNull:
        original = sys.stdout
        sys.stdout = devNull
        import maya.standalone
        maya.standalone.initialize(name='python')
        sys.stdout = original 

def take_screenShot(name, width=1920, height=1080):
    img_path = os.path.join(argv[1], FOLDER_PATH, name + ".png")
    # print(img_path)
    # print(cmds.xform("persp", q=True, ws=True, rp=True))
    cmds.playblast(fr=0, v=False, fmt="image", c="png", orn=False, cf=img_path, wh=[width,height], p=100)

def unhideParents(obj):
    parent = cmds.listRelatives(obj, p=True)[0]
    cmds.setAttr(parent + ".visibility", True)
    unhideParents(parent)


if __name__ == "__main__":
    mayapy_path = sys.executable
    argv = sys.argv
    if len(argv) < 2:
        exit()
    ls = os.listdir(argv[1])
    files = [x for x in ls if x.endswith(".ma")]
    print(files)
    if not os.path.exists(os.path.join(argv[1], FOLDER_PATH)):
        os.makedirs(os.path.join(argv[1], FOLDER_PATH))

    nb_frames = len(files) * 3

    importmaya(mayapy_path)
    i = 0
    for file in files:
        try:
            file_path = os.path.join(argv[1], file)
            name = file[:-3] + "_rs"
            
            # img_path = os.path.join(argv[1], "images", name + ".jpg")
            # if os.path.exists(img_path):
            #     continue
            cmds.file(file_path, o=True, f=True)
            # take_screenShot(name)


            name = file.split("_")[1]

            # c = "persp"
            
            allObjects = cmds.ls()
            dagGeoObject = cmds.ls(g=True)
            allObjects = [x for x in allObjects if x not in dagGeoObject]
            for o in allObjects:
                try:
                    child = cmds.listRelatives(o)
                    if len(child) != 0:
                        childType = [True for c in child if cmds.objectType(c, isType="mesh") or cmds.objectType(c, isType="transform")]
                        if True in childType:
                            continue
                            

                    cmds.setAttr(o + ".visibility", False)
                except:
                    pass

                # try:
                #     if cmds.objectType(o, isType="transform"):
                #         child = cmds.listRelatives(o)
                #         try:
                #             childType = [cmds.objectType(c, isType="mesh") for c in child]
                #             if True in childType:
                #                 unhideParents(o)
                #                 continue
                #         except:
                #             pass
                #     print(o)
                #     cmds.setAttr(o + ".visibility", False)
                # except:
                #     pass

            cams = cmds.ls(type='camera')
            for cam in cams:
                cmds.setAttr(cam + '.rnd', 0)

            c = cmds.camera(n="turnTableScreenShot_cam")[0]
            light = cmds.createNode("directionalLight", n="turnTableScreenShot_light")
            gl = cmds.group(light)
            # cmds.lookThru(c)
            
            cmds.setAttr(c + '.rnd', 0)
            cmds.setAttr(c[:-1] + 'Shape1.rnd', 1)

            g = cmds.group([c, gl])
            cmds.setAttr(c + ".tx", 0)
            cmds.setAttr(c + ".ty", 8)
            cmds.setAttr(c + ".tz", 35)
            cmds.setAttr(c + ".rx", 0)
            cmds.setAttr(c + ".ry", 0)
            cmds.setAttr(c + ".rz", 0)
            cmds.setAttr(gl + ".tx", 0)
            cmds.setAttr(gl + ".ty", 0)
            cmds.setAttr(gl + ".tz", 0)
            cmds.setAttr(gl + ".rx", -10)
            cmds.setAttr(gl + ".ry", -10)
            cmds.setAttr(gl + ".rz", 0)

            for j in range(0, 3):
                cmds.setAttr(g + ".ry", i * (1440.0 / nb_frames))
                take_screenShot(name + "_" + str(i))
                i += 1
                print("{}%".format(int((float(i) / nb_frames)*100)))

            # cmds.playblast(fr=0, v=False, fmt="image", c="jpg", orn=False, cf=img_path, wh=[width,height], p=100)
            # print(cmds.ls())
        except:
            print("global")
            pass

