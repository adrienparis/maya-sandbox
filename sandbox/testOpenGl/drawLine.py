#!/usr/bin/env python
# -- coding: utf-8 --
print(u"▼"*20)

import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI

view = OpenMayaUI.M3dView.active3dView()

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

view.beginGL()

glFT.glBegin(OpenMayaRender.MGL_LINES)

glFT.glVertex3f(0.0, -0.5, 0.0)
glFT.glVertex3f(0.0, 0.5, 0.0)

glFT.glEnd()

view.endGL()
print(u"▲"*20)