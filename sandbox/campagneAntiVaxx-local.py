from genericpath import exists
import os
import time

print(os.listdir("Q:"))
rootdir = "S:\\"

def isCorrupt(path):
    corruptNode = 'createNode script -n "vaccine_gene";'
    with open(path) as f:
        if corruptNode in f.read():
            return True
    return False


topFolders = os.listdir(rootdir)
topFolders = ['#backUp', '#recycle', 'annee01', 'annee02', 'annee03', 'annee04', 'annee05', 'bank']
topFolders = ['annee03', 'annee04', 'annee05', 'bank']

for topFolder in topFolders:
    print(topFolder)
    p = os.path.join(rootdir, topFolder)
    print(p)
    lenghtFiles = 0
    mayaFilesList = []
    for root, subdirs, files in os.walk(p):
        mayaFiles = [os.path.join(root, x) for x in files if x.endswith(".ma")]
        lenghtFiles += len(mayaFiles)
        mayaFilesList += mayaFiles
    print(lenghtFiles)

    lines = []
    oldPercent = 0
    oldFolder = None
    for i, mf_path in enumerate(mayaFilesList):
        if mf_path.split("\\")[3] != oldFolder:
            if oldFolder is not None:
                try:
                    with open("reports/report_{}_{}.txt".format(topFolder, oldFolder), "w+") as report:
                        report.writelines(lines)
                    lines = []
                except:
                    pass
            oldFolder = mf_path.split("\\")[3]
            print(oldFolder)

        percent = int((i * 100.0)/lenghtFiles)
        if percent != oldPercent:
            oldPercent = percent
            print("{} % -> {}".format(percent, mf_path))
        # if percent > 10:
            # break
        if isCorrupt(mf_path):
            # print(mf_path)
            t = time.ctime(os.path.getmtime(mf_path))
            # print(t)
            lines.append("{} - {}\n".format(t, mf_path))


    # i = 0.0
    # for root, subdirs, files in os.walk(p):
    #     mayaFiles = [x for x in files if x.endswith(".ma")]
    #     if len(mayaFiles) > 0:
    #         i += 1
    #         for mf in mayaFiles:
    #             mf_path = os.path.join(root, mf)
    #             if isCorrupt(mf_path):
    #                 # print(mf_path)
    #                 lines.append(mf_path)
        