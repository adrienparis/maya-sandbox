import maya.cmds as cmds


def isDifferent(left, right, transform):
	Ltx = cmds.getAttr(left + "." + transform)
	Rtx = cmds.getAttr(right + "." + transform)

#0.000000000000001
	diffAdd = (Ltx + Rtx) > 0.001 or (Ltx + Rtx) < - 0.001
	diffSub = (Ltx - Rtx) > 0.001 or (Ltx - Rtx) < - 0.001
	str1 = "difference between " + left + " and " + right
	str2 = transform 
	str3 = "Left - Right=" + "%.30f" %(Ltx - Rtx)
	str4 = "Left + Right=" + "%.30f" %(Ltx + Rtx)
	if diffAdd and diffSub:
		print('{:<60s} {:<20s} {:<50s} {:<50s}'.format(str1,str2,str3,str4))

def isWrongSize(obj):
	sx = cmds.getAttr(obj + ".scaleX")
	sy = cmds.getAttr(obj + ".scaleY")
	sz = cmds.getAttr(obj + ".scaleZ")

	if sx > 1.00000000000001 or sx < 0.999999999999:
		print(obj + ".scaleX ->" + "%.30f" %sx)
	if sy > 1.00000000000001 or sy < 0.999999999999:
		print(obj + ".scaleY ->" + "%.30f" %sy)
	if sz > 1.00000000000001 or sz < 0.999999999999:
		print(obj + ".scaleZ ->" + "%.30f" %sz)

def compareLeftRight(ObjList):
	left = ""
	right = ""	

	for obj in ObjList:
		if obj.startswith("TMP_"):
			isWrongSize(obj)
			if obj[-1] == 'L' or obj[-1] == 'R':
				if obj[-1] == 'L':
					left = obj
					continue
				right = obj
				isDifferent(left, right, 'translateX')
				isDifferent(left, right, 'translateY')
				isDifferent(left, right, 'translateZ')
				isDifferent(left, right, 'rotateX')
				isDifferent(left, right, 'rotateY')
				isDifferent(left, right, 'rotateZ')

objects = cmds.ls(type="transform")
	
print("====================================================================================================================================================================")
compareLeftRight(objects)
print("====================================================================================================================================================================")