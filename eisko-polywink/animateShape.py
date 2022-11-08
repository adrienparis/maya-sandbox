from maya import cmds

targetMesh = cmds.ls(sl=True)[0]
blendshapes = cmds.ls(*cmds.listHistory(targetMesh) or [], type= 'blendShape')
bs = blendshapes[0]
print(blendshapes)
targets = cmds.listAttr(bs + ".w", m=True)

for t in targets:
    cmds.setKeyframe(bs, at=t, v=0, ott="flat", itt="flat", t=[1])
i = 10
for t in targets:
    cmds.setKeyframe(bs, at=t, v=0, ott="flat", itt="flat", t=[i - 4])
    cmds.setKeyframe(bs, at=t, v=1, ott="linear", itt="spline", t=[i])
    cmds.setKeyframe(bs, at=t, v=0, ott="flat", itt="flat", t=[i + 4])

    i += 10
