import os
from maya import cmds

def bleach():
    print("Drinking bleach")

    scriptsPath = cmds.internalVar(userAppDir=True) + "scripts"


    virus_gene = ['sysytenasdasdfsadfsdaf_dsfsdfaasd', 'PuTianTongQing', 'daxunhuan']
    all_script_jobs = cmds.scriptJob(listJobs=True)
    for each_job in all_script_jobs:
        for each_gene in virus_gene:
            if each_gene in each_job:
                health = False
                job_num = int(each_job.split(':', 1)[0])
                cmds.scriptJob(kill=job_num, force=True)
    all_script = cmds.ls(type='script')
    if all_script:
        for each_script in all_script:
            commecnt = cmds.getAttr(each_script + '.before')
            for each_gene in virus_gene:
                if commecnt:
                    if each_gene in commecnt:
                        try:
                            cmds.delete(each_script)
                        except:
                            name_space = each_script.rsplit(':',1)[0]
                            print(name_space)



    if cmds.objExists("vaccine_gene"):
        cmds.delete("vaccine_gene")
    if cmds.objExists("breed_gene"):
        cmds.delete("breed_gene")

    for f in ["userSetup.py", "userSetup.mel", "vaccine.py"]:
        p = os.path.join(scriptsPath, f)
        print(p)
        if os.path.exists(p):
            os.remove(p)

    print("Bleach drinked")


def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    bleach()


