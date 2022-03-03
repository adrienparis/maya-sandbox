from genericpath import exists
import os
import time
import tkinter as tk

from tkinter import filedialog


root = tk.Tk()

root.withdraw()


file_path = filedialog.askopenfilename(title="Sélectionnez un rapport d'enquête")

if file_path == "":
    exit()

corruptedFiles = []

print(file_path)
with open(file_path, "r") as f:
    l = f.readline()
    while l:
        l = f.readline()
        l = l[l.find(" - ") + 3:]
        l.replace("\n", "")
        l = l.rstrip().lstrip()
        print("[{}]".format(l))
        if len(l) != 0:
            corruptedFiles.append(l)


for cf in corruptedFiles:
    if cf.split(".")[-1] != "ma":
        continue
    with open(cf,'r+') as f :
        try:
            new_f = f.readlines()
            f.seek(0)
            
            file_iter = iter(new_f)
            for line in file_iter:
                if 'createNode script -n "vaccine_gene";' in line:
                    for i in range(0,12):
                        next(file_iter)                
                elif 'fileInfo "license" "student";\n' in line:
                    continue
                else:
                    f.write(line)
                f.truncate()
        except:
            pass