import os
from datetime import date
from maya import cmds

# full_path = "/".join([ws, "images", "dailyScreenShot", asset_name, current_date])
full_path = r"C:\Users\Adrien Paris\Documents\local_temp\HyeJin_Kwon\images\beauty"

def take_screenShot(name, width=1080, height=1080):
    img_path = "/".join([full_path, name + ".jpg"])
    cmds.playblast(fr=0, v=False, fmt="image", c="jpg", orn=False, cf=img_path, wh=[width,height], p=100)

sel = cmds.ls(sl=True)
for s in sel:
    cmds.setAttr(s + ".v", 0)


for s in sel:
    cmds.setAttr(s + ".v", 1)
    take_screenShot(s)
    cmds.setAttr(s + ".v", 0)

for s in sel:
    cmds.setAttr(s + ".v", 1)