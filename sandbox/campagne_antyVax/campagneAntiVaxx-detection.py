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

def progress(i, total, f):
    i += 1
    percent = int((i * 100.0)/total)
    size = 0.5
    p = int(percent * size)
    maxSize = int(100 * size)
    progressBar = "█" * p + " " * (maxSize - p)
    line = "  {:02d} % |{}| \t{}/{}\t| ->\t{} ".format(percent, progressBar,i, total, f)
    print(line, end = "\r")


def getMayaFiles(directory):
    mayaFilesList = []
    for root, subdirs, files in os.walk(directory):
        mayaFiles = [os.path.join(root, x) for x in files if x.endswith(".ma")]
        mayaFilesList += mayaFiles

        # satusStr.set(root)
        # progressBarCounting['value'] += 1
        # progressWin.update_idletasks()
    return mayaFilesList

def searching():
    print("Starting")
    mayaFilesList = getMayaFiles(directory_path)
    nbFiles = len(mayaFilesList)
    oldPercent = 0
    lines = []
    for i, mf_path in enumerate(mayaFilesList):
        mf_path = os.path.normpath(mf_path)

        progress(i, nbFiles, mf_path)
        # percent = int((i * 100.0)/nbFiles)
        
        # if percent != oldPercent:
        #     oldPercent = percent
        #     print("{} % -> {}".format(percent, mf_path), end = "\r")
            
            # satusStr.set("{} %".format(percent))
            # progressWin.update_idletasks()
            # progressBarSearching['value'] = percent
        if isCorrupt(mf_path):
            t = time.ctime(os.path.getmtime(mf_path))
            lines.append("{} - {}\n".format(t, mf_path))
    print("\nDone !")
    return lines



root = tk.Tk()
root.withdraw()
directory_path = filedialog.askdirectory(title="Sélectionnez un dossier à analyser")
if directory_path == "":
    quit()
FolderName = directory_path.replace("/", "_").replace(":", "")


lines = searching()
print(lines)
with open("report_{}.txt".format(FolderName), "w+") as report:
    report.writelines(lines)
