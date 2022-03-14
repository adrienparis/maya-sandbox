from maya import cmds


class FootAttr():
    def __init__(self, ctrl, attr, keys):
        self.ctrl = ctrl
        self.attr = attr
        self.driverKeys = keys
        self.drivenAttr = {}
        self.drivens_L = {}
        self.drivens_R = {}

    def addDriven(self, ctrl, attr, key):
        if len(key) != len(self.driverKeys):
            return False
        if ctrl in self.drivenAttr:
            self.drivenAttr[ctrl].append(attr)
        else:
            self.drivenAttr[ctrl] = [attr]
        self.drivens_L[ctrl + attr] = key
        self.drivens_R[ctrl + attr] = key
        return True

    def addDriven_L(self, ctrl, attr, key):
        if len(key) != len(self.driverKeys):
            return False
        if ctrl in self.drivenAttr:
            self.drivenAttr[ctrl].append(attr)
        else:
            self.drivenAttr[ctrl] = [attr]
        self.drivens_L[ctrl + attr] = key
        return True

    def addDriven_R(self, ctrl, attr, key):
        if len(key) != len(self.driverKeys):
            return False
        if ctrl in self.drivenAttr:
            self.drivenAttr[ctrl].append(attr)
        else:
            self.drivenAttr[ctrl] = [attr]
        self.drivens_R[ctrl + attr] = key
        return True
    
    def applyKeys(self):
        for side in ["L", "R"]:
            for i, k in enumerate(self.driverKeys):
                cmds.setAttr(self.ctrl + "_" + side + "." + self.attr, k)
                print("setAttr", self.ctrl + "_" + side + "." + self.attr, k)
                for c in self.drivenAttr:
                    attr = self.drivenAttr[c]
                    for a in attr:
                        if side == "L":
                            cmds.setAttr(c + "_L." + a, self.drivens_L[c + a][i])
                            print("setAttr", c + "_L." + a, self.drivens_L[c + a][i])
                        else:
                            cmds.setAttr(c + "_R." + a, self.drivens_R[c + a][i])
                            print("setAttr",c + "_R." + a, self.drivens_R[c + a][i])

                        cmds.setDrivenKeyframe(c + "_" + side + "." + a, cd=self.ctrl + "_" + side + "." + self.attr, itt="linear", ott="linear")
                        print("drivenKey", c + "_" + side + "." + a, self.ctrl + "_" + side + "." + self.attr)
                cmds.setAttr(self.ctrl + "_" + side + "." + self.attr, 0)

attrs = ["footRool", "toesRoll", "toesEndRoll", "heelPivot", "toesPivot", "toesEndPivot", "tilt"]
keys = {}

keys["footRool"] = FootAttr("c_IK_foot", "footRool", [0, 5, 10, -10])
keys["footRool"].addDriven("rf_heel", "rotateX", [0,0,0,-60])
keys["footRool"].addDriven("rf_leg", "rotateX", [0,80,0,0])
keys["footRool"].addDriven("rf_toesEnd", "rotateX", [0,0,70,0])

keys["toesRoll"] = FootAttr("c_IK_foot", "toesRoll", [0, 10, -10])
keys["toesRoll"].addDriven("rf_toes", "rotateX", [0,90,-90])

keys["toesEndRoll"] = FootAttr("c_IK_foot", "toesEndRoll", [0, 10, -10])
keys["toesEndRoll"].addDriven("rf_toesEnd", "rotateX", [0,90,-90])

keys["heelPivot"] = FootAttr("c_IK_foot", "heelPivot", [0, 10, -10])
keys["heelPivot"].addDriven_L("rf_heel", "rotateY", [0,90,-90])
keys["heelPivot"].addDriven_R("rf_heel", "rotateY", [0,-90,90])

keys["toesPivot"] = FootAttr("c_IK_foot", "toesPivot", [0, 10, -10])
keys["toesPivot"].addDriven_L("rf_toes", "rotateY", [0,90,-90])
keys["toesPivot"].addDriven_R("rf_toes", "rotateY", [0,-90,90])

keys["toesEndPivot"] = FootAttr("c_IK_foot", "toesEndPivot", [0, 10, -10])
keys["toesEndPivot"].addDriven_L("rf_toesEnd", "rotateY", [0,90,-90])
keys["toesEndPivot"].addDriven_R("rf_toesEnd", "rotateY", [0,-90,90])

keys["tilt"] = FootAttr("c_IK_foot", "tilt", [0, 10, -10])
keys["tilt"].addDriven_L("rf_tiltInt", "rotateZ", [0,0,70])
keys["tilt"].addDriven_L("rf_tiltExt", "rotateZ", [0,-70,0])
keys["tilt"].addDriven_R("rf_tiltInt", "rotateZ", [0,0,-70])
keys["tilt"].addDriven_R("rf_tiltExt", "rotateZ", [0,70,0])





def createFootAttr():
    sides = ["L", "R"]
    attrs = ["footRool", "toesRoll", "toesEndRoll", "heelPivot", "toesPivot", "toesEndPivot", "tilt"]
    keys = [{"rf_heel_": [0, 5, 10, -10]},{"rf_heel_": [0, 5, 10, -10]}]
    for s in sides:
        cmds.addAttr("c_IK_foot_" + s, longName='footAttrs', attributeType='enum', en=" ", k=True)
        for a in attrs:
            cmds.addAttr("c_IK_foot_" + s, longName=a, defaultValue=0, minValue=-10, maxValue=10, k=True)
    
    
#    cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1.reverseroot", 0)
#    cmds.setAttr(inf + "_" + CONSTRAINT[const] + "1."  + Wname, 1)
#    cmds.setDrivenKeyframe(inf + "_" + CONSTRAINT[const] + "1." + Wname, cd=inf + "_" + CONSTRAINT[const] + "1.reverseroot")


createFootAttr()

for k in keys:
    keys[k].applyKeys()