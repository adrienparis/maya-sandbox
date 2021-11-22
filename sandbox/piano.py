from maya import cmds

with open(r"S:\a.paris\Rescources\convertedPiano.txt", "r") as f:
    data = f.readlines()
#print("".join(data))
midi = eval("".join(data))    
#print(midi)
notes = ["C", "C_", "D", "D_", "E", "F", "F_", "G", "G_", "A", "A_", "B"]

for i in midi:
    if i[0] == "time_signature":
        continue
    octave = i[1] / len(notes)
    note = i[1] % len(notes)
    if notes[note][-1] == '_':
        ctrl = "c_key_B_{}d{}".format(notes[note][0], octave)
    else:
        ctrl = "c_key_W_{}{}".format(notes[note], octave)
    frame = i[2] * 24

    velocity = int((100 - i[4]))
    pressed = -3.5

    # cmds.currentTime(int(frame - 3 * velocity))
    # cmds.setKeyframe(ctrl, at='rz')
    # cmds.currentTime(int(frame - 2 * velocity))
    # cmds.setKeyframe(ctrl, at='rz', v=pressed)
    # cmds.currentTime(int(frame - velocity))
    # cmds.setKeyframe(ctrl, at='rz', v=0.0)
    if i[0] == "note_off":
        cmds.currentTime(int(frame))
        cmds.setKeyframe(ctrl, at='rz', v=0.0)
        cmds.setKeyframe(ctrl, at='hand', v=0)
    elif i[0] == "note_on":
        cmds.currentTime(int(frame))
        cmds.setKeyframe(ctrl, at='rz', v=pressed)
        cmds.setKeyframe(ctrl, at='hand', v=i[3] + 1)
    cmds.setKeyframe(ctrl, at='velocity', v=velocity)