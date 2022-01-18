
# "c:/Program Files/Autodesk/Maya2020/bin/mayapy.exe" "path/to/this/file" "path/to/src/project" "path/to/dest/project"

import os
import sys
import shutil
def copyLast(src, files):
    oldest = (None, 0)
    for f in files:
        age = f, os.path.getmtime(os.path.join(src, f))
        if age[1] > oldest[1]:
            oldest = age
    return oldest[0]
def main():
    args = sys.argv[1:]
    if len(args) != 2:
        return
    src = args[0]
    dst = args[1]
    for root, dirs, files in os.walk(src, topdown=True):
            relative = root[len(src) + 1:]
            for d in dirs:
                if not os.path.exists(os.path.join(dst, relative, d)):
                    os.makedirs(os.path.join(dst, relative, d))
    for root, dirs, files in os.walk(src, topdown=True):
        relative = root[len(src) + 1:]
        if root.split("\\")[-1] == "wip" or root.split("\\")[-1] == "versions":
            oldest = copyLast(root, files)
            if not os.path.exists(os.path.join(dst, relative, oldest)):
                shutil.copyfile(os.path.join(root, oldest), os.path.join(dst, relative, oldest))
        else:
            for f in files:
                if not os.path.exists(os.path.join(dst, relative, f)):
                    shutil.copyfile(os.path.join(root, f), os.path.join(dst, relative, f))
if __name__ == "__main__":
    main()
