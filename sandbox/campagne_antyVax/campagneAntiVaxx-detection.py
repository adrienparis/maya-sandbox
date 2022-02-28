from genericpath import exists
import os
import time
import io
import tkinter as tk


from tkinter import filedialog

PROGSEARCHSIZE = 30

class SearchingBar():
    def __init__(self):
        self.i = 0
        self.direction = 1
        self.speed = 0.01
        self.size = PROGSEARCHSIZE

    def print(self):
        totalSize = os.get_terminal_size().columns
        if self.i >= self.size:
            self.direction = -1
        elif self.i <= 0:
            self.direction = 1
        self.i += self.direction * self.speed 
        cursor = int(self.i)
        bar = " " * cursor + "*" + " " * (self.size - cursor) 
        line = "█{}█".format(bar)
        line = line[:totalSize]
        print(line, end="\r")


def isCorrupt(path):
    corruptNode = 'createNode script -n "vaccine_gene";'
    with io.open(path, "rb") as f:
        if bytes(corruptNode, 'utf-8') in f.read():
            return True
    return False

def progress(i, total, f):
    i += 1
    percent = int((i * 100.0)/total)
    size = PROGSEARCHSIZE / 100.0
    totalSize = os.get_terminal_size().columns
    p = int(percent * size)
    maxSize = int(100 * size)
    progressBar = "█" * p + " " * (maxSize - p)
    line = "{: 3d} % |{}| {: {}d}/{}  -> {}".format(percent, progressBar,i, len(str(total)) + 1, total, f)
    line = line + " " * (totalSize - len(line))
    line = line[:totalSize - 1]
    print(line, end="\r")


def getMayaFiles(directory):
    print("\nSearching maya files")
    schBar = SearchingBar()
    mayaFilesList = []
    for root, subdirs, files in os.walk(directory):
        mayaFiles = [os.path.join(root, x) for x in files if x.endswith(".ma")]
        mayaFilesList += mayaFiles
        schBar.print()

        # satusStr.set(root)
        # progressBarCounting['value'] += 1
        # progressWin.update_idletasks()
    return mayaFilesList

def searching():
    print("Starting")
    mayaFilesList = getMayaFiles(directory_path)
    print("\nAnalyzing maya files")
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
    print("\n\nDone !")
    return lines



root = tk.Tk()
root.withdraw()
directory_path = filedialog.askdirectory(title="Sélectionnez un dossier à analyser")
if directory_path == "":
    quit()
FolderName = directory_path.replace("/", "_").replace(":", "")


lines = searching()
reportFileName = "report_{}.txt".format(FolderName)
with open(reportFileName, "w+") as report:
    report.writelines(lines)
os.system('notepad.exe "{}"'.format(reportFileName))
