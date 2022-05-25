from maya import cmds

path = cmds.fileDialog2(fm=1, cap="Select a piano converted maya file", ff="Piano Converted Maya Files (*.pcm)")[0]
print(path)
with open(path, "r") as f:
    data = f.readlines()
#print("".join(data))
midi = eval("".join(data))    
#print(midi)
# midi = midi[:50]

notes = ["C", "C_", "D", "D_", "E", "F", "F_", "G", "G_", "A", "A_", "B"]

cmds.progressWindow(title="Assign key to key ", progress=0, status="Sett all key to 0")
totalKey = len(midi)

# FRAMERATE = 30
# FRAMERATE = 29.97
FRAMERATE = 24
STARTTIME = 100
PRESSED = -3.5


cmds.currentTime(STARTTIME)
STARTTIME += 2
for i in range(0,88):
    octave = i / len(notes)
    note = i % len(notes)
    if notes[note][-1] == '_':
        ctrl = "c_key_B_{}{}".format(notes[note][0], octave)
    else:
        ctrl = "c_key_W_{}{}".format(notes[note], octave)
    if cmds.objExists(ctrl):
        cmds.setKeyframe(ctrl, at='rz', v=0.0, ott="step", itt="step")
        cmds.setKeyframe(ctrl, at='hand', v=0, ott="step", itt="step")


for p, i in enumerate(midi):
    percentage = float(p) / float(totalKey) * 100
    cmds.progressWindow(e=True, progress=percentage, status="{}/{}".format(p, totalKey))

    if i[0] == "time_signature":
        continue
    octave = i[1] / len(notes)
    note = i[1] % len(notes)
    if notes[note][-1] == '_':
        ctrl = "c_key_B_{}{}".format(notes[note][0], octave)
    else:
        ctrl = "c_key_W_{}{}".format(notes[note], octave)
    frame = i[2] * FRAMERATE

    velocity = int(((100 - i[4]) / 100) * FRAMERATE)
    color = i[3] + 1

    # cmds.currentTime(int(frame - 3 * velocity))
    # cmds.setKeyframe(ctrl, at='rz')
    # cmds.currentTime(int(frame - 2 * velocity))
    # cmds.setKeyframe(ctrl, at='rz', v=pressed)
    # cmds.currentTime(int(frame - velocity))
    # cmds.setKeyframe(ctrl, at='rz', v=0.0)
    if i[0] == "note_off":
        # cmds.currentTime(STARTTIME + int(frame) - 2)
        cmds.setKeyframe(ctrl, at='rz', v=PRESSED, ott="spline", itt="step", t=[STARTTIME + int(frame) - 2])
        # cmds.currentTime(STARTTIME + int(frame))
        cmds.setKeyframe(ctrl, at='rz', v=0.0, ott="step", itt="spline", t=[STARTTIME + int(frame)])
        cmds.setKeyframe(ctrl, at='hand', v=0, ott="step", t=[STARTTIME + int(frame)])
    elif i[0] == "note_on":
        # if cmds.getAttr(ctrl)
        # cmds.currentTime(STARTTIME + int(frame) - 1)
        cmds.setKeyframe(ctrl, at='rz', v=0, ott="spline", itt="step", t=[STARTTIME + int(frame) - 1])

        # cmds.currentTime(STARTTIME + int(frame))
        cmds.setKeyframe(ctrl, at='rz', v=PRESSED, ott="step", itt="spline", t=[STARTTIME + int(frame)])
        cmds.setKeyframe(ctrl, at='hand', v=color, ott="step", t=[STARTTIME + int(frame)])

cmds.progressWindow(endProgress=True)
