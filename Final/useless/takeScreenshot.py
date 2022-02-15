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
    i = 0
    def __call__(self, name):
        self.i += 1
        return '{:02}_{}'.format(self.i, name)
In = ImgName()

def take_screenShot(name, width=1920, height=1080):
    img_path = "/".join([full_path, name + ".jpg"])
    cmds.playblast(fr=0, v=False, fmt="image", c="jpg", orn=False, cf=img_path, wh=[width,height], p=100)

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

old_sl = cmds.ls(sl=True)
current_view = cmds.lookThru(q=True)
cmds.lookThru('persp')
isolateSelected(True)

# fit()
# zoom(-20)
wireframe_switcher(False)
switch_light(True)

take_screenShot(In("default"))

switch_light(False)
take_screenShot(In("shadow"))
switch_light(True)

wireframe_switcher(True)
take_screenShot(In("wireframe"))
wireframe_switcher(False)

# zoom(20)

cmds.lookThru('front')
fit()
# cmds.dolly( 'front', os=0.6666 )
take_screenShot(In("front"))
# cmds.dolly( 'front', os=1.5 )
cmds.hotkey( 'z', query=True, alt=True )

cmds.lookThru('side')
fit()

# cmds.dolly( 'side', os=0.6666 )
take_screenShot(In("side"))
cmds.hotkey( 'z', query=True, alt=True )

# cmds.dolly( 'side', os=1.5 )
cmds.lookThru(current_view)
cmds.select(old_sl)
isolateSelected(False)