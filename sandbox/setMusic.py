from maya import cmds
from maya import mel
music_file = cmds.fileDialog( dm='*.wav' )
nodeName = "music_{}".format("aww")

def getSelectedChannels():
	channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')	#fetch maya's main channelbox
	attrs = cmds.channelBox(channelBox, q=True, sma=True)
	if not attrs:
		return []
	return attrs

with open(music_file, "rb") as mf:
	data = mf.readlines()
nodeName = cmds.createNode("script", n=nodeName)
script = 'import os\nimport winsound\nmusicPath = os.path.expanduser("~/") + "maya/music"\nif not os.path.exists(musicPath):\n	os.makedirs(musicPath)\ndata = eval(cmds.getAttr("{}.nts"))\nmusic_file = os.path.join(musicPath, "{}.wav")\nwith open(music_file, "wb+") as mf:\n	mf.writelines(data)\nwinsound.PlaySound(music_file, winsound.SND_ASYNC)\n'.format(nodeName, nodeName.replace("music_", ""))
cmds.setAttr(nodeName + ".stp", 1)
cmds.setAttr(nodeName + ".st", 7)
cmds.addAttr(ci=True, sn="nts", ln="notes", dt="string")
cmds.setAttr(nodeName + ".nts", str(data), type="string")
cmds.setAttr(nodeName + ".b", script, type="string")



print(getSelectedChannels())



import maya.OpenMaya as om

def changed_radius(msg, m_plug, otherMplug, clientData):
	# msg  kIncomingDirection = 2048
	# msg  kAttributeSet = 8
	# 2048 + 8 = 2056
	if msg == 2056:
		if m_plug.partialName() == 'rz':
			m_node = m_plug.node()
			# Get node's rotateZ value
			rz_val = om.MFnDependencyNode(m_node).findPlug('rz').asFloat()
			# Set node's scaleX value to that of rotateZ
			att = om.MFnDependencyNode(m_node).findPlug('sx').setFloat(rz_val)



# Get sphere's MObject
sellist = om.MSelectionList()
sellist.add('pSphere1')
node = om.MObject()
sellist.getDependNode(0, node)

# Connect callback to event
id = om.MNodeMessage.addAttributeChangedCallback(node, changed_radius)








import os
import winsound
import maya.OpenMaya as om
def musicUpdateAttr(msg, m_plug, otherMplug, clientData):
	if msg == 2056:
		if m_plug.partialName() == 'rz':
			m_node = m_plug.node()
			rz_val = om.MFnDependencyNode(m_node).findPlug('rz').asFloat()
			att = om.MFnDependencyNode(m_node).findPlug('sx').setFloat(rz_val)

musicPath = os.path.expanduser("~/") + "maya/music"
if not os.path.exists(musicPath):
	os.makedirs(musicPath)
data = eval(cmds.getAttr("{}.nts"))
music_file = os.path.join(musicPath, "{}.wav")
with open(music_file, "wb+") as mf:
	mf.writelines(data)
winsound.PlaySound(music_file, winsound.SND_ASYNC)
