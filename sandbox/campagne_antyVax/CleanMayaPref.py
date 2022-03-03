import os
# from maya import cmds

# scriptsPath = cmds.internalVar(userAppDir=True) + "scripts"

scriptsPath = os.path.expanduser(r'~\Documents\maya\scripts')

if os.path.exists(os.path.join(scriptsPath, "vaccine.py")):
    print("Maya is contaminated")
    for f in ["userSetup.py", "userSetup.mel", "vaccine.py", "vaccine.pyc"]:
        p = os.path.join(scriptsPath, f)
        print(p)
        if os.path.exists(p):
            os.remove(p)
    print("Your Maya has been cleaned")
else:
    print("Your Maya is already cleaned")

input("press enter")
