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







'import os\nimport winsound\nmusicPath = os.path.expanduser("~/"") + "maya/music"\nif not os.path.exists(musicPath):\n	os.makedirs(musicPath)\ndata = eval(cmds.getAttr("musica.nts"))\nmusic_file = os.path.join(musicPath, "sound.wav")\nwith open(music_file, "wb+") as mf:\n	mf.writelines(data)\nwinsound.PlaySound(music_file, winsound.SND_ASYNC)\n'




print('# @Author  : \xe9\xa1\xb6\xe5\xa4\xa9\xe7\xab\x8b\xe5\x9c\xb0\xe6\x99\xba\xe6\x85\xa7\xe5\xa4\xa7\xe5\xb0\x86\xe5\x86\x9b\r\n'.decode('utf-8'))
print('# \xe4\xbb\x85\xe4\xbd\x9c\xe4\xb8\xba\xe5\x85\xac\xe5\x8f\xb8\xe5\x86\x85\xe9\x83\xa8\xe4\xbd\xbf\xe7\x94\xa8\xe4\xbf\x9d\xe6\x8a\xa4 \xe4\xb8\x80\xe6\x97\xa6\xe6\xb3\x84\xe9\x9c\xb2\xe5\x87\xba\xe5\x8e\xbb\xe9\x80\xa0\xe6\x88\x90\xe7\x9a\x84\xe5\xbd\xb1\xe5\x93\x8d \xe6\x9c\xac\xe4\xba\xba\xe6\xa6\x82\xe4\xb8\x8d\xe8\xb4\x9f\xe8\xb4\xa3\r\n'.decode('utf-8'))
print('\xe4\xbd\xa0\xe7\x9a\x84\xe6\x96\x87\xe4\xbb\xb6\xe8\xa2\xab\xe6\x84\x9f\xe6\x9f\x93\xe4\xba\x86\xef\xbc\x8c\xe4\xbd\x86\xe6\x98\xaf\xe6\x88\x91\xe8\xb4\xb4\xe5\xbf\x83\xe7\x9a\x84\xe4\xb8\xba\xe6\x82\xa8\xe6\x9d\x80\xe6\xaf\x92\xe5\xb9\xb6\xe4\xb8\x94\xe5\xa4\x87\xe4\xbb\xbd\xe4\xba\x86~\xe4\xb8\x8d\xe7\x94\xa8\xe8\xb0\xa2~'.decode('utf-8'))