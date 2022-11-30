# print(elements_to_combine)
elements_to_combine = [u'head',
 u'hair',
 u'goaty',
 u'eyebrow_L',
 u'eyebrow_R',
 u'eyelash_L',
 u'eyelash_R',
 u'eye_L',
 u'eye_iris_L',
 u'eye_R',
 u'eye_iris_R',
 u'tongue',
 u'teeth_upper',
 u'teeth_lower']

for etc in elements_to_combine:
    hist = cmds.listHistory(etc, lv=1)
    print(hist)
    skinCl = cmds.ls(hist, type="skinCluster")
    if not skinCl:

        print(etc)
    else:
        print(etc, skinCl)
