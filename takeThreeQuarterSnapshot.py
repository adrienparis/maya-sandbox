import os
from datetime import date
from maya import cmds


today = date.today()
ws = cmds.workspace( q=True, rootDirectory=True )
current_date = today.strftime("%Y%m%d")
file_path_abs = cmds.file(q=True, sn=True)
file_path_rlt = file_path_abs.replace(ws, "")
asset_name = file_path_rlt.split("/")[-1].split("_")[1]
print(asset_name)
full_path = "/".join([ws, "images", "dailyScreenShot", asset_name, current_date])
print(full_path)
if not os.path.exists(full_path):
    os.makedirs(full_path)

class ImgName():
    i = 1
    def __call__(self, name):
        return '{:02}_{}'.format(self.i, name)
    def incr(self):
        self.i += 1

In = ImgName()

def take_screenShot(name, width=1920, height=1080, frame=100):
    img_path = "/".join([full_path, name + ".jpg"])
    cmds.playblast(fr=frame, v=False, fmt="image", c="jpg", orn=False, cf=img_path, wh=[width,height], p=100)

def switch_light(on=True):
    currentPanel = cmds.getPanel(withFocus=True)

    if cmds.getPanel(to=currentPanel) == "modelPanel":
        if on:
            cmds.modelEditor(currentPanel, e=True, dl="default")
        else:
            cmds.modelEditor(currentPanel, e=True, dl="none")

def zoom(v):
    currentPanel = cmds.getPanel(withFocus=True)

    if cmds.getPanel(to=currentPanel) == "modelPanel":
        curCamera=cmds.modelEditor(currentPanel,q=1,av=1,cam=1)
        cmds.xform(curCamera, rt=[0, 0, v], r=True, os=True)

def fit():
    if cmds.ls("GEO"):
        cmds.select(cmds.ls("GEO"), r=True)
    else:
        cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)
    cmds.viewFit()
    cmds.select(cl=True)

def isolateSelected(state):
    viewport = cmds.getPanel( withFocus = True)
    if cmds.ls("GEO"):
        cmds.select(cmds.ls("GEO"), r=True)
    else:
        cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)
    if 'modelPanel' in viewport:
        if state:
            cmds.isolateSelect( viewport, addSelected=True )
            cmds.isolateSelect( viewport, s=True )
            cmds.isolateSelect( viewport, addSelected=True )
            cmds.isolateSelect( viewport, s=True )
        else:
            cmds.isolateSelect( viewport, s=False )
    cmds.select(cl=True)

def wireframe_switcher(state=None):
    viewport = cmds.getPanel( withFocus = True)
    if 'modelPanel' in viewport:
        
        currentState = cmds.modelEditor( viewport, q = True, wireframeOnShaded = True) if state == None else not state
        if currentState:
            cmds.modelEditor( viewport, edit = True, wireframeOnShaded = False)
        else:
            cmds.modelEditor( viewport, edit = True, wireframeOnShaded = True)

chara = [u'C1:msh_eye_R', u'C1:msh_eye_L', u'C1:msh_pupil_L', u'C1:msh_body', u'C1:msh_tongue', u'C1:msh_teethDn', u'C1:msh_teethUp', u'C1:msh_gumDn', u'C1:msh_gumUp', u'C1:msh_stem', u'C1:msh_leaf', u'C1:msh_pupil_R']
poses = {}
poses["bonjour"] = 110
poses["quiMoi"] = 120
poses["regardeHeure"] = 140
poses["regardeHeureStress"] = 146
poses["tocToc"] = 150
poses["tocTocSeduce"] = 155
poses["drink"] = 160

old_sl = cmds.ls(sl=True)
current_view = cmds.lookThru(q=True)

for k, v in poses.items():
    print(k, v)
    cmds.currentTime(int(v))

    switch_light(True)
    cmds.lookThru('trois_quart')
    take_screenShot(In("{}_3.4".format(k)), frame=v)
    cmds.lookThru('front')
    take_screenShot(In("{}_front".format(k)), frame=v)
    cmds.lookThru('side')
    take_screenShot(In("{}_side".format(k)), frame=v)
    switch_light(False)
    cmds.lookThru('trois_quart')
    take_screenShot(In("{}_3.4_shadow".format(k)), frame=v)
    cmds.lookThru('front')
    take_screenShot(In("{}_front_shadow".format(k)), frame=v)
    cmds.lookThru('side')
    take_screenShot(In("{}_side_shadow".format(k)), frame=v)
    In.incr()
switch_light(True)
cmds.lookThru('persp')
