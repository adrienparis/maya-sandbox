from genericpath import exists
import os
import time
import io
import tkinter as tk

from tkinter import filedialog

def isCorrupt(path):
    corruptNode = 'createNode script -n "vaccine_gene";'
    with io.open(path, "rb") as f:
        if bytes(corruptNode, 'utf-8') in f.read():
            return True
    return False


root = tk.Tk()

root.withdraw()


directory_path = filedialog.askdirectory(title="Sélectionnez un dossier à analyser")

if directory_path == "":
    quit()
rootdir = "S:\\"




topFolders = [directory_path]

for topFolder in topFolders:
    print(topFolder)
    topFolderName = topFolder.replace("/", "_").replace(":", "")
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
        mf_path = os.path.normpath(mf_path)
        print(mf_path)
        if mf_path.split("\\")[3] != oldFolder:
            if oldFolder is not None:
                try:
                    with open("reports/report_{}_{}.txt".format(topFolderName, oldFolder), "w+") as report:
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

    print(lines)
    with open("report_{}.txt".format(topFolderName), "w+") as report:
        report.writelines(lines)


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
        