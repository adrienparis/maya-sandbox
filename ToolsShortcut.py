import sys
from maya import cmds
from maya import mel

TB_PATH = r"S:\a.paris\Rescources\ToolBox"
sys.path.append(TB_PATH) if TB_PATH not in sys.path else None
from miniToolsRig_v006 import MiniToolRig
from publisher import Publisher


def initializePlugin(*args):
    '''To load the tool as a plugin
    '''
    mel.eval('addNewShelfTab "CreativeSeeds";')
    MiniToolRig().load()
    Publisher().load()

def uninitializePlugin(*args):
    mel.eval('addNewShelfTab "CreativeSeeds";')

    MiniToolRig().unload()