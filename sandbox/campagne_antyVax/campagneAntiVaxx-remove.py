import os
<<<<<<< HEAD
import sys 
=======
>>>>>>> edc5dd817ab36f0cbcf0264b3415fa7ca5816df1
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog

<<<<<<< HEAD
CURSOR_UP_ONE = '\x1b[1A' 
ERASE_LINE = '\x1b[2K' 
=======
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
>>>>>>> edc5dd817ab36f0cbcf0264b3415fa7ca5816df1
PROGSEARCHSIZE = 30

def generateProgressBar(percent):
    percent = int(percent)
    size = PROGSEARCHSIZE / 100.0
    p = int(percent * size)
    maxSize = int(100 * size)
    progressBar = "█" * p + " " * (maxSize - p)
    line = " {: 3d} % |{}| ".format(percent, progressBar)
    return line

currentTime = datetime.now()

<<<<<<< HEAD
def progress(incL, totalL, incF, totalF, f):
    global currentTime
    if currentTime + timedelta(milliseconds=100) >= datetime.now():
        return
    currentTime = datetime.now()

    totalSize = os.get_terminal_size().columns

    incL += 1
=======
def progress(incL, totalL, incF, totalF, f, force=False):
    global currentTime
    if currentTime + timedelta(milliseconds=500) >= datetime.now() and not force:
        return
    currentTime = datetime.now()


    totalSize = os.get_terminal_size().columns

    # incL += 1
>>>>>>> edc5dd817ab36f0cbcf0264b3415fa7ca5816df1
    percentL = (incL * 100.0) / totalL
    percentF = (incF * 100.0) / totalF

    os.system('cls' if os.name == 'nt' else 'clear')
    # for erase in range(3):
<<<<<<< HEAD
    #     sys.stdout.write(CURSOR_UP_ONE) 
    #     sys.stdout.write(ERASE_LINE) 
=======
    #     sys.stdout.write(CURSOR_UP_ONE)
    #     sys.stdout.write(ERASE_LINE)
>>>>>>> edc5dd817ab36f0cbcf0264b3415fa7ca5816df1


    lines = []
    lines.append(generateProgressBar(percentF))
    lines.append("{: {}d}/{}  -> {}".format(incF, len(str(totalF)) + 1, totalF, f))
    lines.append(generateProgressBar(percentL))
    for l in lines:
        l = l + " " * (totalSize - len(l))
        l = l[:totalSize - 1]
        print(l)


    # lineF = "{: 3d} % |{}| {: {}d}/{}  -> {}".format(percent, progressBar,incL, len(str(total)) + 1, total, f)
    # lineF = lineF + " " * (totalSize - len(lineF))
    # lineF = lineF[:totalSize - 1]

    # print(lineF, end="\r")

root = tk.Tk()

root.withdraw()


file_path = filedialog.askopenfilename(title="Sélectionnez un rapport d'enquête", initialdir=os.getcwd())

if file_path == "":
    exit()

corruptedFiles = []

print(file_path)
with open(file_path, "r") as f:
    l = f.readline()
    while l:
        l = l[l.find(" - ") + 3:]
        l.replace("\n", "")
        l = l.rstrip().lstrip()
        if not os.path.exists(l):
            continue
        if len(l) != 0:
            corruptedFiles.append(l)
        l = f.readline()


for fileCursor, cf in enumerate(corruptedFiles):
    if cf.split(".")[-1] != "ma":
        continue


    with open(cf, 'r+') as f :
        for count, line in enumerate(f):
            pass
    nbLines = count + 1
    print(nbLines)

    with open(cf, 'r+') as f :
        # try:
        new_f = f.readlines()
        f.seek(0)
<<<<<<< HEAD
        
        file_iter = iter(new_f)
        for il, line in enumerate(file_iter):
            progress(il, nbLines, fileCursor, len(corruptedFiles), cf)
            if 'createNode script -n "vaccine_gene";' in line:
                for i in range(0,12):
                    next(file_iter)                
            elif 'fileInfo "license" "student";\n' in line:
                continue
            else:
                f.write(line)
=======

        file_iter = iter(new_f)
        for il, line in enumerate(file_iter):
            progress(il, nbLines, fileCursor, len(corruptedFiles), cf)
            if 'createNode script -n "' in line:
                if 'vaccine_gene' in line:
                    for i in range(0,7):
                        next(file_iter)
                    continue
                if 'breed_gene' in line:
                    for i in range(0,4):
                        next(file_iter)
                    continue
            elif 'fileInfo "license" "student";\n' in line:
                continue
            f.write(line)
>>>>>>> edc5dd817ab36f0cbcf0264b3415fa7ca5816df1
            f.truncate()
        # except:
        #     print("error while reading[{}]".format(cf))
        #     pass
<<<<<<< HEAD
=======
progress(100, 100, len(corruptedFiles), len(corruptedFiles), cf, force=True)
>>>>>>> edc5dd817ab36f0cbcf0264b3415fa7ca5816df1

print("Done")
input("press enter")