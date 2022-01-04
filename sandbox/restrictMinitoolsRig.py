import __main__
for i in dir(__main__):
    if "ini" in i:
        print(i)
print(__main__.MiniToolRig.Singleton)
mtr = __main__.MiniToolRig.Singleton

for k, i in mtr.sections.items():
    i.lock = True
mtr.load()
for name in mtr.sections_order:
        mtr.sections[name].unload()
        mtr.sections[name].load()
print(__main__.myTempEDPF.executeDroppedPythonFile)
import maya.app.general.executeDroppedPythonFile as module
print(module)

class manInTheMiddle():
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args):
        self.func(*args)
        
        print("I'm in the middle")
    def restore(self):


#module.executeDroppedPythonFile("S:/a.paris/Rescources/Toolbox/createFollows.py", "")

module.executeDroppedPythonFile = manInTheMiddle(module.executeDroppedPythonFile)
module.executeDroppedPythonFile = module.executeDroppedPythonFile.func
plop("S:/a.paris/Rescources/Toolbox/createFollows.py", "")