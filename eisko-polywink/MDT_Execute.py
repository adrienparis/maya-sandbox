#!/usr/bin/env python
# -- coding: utf-8 --

from maya import mel
from maya import cmds

class MDTExecution():

    def __init__(self, sourceModel, targetModel, sourcePointList, targetPointList):
        self.sourceModel = sourceModel
        self.targetModel = targetModel
        self.sourcePointList = sourcePointList
        self.targetPointList = targetPointList
        self.sourceFit = self.sourceModel + "_To_" + self.targetModel + "_MatchingDeformerNode_SourceFit"
        self.targetFit = self.sourceModel + "_To_" + self.targetModel + "_MatchingDeformerNode_TargetFit"
        self.deformedFit = self.sourceModel + "_To_" + self.targetModel + "_MatchingDeformerNode_DeformedFit"
        self.initiated = False
        self.shift = 0

    def processeByADMatching(self, admodifier, value):

        if value > 0:
        #     print (admodifier, value)
        #     cmds.evalDeferred("print('{}')".format(admodifier), lp=True)
        #     cmds.evalDeferred("cmds.setAttr('{}_To_{}_MatchingDeformerNode.{}', 1)".format(self.sourceModel, self.targetModel, admodifier), lp=True)
        #     cmds.evalDeferred("cmds.select('{}','{}')".format(self.sourceModel, self.targetModel), lp=True)
        #     cmds.evalDeferred("mel.eval('NPutInCorrespondence({})')".format(value), lp=True)
        #     cmds.evalDeferred("cmds.setAttr('{}_To_{}_MatchingDeformerNode.{}', 0)".format(self.sourceModel, self.targetModel, admodifier), lp=True)
        # cmds.evalDeferred("cmds.select(cl=True)", lp=True)

            print(admodifier)
            cmds.setAttr('{}_To_{}_MatchingDeformerNode.{}'.format(self.sourceModel, self.targetModel, admodifier), 1)
            cmds.select(self.sourceModel, self.targetModel)
            mel.eval('NPutInCorrespondence({})'.format(value))
            cmds.setAttr('{}_To_{}_MatchingDeformerNode.{}'.format(self.sourceModel, self.targetModel, admodifier), 0)
        cmds.select(cl=True)

    def process(self, G_AMD, L_AMD, ProjM):
        if not self.initiated:
            return
        cmds.evalDeferred('import maya.cmds as cmds\nimport maya.mel as mel\nprint "Start" ')
        cmds.select(cl=True)

        self.processeByADMatching("doGlobalADMatching", G_AMD)
        self.processeByADMatching("doLocalADMatching", L_AMD)
        self.processeByADMatching("doProjectionMatching", ProjM)

    def applyModification(self):
        cmds.evalDeferred("bs = cmds.blendShape( {}, {})".format( self.deformedFit, self.sourceModel), lp=True)
        cmds.evalDeferred("print(bs)", lp=True)
        # cmds.evalDeferred("print(cmds.listAttr('{}'))".format(bs), lp=True)
        # cmds.evalDeferred("cmds.delete('{}')".format(self.sourceFit), lp=True)
        # cmds.evalDeferred("cmds.delete('{}')".format(self.targetFit), lp=True)
        # cmds.evalDeferred("cmds.delete('{}')".format(self.deformedFit), lp=True)

    def init(self):
        cmds.select(self.sourceModel, self.targetModel)

        mel.eval('MatchingDeformerToolCmd -m "create" ')

        if self.shift != 0:
            cmds.setAttr(self.sourceFit + ".ty", self.shift)
            cmds.setAttr(self.targetFit + ".ty", self.shift)
            cmds.setAttr(self.targetFit + ".tx", self.shift)
            cmds.setAttr(self.deformedFit + ".tx", self.shift)
            cmds.setAttr(self.deformedFit + ".ty", self.shift)
            cmds.setAttr(self.targetModel + ".tx", self.shift)

        commande = "int $sourceCorrespondingPointsIndex1[] = {" + str(self.sourcePointList)[1:-1] + "};\n" + \
                "int $targetCorrespondingPointsIndex1[] = {" + str(self.targetPointList)[1:-1] + "};\n"
        mel.eval(commande)

        mel.eval(
            """
            FullfilCorrespondingPointsLocator("{}", "{}", $sourceCorrespondingPointsIndex1, $targetCorrespondingPointsIndex1)
            """.format(self.sourceFit, self.targetFit)
        )
        self.initiated = True
# cmds.scriptEditorInfo(ch=True)
cmds.file("C:/Users/Adrien Paris/Documents/local_temp/polywink/TestRigPro/order_20220816_1803495 _GMMADUEQX_SpaceDive/08_RigPro/20220907_Sk_Elly_Head_RigPro_etape_01_MDT_init.mb", f=True, options="v=0;", ignoreVersion=True, typ="mayaBinary", o=True)



sourcePointList = [123,808,2336,426,2036,2106,2275,1671,456,405,357,466,2191,64,1184,1020,2498,2579,1972,1310,2488,2557,1384,2581,2563,2531,2525,199,1633,207,1612,1587,2477,1272,2483,2537,2464,2576,2451,2707,3392,4920,3010,4620,4690,4859,4255,3040,2989,2941,3050,4775,2648,3604,3768,4556,3894,3968,2783,4217,2791,4196,4171,3856]
sourcePointList = [1369,1467,910,1081,945,885,899,1256,1238,1233,397,136,1324,249,1974,1969,47,2209,1963,2037,2205,49,2027,40,2225,42,2483,493,711,578,624,2504,2194,2164,2196,35,31,26,1784,3882,3980,3423,3594,3458,3398,3412,3769,3751,3746,2910,2649,3837,2762,4466,4471,4460,4533,4523,3006,3224,3091,3137,4941,4660]
targetPointList = [3015,2075,3109,3071,3123,3085,3045,3168,2819,2812,2737,2743,2744,2547,433,440,181,319,602,454,183,325,594,315,2022,962,1917,2478,2541,2382,2334,3299,51,2616,1291,1282,1314,848,1592,1624,642,1722,1680,1733,1696,1658,1779,1411,1403,1327,1333,1335,1119,119,112,294,132,285,1047,1113,953,904,1913,1186]
sourceModel = "head_preDeform_geo"
targetModel = "Elly_Head_Skin001"

mdt = MDTExecution(sourceModel, targetModel, sourcePointList, targetPointList)

mdt.init()
mdt.process(1, 1, 1)
mdt.applyModification()
