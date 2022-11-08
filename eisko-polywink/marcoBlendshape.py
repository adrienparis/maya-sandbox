import pymel.core as pm
import time
from maya import cmds
###_________________________________________________________________####
##__select_all_BS__##
BS_list = []
for x in pm.ls(selection=True, sn = True):
    BS_list.append(str(x).split(':')[-1])
###_________________________________________________________________####
BS_list=pm.listAttr('BS_Node.w',m=1)
###_________________________________________________________________####
##__select_all_Mesh_to_combine__##
msh_to_combine = []
for x in pm.ls(selection=True):
    msh_to_combine.append(str(x))
###_________________________________________________________________####
##__FOR_SPECIFIC_EXISTING_BS_##
print BS_list
Prefixe = ""
meshs_duplicated = []
for b in BS_list:
    for m in msh_to_combine:
        pm.duplicate(m, n = m + "_duplicated")
        meshs_duplicated.append(str(m + "_duplicated"))
    pm.polyUnite(meshs_duplicated, n = Prefixe+b, ch = False)
    for x in meshs_duplicated:
        pm.delete(x)
###_________________________________________________________________####
##__FOR_SPECIFIC_NON-EXISTING_BS_##
Prefixe = ""
newBS = "tongueOut"
meshs_duplicated = []
for m in msh_to_combine:
    pm.duplicate(m, n = m + "_duplicated")
    meshs_duplicated.append(str(m + "_duplicated"))
pm.polyUnite(meshs_duplicated, n = Prefixe+newBS, ch = False)
for x in meshs_duplicated:
    if pm.objExists(x):
        pm.delete(x)
###_________________________________________________________________####
##__fill_BS_list__check_names__and_execute__##
start = time.time()
BS_Node = "MASTER_BS_Node_cnt"
Prefixe = "XXX_"
BS_Grp="BS_tmp_GRP"
renameFlag = False
try:
    cmds.aimConstraint('Jaw_01_jnt', q = True)
    aim_constraint=pm.aimConstraint('Jaw_01_jnt', q=1)
    aim_constraint=aim_constraint+'.jawAimW0'
    jawExists = True
except:
    jawExists = False
#setting lenPerc in float space (aka binary space) will not be accurate in base ten display but watev
lenPerc = 100/float(len(BS_list))
iter = 0
#setting the progress window
cmds.progressWindow(title="Processing Shapes", progress=0, status="Starting")
for b in BS_list:
    #Print and advancing the progress window and iter
    #print("processing shape: "+b)
    cmds.progressWindow(e=True, progress=iter*lenPerc, status="{} % Processing {}".format(int((iter*lenPerc) * 100)/100.0, b))
    iter+=1
    #reset BS value to zero to avoid interference
    for w in BS_list:
        pm.setAttr(BS_Node+'.'+w, 0)
    #set BS value of list to 1
    pm.setAttr(BS_Node+'.'+b, 1)
    if jawExists == True:
        if "jaw" in b or 'V_Open' in b:
            print('/ Jaw in {} / Activating aim constraint'.format(b))
            pm.setAttr(aim_constraint,1)
        else:
            pm.setAttr(aim_constraint,0)
    #duplicate all mesh with 1 activated blendshape, combine and delete history
    meshs_duplicated = []
    for m in msh_to_combine:
        meshs_duplicated.append(pm.duplicate(m, n = m + "_duplicated"))
    if len(msh_to_combine) > 1 :
        pm.polyUnite(meshs_duplicated, n = b, ch = False)
        for x in meshs_duplicated:
            if pm.objExists(x):
                pm.delete(x)
    elif len(msh_to_combine) == 1 :
        pm.rename(meshs_duplicated[0], b)
    if renameFlag == True:
        pm.rename(BS_Grp+'|'+b,Prefixe+b)
        pm.hide(b)
    #reset all BS value to zero
    for w in BS_list:
        pm.setAttr(BS_Node+'.'+w, 0)
if jawExists == True:
    pm.setAttr(aim_constraint,1)
#closing the progress window
cmds.progressWindow(endProgress=True)
end = time.time()
total_time =  end - start
print("EXECUTION TIME : \n ### {} ###".format(str(total_time)))
###_________________________________________________________________####
for s in cmds.ls(sl = True):
    cmds.rename(s, s.replace('XXX_', ''))
###_________________________________________________________________####
##__fill_BS_list__check_names__and_execute__##
BS_Node = "BS_Node"
Prefixe = "XXX_"
BS_Grp="BS_GRP"
for b in BS_list:
    print("processing shape: "+b)
    #reset BS value to zero to avoid interference
    for w in BS_list:
        pm.setAttr(BS_Node+'.'+w, 0)
    #set BS value of list to 1
    pm.setAttr(BS_Node+'.'+b, 1)
    #duplicate all mesh with 1 activated blendshape, combine and delete history
    meshs_duplicated = []
    for m in msh_to_combine:
        meshs_duplicated.append(pm.duplicate(m, n = m + "_duplicated"))
    if len(msh_to_combine) > 1 :
        pm.polyUnite(meshs_duplicated, n = b, ch = False)
        for x in meshs_duplicated:
            if pm.objExists(x):
                pm.delete(x)
    elif len(msh_to_combine) == 1 :
        pm.rename(meshs_duplicated[0], b)
    #pm.rename(BS_Grp+'|'+b,Prefixe+b)
    #pm.hide(b)
    #reset all BS value to zero
    for w in BS_list:
        pm.setAttr(BS_Node+'.'+w, 0)
		
###_____________________________________________________
###Connect all new blendshapes to the rig Node with all blendshapes selected
###_____________________________________________________
BSNode = "BS_Node"
BSLoc = "MASTER_BS_Node_cnt"
for x in BS_list:
    if pm.objExists(BSLoc+"."+x):
        pm.connectAttr(BSLoc+"."+x, BSNode+"."+x, force = True)
        print x + "  connected"
    else:
        print (str(BSLoc+"."+x) + '  not found')