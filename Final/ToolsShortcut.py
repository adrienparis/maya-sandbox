import sys
from maya import cmds
from maya import mel

TB_PATH = r"S:\a.paris\Rescources\ToolBox"
PLUGIN_SHELF_NAME = "Creative Seeds"
sys.path.append(TB_PATH) if TB_PATH not in sys.path else None
from miniToolsRig_v006 import MiniToolRig
from publisher import Publisher

def getLastCommonParent(top):
    childrens = cmds.layout(top, q=True, ca=True)
    if len(childrens) != 1:
        print(childrens)
        return top, childrens
    return getLastCommonParent("{}|{}".format(top, childrens[0]))

def getPlugInShelf():
    parent, childrens = getLastCommonParent("Shelf|MainShelfLayout")
    n = [c for c in childrens if c.startswith("ShelfLayout")]
    if len(n) != 1:
        return None
    n = n[0]
    n = "{}|{}".format(parent, n)
    lay, _ = getLastCommonParent(n)
    return lay


def initializePlugin(*args):
    '''To load the tool as a plugin
    '''
    shelfLay = getPlugInShelf()
    if shelfLay is not None:
        plugInTab = "{}|{}".format(shelfLay, PLUGIN_SHELF_NAME)
        if not cmds.layout(plugInTab, q=True, ex=True):
            cmds.shelfLayout(PLUGIN_SHELF_NAME, p=shelfLay)

    MiniToolRig().load()
    Publisher().load()

def uninitializePlugin(*args):
    
    shelfLay = getPlugInShelf()
    plugInTab = "{}|{}".format(shelfLay, PLUGIN_SHELF_NAME)

    if shelfLay is not None:
        if cmds.layout(plugInTab, q=True, ex=True):
            cmds.deleteUI(plugInTab)

    MiniToolRig().unload()