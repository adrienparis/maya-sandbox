import maya.cmds as cmds

def rkc(src, old, new):
    if not old.lower() in src.lower():
        return src
    index = src.lower().index(old.lower())
    
    if index != 0 and src[index - 1] == "_":
        print(src)
        midLow = src[:index] + new.lower() + src[index + len(old):]
        midUp = src[:index] + new[:1].lower() + new[1:] + src[index + len(old):]
        print(midUp, midLow)
        if cmds.objExists(midLow):
            return midLow
        if cmds.objExists(midUp):
            return midUp
        if src[index : index + 1].isupper():
            return midUp
        return midLow
    if src[index : index + len(old)].isupper():
        return src[:index] + new.upper() + src[index + len(old):]
    elif src[index : index + len(old)].islower():
        return src[:index] + new.lower() + src[index + len(old):]
    else :
        return src[:index] + new + src[index + len(old):]

def multiReplaceRkc(src, words):
    '''
    words = [[old, new], [old, new], ...]
    '''
    for word in words:
        src = rkc(src, word[0], word[1])
    return src

wordsList = []
wordsList.append(["Shoulder" ,"BackHip"])
wordsList.append(["Elbow" ,"BackKnee"])
wordsList.append(["Wrist" ,"BackAnkle"])
wordsList.append(["Arm" ,"BackLeg"])
wordsList.append(["Hand" ,"BackFoot"])

sel = cmds.ls(sl=True)

connections = []
for s in sel:
    con = cmds.listConnections(s, c=True, p=True, s=True, d=False)
    if con is None:
        continue
    for i in range(0,len(con), 2):
        if con[i].endswith(".message"):
            continue
        connections.append([con[i + 1], con[i]])


newSel = [multiReplaceRkc(s, wordsList) for s in sel]
newCon = [[multiReplaceRkc(s[0], wordsList), multiReplaceRkc(s[1], wordsList)] for s in connections]
# newSel = [rkc(s, "_L", "_R") for s in sel]
# newCon = [[rkc(s[0], "_L", "_R"), rkc(s[1], "_L", "_R")] for s in connections]
for i in range(0, len(sel)):
    if not cmds.objExists(newSel[i]):
        # print(sel[i], newSel[i])
        cmds.duplicate(sel[i], n=newSel[i])
print("=" * 200)
for c in newCon:
    
    try:
        if not cmds.objExists(c[1].split(".")[0]):
            print(str(c[1]) + " does not exist")
            continue
        if cmds.isConnected(c[0], c[1]):
            continue
        cmds.connectAttr(c[0], c[1], f=True)
        print("\t" + str(c))
    except:
        print("failed " + str(c))