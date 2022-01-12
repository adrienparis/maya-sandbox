#!/usr/bin/env python
# -- coding: utf-8 --


"""publisher.py: A little tool to help syncronise maya file for a CreativeSeeds pipeline"""

__author__      = "Adrien PARIS"
__email__       = "a.paris.cs@gmail.com"
__version__     = "3.0.0-alpha"
__copyright__   = "Copyright 2021, Creative Seeds"

import sys
import os
import ctypes
import threading
import time
import random
import webbrowser
import urllib
import shutil
import re
import getpass
import io
from datetime import datetime

try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

class Callback():
    '''Use for maya interface event, because it send you back your argument as strings
    func : the function you want to call
    *args : your arguments
    **kwargs : your keywords arguments

    Example:
    cmds.button(c=Callback(myFunc, arg1, arg2))
    cmds.button(c=Callback(myFunc, arg1, arg2).repeatable())
    '''
    __author__ = "Adrien PARIS"
    __email__ = "a.paris.cs@gmail.com"
    __version__     = "3.1.0"
    __copyright__   = "Copyright 2021, Creative Seeds"
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.repeatArgs = args
        self.kwargs = kwargs
        self.repeatable_value = False
        self.getCommandArgument_value = False

    def _addArgument(self, *args, **kwargs):
        self.args = args
        self.repeatArgs = args
        self.kwargs = kwargs
        return self
        
    def repeatable(self):
        ''' Call this methode to make the function repeatable with 'g'
        '''
        self.repeatable_value = True
        return self

    def getCommandArgument(self):
        ''' Call this methode to receive the argument of the event
        '''
        self.getCommandArgument_value = True
        return self
        
    def _repeatCall(self):
        return self.func(*self.repeatArgs, **self.kwargs)

    def __call__(self, *args):
        ag = self.args + args if self.getCommandArgument_value else self.args
        if self.repeatable_value:
            import __main__
            __main__.cb_repeatLast = self
            self.repeatArgs = ag
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast._repeatCall()"); ''')
        return self.func(*ag, **self.kwargs)

# Decorator
def callback(func):
    def wrapper(*args, **kwargs):
        return Callback(func, *args, **kwargs)
    return wrapper

def thread(func):
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return wrapper

def singleton(class_):
    class class_w(class_):
        __doc__ = class_.__doc__
        _instance = None
        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w,
                                    class_).__new__(class_,
                                                    *args,
                                                    **kwargs)
                class_w._instance._sealed = False
            return class_w._instance
        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
    class_w.__name__ = class_.__name__
    return class_w

class Module(object):
    '''Little bloc to encapsulate the UI's maya's system
    The parent must be either a Module, either a string that has the name of a maya's layout
    (cmds.layout, cmds.formLayout, cmds.columnLayout, ...)

    When converting this object to str, it print the layout to store his childrens
    like that, even if whe call it has a parent, it still return a maya's layout
    
    You must create a load function.
    
    Name your class starting by
    M_  if it's a simple module
    MG_ if it's a group of module
    MT_ if it's for a specific tools
    MC_ if it's for a control
    MGT_ if it's a group that contain tools
    '''
    # Maya's colors
    COLOR_WHITE = [1, 1, 1]
    COLOR_BLACK = [0, 0, 0]
    COLOR_BLUE = [0.32, 0.52, 0.65]
    COLOR_TURQUOISE = [0.28, 0.66, 0.70]
    COLOR_EUCALYPTUS = [0.37,0.68,0.53]
    COLOR_ORANGE = [0.86, 0.58, 0.34]
    COLOR_DARKGREY = [0.21, 0.21, 0.21]
    COLOR_GREY = [0.26, 0.26, 0.26]
    COLOR_LIGHTGREY = [0.36, 0.36, 0.36]
    COLOR_GREEN = [0.48, 0.67, 0.27]
    COLOR_RED = [0.85, 0.34, 0.34]
    COLOR_YELLOW = [0.86,0.81,0.53]


    increment = 0
    drag = None

    def __init__(self, parent, name=None):
        
        if name is None:
            name = self.__class__.__name__ + str(Module.increment)
            Module.increment += 1
        self.name = name
        self.childrens = []
        self.command = {}
        self.parent = None
        self.setParent(parent)
        self._scriptJobIndex = []
        self.childrenLayout = None
        self.layout = None
        self.bgc = None
        self.bgc = False
        self.dragged = False
        self.af = []
        self.ac = []
        self.ap = []

    def __str__(self):
        return str(self.childrenLayout)

    def __getattribute__(self, name):
        if name == 'load':
            return object.__getattribute__(self, "_load")
        if name == 'unload':
            return object.__getattribute__(self, "_unload")
        if name == "height":
            return cmds.layout(self.layout, q=True, h=True)
        if name == "width":
            return cmds.layout(self.layout, q=True, w=True)
        return object.__getattribute__(self, name)

    def setParent(self, parent):
        if self.parent is not None:
            if isinstance(self.parent, Module):
                self.parent.childrens.remove(self)
        self.parent = parent
        if isinstance(self.parent, Module):
            self.parent.childrens.append(self)

    def attach(self, elem, top=None, bottom=None, left=None, right=None, margin=(0,0,0,0)):
        '''For formLayout
            Register the attach information of your elem 
            attach "FORM": string
                    elem : layout/control
                    pos : float
                    None
            return elem
            Use applyAttach() to attach the layout to your parent
        '''
        if isinstance(elem, Module):
            e = elem.layout
        else:
            e = elem
        for s, n, m in [(top, "top", margin[0]), (bottom, "bottom", margin[1]), (left, "left", margin[2]), (right, "right", margin[3])]: 
            if s == None:
                continue
            if isinstance(s, (str, unicode)):
                if s.upper() == "FORM":
                    self.af.append((e, n, m))
                else:
                    self.ac.append((e, n, m, s))
            if isinstance(s, Module):
                self.ac.append((e, n, m, s.layout))
            if isinstance(s, (float, int)):
                self.ap.append((e, n, m, float(s)))
        return elem

    def clearAttach(self):
        self.af = []
        self.ac = []
        self.ap = []
    
    @staticmethod
    def _getParentLayout(attachList):
        parLayout = {}
        for af in attachList:
            e = af[0]
            if isinstance(e, Module):
                parLayout[e.parent] = [af] if e.parent not in parLayout else parLayout[e.parent] + [af]
            else:
                if cmds.layout(e, exists=True):
                    parent = cmds.layout(e, q=True, p=True)
                elif cmds.control(e, exists=True):
                    parent = cmds.control(e, q=True, p=True)
                else:
                    continue
                parLayout[parent] = [af] if parent not in parLayout else parLayout[parent] + [af] 
        return parLayout

    def applyAttach(self):
        parLayoutAf = Module._getParentLayout(self.af)
        parLayoutAc = Module._getParentLayout(self.ac)
        parLayoutAp = Module._getParentLayout(self.ap)
        parentlayouts = parLayoutAf.keys() + parLayoutAc.keys() + parLayoutAp.keys()
        parentlayouts = list(dict.fromkeys(parentlayouts))
        for pl in parentlayouts:
            af = parLayoutAf[pl] if pl in parLayoutAf else []
            ac = parLayoutAc[pl] if pl in parLayoutAc else []
            ap = parLayoutAp[pl] if pl in parLayoutAp else []
            try:
                cmds.formLayout(pl, e=True, af=af, ac=ac, ap=ap)
            except Exception as inst:
                print(inst)
                raise Exception("Can't attach {} {}".format(pl, inst))

    def _load(self):
        object.__getattribute__(self, "load")()
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self._killJobs)])
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self.unloadEvent)])
        self._loadJobs()
        return self

    def load(self):
        ''' Put your main layout in the self.layout
        If you use a formeLayout use self.attach()
        Put the layout where the childrens will go in self.childrenLayout
        '''
        raise Exception('load function not implemented')

    def reload(self):
        self.unload()
        self.load()

    def _unload(self):
        if self.layout == None:
            return self
        for c in self.childrens:
            c.unload()
        if cmds.workspaceControl(self.layout, exists=1):
            cmds.deleteUI(self.layout)
        return self

    def unload(self):
        pass
    
    def unloadEvent(self):
        pass

    def refresh(self):
        pass

    def move(self, other):
        parent = self.parent
        pos = parent.childrens.index(other)
        parent.childrens.remove(self)
        parent.childrens.insert(pos, self)
        parent.refresh()
        # tmp = cmds.formLayout(p=parent.layout)
        # for c in parent.childrens:
        #     cmds.layout(c.layout, e=True, p=tmp)
        # for c in parent.childrens:
        #     cmds.layout(c.layout, e=True, p=parent.childrenLayout)
        #     # c.reload()
        # cmds.deleteUI(tmp)

    # Jobs
    def _loadJobs(self):
        '''Load all jobs
        '''
        # Example : 
        # self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", Callback(self.methode)]))
        # raise Exception('_loadJobs function not implemented')
    def _killJobs(self):
        '''Kill all jobs
        '''
        for i in self._scriptJobIndex:
            cmds.scriptJob(kill=i, f=True)
        self._scriptJobIndex = []

    # drag&Drop
    def _dragCb(self, dragControl, x, y, modifiers):
        Module.drag = self
        
        if not self.dragged:
            self.bgc = cmds.layout(self.layout, q=True, bgc=True)
            self.ebg = cmds.layout(self.layout, q=True, ebg=True)
        self.dragged = True
        cmds.layout(self.layout, e=True, ebg=True)
        cmds.layout(self.layout, e=True, bgc=Module.COLOR_BLUE)
    def _dropCb(self, dragControl, dropControl, messages, x, y, dragType):
        cmds.layout(Module.drag.layout, e=True, bgc=Module.drag.bgc)
        cmds.layout(Module.drag.layout, e=True, ebg=Module.drag.ebg)
        Module.drag.dragged = False
        Module.drag.move(self)
        Module.drag = None

    # Events
    def eventHandler(self, event, c, *args):
        if not event in self.command:
            self.command[event] = []
        self.command[event].append((c, args))
    def runEvent(self, event, *args):
        if not event in self.command:
            return
        for c in self.command[event]:
            if c[0] is None:
                continue
            a = c[1] + args
            c[0](*a)

def info(message):
    mel.eval('trace -where ""; print "{}"; trace -where "";'.format(message))

@singleton
class Publisher(Module):
    __prefPath = os.path.expanduser('~/') + "maya/2020/prefs/cs"
    __prefName = "Publisher"
    @staticmethod
    def writePref(name, value):
        prefVars = {} 
        fPath = os.path.join(Publisher.__prefPath, Publisher.__prefName + ".pref")
        if not os.path.isdir(Publisher.__prefPath):
            os.makedirs(Publisher.__prefPath)
        if os.path.isfile(fPath):   
            with open(fPath, "r") as f:
                l = f.readline()
                while l:
                    try:
                        res = eval(l)
                        prefVars[res[0]] = res[1]
                    except:
                        pass
                    l = f.readline()
        prefVars[name] = value
        with open(fPath, "w+") as f:
            for key in prefVars:
                f.writelines(str([key, prefVars[key]]) + "\n")

    @staticmethod
    def readPref(name):
        fPath = os.path.join(Publisher.__prefPath, Publisher.__prefName + ".pref")
        if not os.path.isdir(Publisher.__prefPath):
            return None
        if not os.path.isfile(fPath):
            return None
        prefVars = {}    
        with open(fPath, "r") as f:
            l = f.readline()
            try:
                while l:
                    res = eval(l)
                    prefVars[res[0]] = res[1]
                    if res[0] == name:
                        return(res[1])
                    l = f.readline()
            except:
                pass
        return None

    class Theme():
        SAVE = Module.COLOR_BLUE
        LOCAL = Module.COLOR_TURQUOISE
        RELATIVE = Module.COLOR_ORANGE
        SEC_BGC = Module.COLOR_DARKGREY
        MAIN_BGC = Module.COLOR_GREY
        BUTTON = Module.COLOR_LIGHTGREY
        VALIDATION = Module.COLOR_GREEN
        ERROR = Module.COLOR_RED
        WARNING = Module.COLOR_YELLOW

    class Image():
        ADD = "addClip.png"
        ANIMATION = "animateSnapshot.png"
        DELETE = "deleteClip.png"
        CHECK = "SP_FileDialogContentsView.png"
        CLEAN = "brush.png"
        COMMON = "volumeCube.png"
        FOLDER = "openLoadGeneric.png"
        HELP = "help.png"
        LINE = "UVEditorUAxisDisabled.png"
        NETWORK = "SP_DriveNetIcon.png"
        PUBLISH = "SP_FileDialogForward.png"
        RIGHTARROW = "moveUVRight.png"
        SETTING = "QR_settings.png"
        SAVE = "UVTkSaveValue.png"
        UNDO = "undo_s.png"
        UNKNOW = "UVTkBtnHead.png"
        UPLOAD = "SP_FileDialogToParent.png"

    class Language():
        class En():
            class Button():
                prepare = "Prepare publish to be cleaned"
                rollback = "Rollback to last WIP"
                backup = "Backup current WIP to drives"
                check = "Run tests (you might set it in settings pannel)"
                publish = "Publish"
                upload = "Upload to drives"
                confo = "Confo"
                ticket = "Open a ticket"
                delete = "Delete"
                add = "Add"
                common = "Common"
                animation = "Animation"
                about = "About"
                settings = "Settings"

            class Label():
                comment = "Comments : "

            class About():
                PUBLISHER = """
                        <h1 style="background-color:{THEME_MAIN_BGC}; color:{THEME_SAVE};text-align: left;">{NAME} </h1>
                        <p>The {NAME} is a tool to help publish and sync maya files in a pipeline like Creative Seeds' one.</p>
                        <h4>Author :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{AUTHOR}</p>
                        <h4>Contact :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{EMAIL}</p>
                        <h4>Version :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{VERSION}</p>
                        <h4>Copyright :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{COPYRIGHT}</p>
                    """
                PATHS = """        
                        <h2>The Header of the application</h2>
                        <p>The top part of the application is to define the location of differents path</p>
                        <p>The <span class="publish">top line</span> indicate your "set project"</p>
                        <p>You can add a path to an other "set project" of a drive with <img src="{IMAGE_ADD}" style="background-color:{THEME_BUTTON}"/> to be sync latter</p>
                        <p>The added path will be this <span class="drives" > color</span></p>
                        <p>You can click on <img src="{IMAGE_DELETE}" style="background-color:{THEME_BUTTON}"/> at any time to remove a drive</p>
                        <p>The <span class="local"> last line</span> should display the path of your current opened file in maya relative to your set project</p>
                        <p>The opened file should be in the tree of the current project, or else it will display his absolute path</p>
                        <p>The color code works as follow:</p>
                        <ul>
                        <li> This <span class="publish"> color</span> for local project, or publishs</li>
                        <li> This <span class="drives"> color</span> for project in an other drive. (in a backup/shared drive)</li>
                        <li> This <span class="local"> color</span> for files related to wip files</li>
                        </ul>
                        <p></p>
                    """
                SYNCCOMMON = """
                        <h2>Common Synchronisation</h2>
                        <p>This section is made to match everybody's needs in term of preparing, publishing and uploading your version</p>
                        <p>To publish your version, first of all, you should have a WIP file openned</p>
                        <p>and have this file in the current project</p>
                        <p>then you can press on <img src="{IMAGE_PUBLISH}" class="publish"/></p>
                        <p>That will :</p>
                        <ul>
                            <li>Copy your current wip to the root folder of the asset and rename it</li>
                            <li>Copy it to the "versions" folder in  the root of the asset and rename it</li>
                            <li>Create a tumbnail of the current version and save it at the root and the versions' folder</li>
                            <li>Clean the Student Licences pop-up</li>
                            <li>Revert back to your current WIP, if you stored it with a "prepare publish"</li>
                            <li>Save a new WIP and rename it to the next version</li>
                        </ul>
                        <p>If you want to clean your scene before publishing it,</p>
                        <p>but still want to work with messy stuff in the future</p>
                        <p>Use the "prepare publish" button</p>
                        <p><img src="{IMAGE_CLEAN}" class="button"/></p>
                        <p>It will save your current WIP to a new scene, and store it so you can rollback to it if you change your mind</p>
                        <p>or it'll rollback itself when you publish it</p>
                        <p></p>
                        <p>To rollback when you change your mind press <img src="{IMAGE_UNDO}" class="button"/></p>
                        <p>It will restore you're last wip</p>
                    """
                SYNCANIMATION = """
                        <h2>Annimation Synchronisation</h2>
                        <p>Work in progress</p>
                        <p>This section is made for animator when they want to do a "confo"</p>
                        <p>When pressing the <img src="{IMAGE_PUBLISH}" class="publish" /> confo button</p>
                        <p>It will :</p>
                        <ul>
                            <li>copy</li>
                            <li>replace rig by surf</li>
                            <li>increment version</li>
                            <li>take a playblast</li>
                        </ul>
                        <p></p>
                        <p></p>
                        <p></p>
                    """
                SETTINGS = """
                        <h2>Settings</h2>
                        <p> Work in progress</p>
                    """
        
        class Fr():
            class Button():
                prepare = u"Préparer votre version avant de la publier"
                rollback = u"Revenir sur votre TEC précedent"
                backup = u"Sauvegarder votre TEC sur les périphérique de sauvegarde"
                check = u"Lancer les tests (vous devrer les configurer dans Paramètre)"
                publish = u"Publier"
                upload = u"Télécharger votre publication ainsi que \nla dernière sauvegarde vers vos périphérique de sauvegarde"
                confo = u"Confo"
                ticket = u"Ouvrir un ticket"
                delete = u"Supprimer"
                add = u"Ajouter"
                common = u"Commun"
                animation = u"Animation"
                about = u"À propos"
                settings = u"Paramètre"

            class Label():
                comment = u"Commentaires : "

            class About():
                PUBLISHER = u"""
                        <h1 style="background-color:{THEME_MAIN_BGC}; color:{THEME_SAVE};text-align: left;">{NAME} </h1>
                        <p>Le {NAME} est un outils pour publier et syncronisser des scènes maya dans un pipeline semblable à celui de Creative Seeds.</p>
                        <h4>Auteur :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{AUTHOR}</p>
                        <h4>Contact :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{EMAIL}</p>
                        <h4>Version :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{VERSION}</p>
                        <h4>Droits d'auteur :</h4> 
                        <p style="margin-left&#58; 30px; background-color:{COLOR_BLACK};color:{COLOR_WHITE};">{COPYRIGHT}</p>
                    """
                PATHS = u"""        
                        <h2>Définition des chemins</h2>
                        <p>La partie haute de l'application est pour définir les différents chemins du projets</p>
                        <p>La <span class="publish">ligne du haut</span> indique le chemin du projet que vous avez initialisé avec "set project"</p>
                        <p>En cliquant sur <img src="{IMAGE_ADD}" style="background-color:{THEME_BUTTON}"/> Vous pouvez ajouter un autre chemin de sauvegarde</p>
                        <p>Le chemin de sauvegarde ajouté sera de cette <span class="drives" > couleur</span></p>
                        <p>Vous pouvez cliquer sur <img src="{IMAGE_DELETE}" style="background-color:{THEME_BUTTON}"/> pour supprimer un chemin de sauvegarde</p>
                        <p>La <span class="local"> dernière ligne</span> Devrait afficher le chemin de la scène ouverte dans maya, relatif au chemin du projet</p>
                        <p>Le fichier ouvert doit être dans l'arborescence du projet en cours, sinon il affichera le chemin absolue</p>
                        <p>Si le chemin est absolu, l'application ne fonctionnera pas</p>
                        <p>Le code couleur fonctionne ainsi : </p>
                        <ul>
                            <li> Cette <span class="publish"> couleur</span> pour tout ce qui est en rapport avec les publication local</li>
                            <li> Cette <span class="drives"> couleur</span> pour les chemin de sauvegarde sur d'autres disques/péréphérique</li>
                            <li> Cette <span class="local"> couleur</span> pour files related to wip files</li>
                        </ul>
                        <p></p>
                    """
                SYNCCOMMON = u"""
                        <h2>Common Synchronisation</h2>
                        <p>This section is made to match everybody's needs in term of preparing, publishing and uploading your version</p>
                        <p>To publish your version, first of all, you should have a WIP file openned</p>
                        <p>and have this file in the current project</p>
                        <p>then you can press on <img src="{IMAGE_PUBLISH}" class="publish"/></p>
                        <p>That will :</p>
                        <ul>
                            <li>Copy your current wip to the root folder of the asset and rename it</li>
                            <li>Copy it to the "versions" folder in  the root of the asset and rename it</li>
                            <li>Create a tumbnail of the current version and save it at the root and the versions' folder</li>
                            <li>Clean the Student Licences pop-up</li>
                            <li>Revert back to your current WIP, if you stored it with a "prepare publish"</li>
                            <li>Save a new WIP and rename it to the next version</li>
                        </ul>
                        <p>If you want to clean your scene before publishing it,</p>
                        <p>but still want to work with messy stuff in the future</p>
                        <p>Use the "prepare publish" button</p>
                        <p><img src="{IMAGE_CLEAN}" class="button"/></p>
                        <p>It will save your current WIP to a new scene, and store it so you can rollback to it if you change your mind</p>
                        <p>or it'll rollback itself when you publish it</p>
                        <p></p>
                        <p>To rollback when you change your mind press <img src="{IMAGE_UNDO}" class="button"/></p>
                        <p>It will restore you're last wip</p>
                    """
                SYNCANIMATION = u"""
                        <h2>Synchronisation pour les fichier d'animation</h2>
                        <p>Travail en cours</p>
                        <p>Cette section est faite pour les animateur pour effectuer une "confo"</p>
                        <p>En appuyant sur <img src="{IMAGE_PUBLISH}" class="publish" alt="confo"/> confo button</p>
                        <p>It will :</p>
                        <ul>
                            <li>copy</li>
                            <li>replace rig by surf</li>
                            <li>increment version</li>
                            <li>take a playblast</li>
                        </ul>
                        <p></p>
                        <p></p>
                        <p></p>
                    """
                SETTINGS = u"""
                        <h2>Paramètres</h2>
                        <p> En cours de création</p>
                    """
        
        @staticmethod
        def getLg(name):
            if name is None:
                return None
            if name.upper() == "FR":
                return Publisher.Language.Fr
            if name.upper() == "EN":
                return Publisher.Language.En

    lg = Language.Fr

    class MC_PathLine(Module):

        def __init__(self, parent, image=None, color=Module.COLOR_BLUE, annotation=""):
            Module.__init__(self, parent)
            self.parent = parent
            self.color = color
            self.path = ""
            self.pathVisibility = True
            self.func = None
            self.image = image
            self.annotation = annotation
        
        def __setattr__(self, name, value):
            self.__dict__[name] = value
            if "field" in self.__dict__:
                if name == "path":
                    cmds.scrollField(self.field, e=True, text=self.path)
                if name == "color":
                    cmds.scrollField(self.field, e=True, bgc=self.color)
                if name == "pathVisibility":
                    cmds.scrollField(self.field, e=True, vis=self.pathVisibility)
            if "button" in self.__dict__:
                if name == "func":
                    cmds.iconTextButton(self.button, e=True, c=self.func)
                if name == "image":
                    if self.image is not None:
                        cmds.iconTextButton(self.button, e=True, image=self.image)
                    self._setButtonVis()
                if name == "annotation":
                    cmds.iconTextButton(self.button, e=True, ann=self.annotation)

        def _setButtonVis(self):
            btnVis = self.image is not None
            cmds.iconTextButton(self.button, e=True, vis=btnVis)

            self.attach(self.field, top="FORM", bottom="FORM", left="FORM", right=self.button if btnVis else "FORM", margin=(0,0,0, 4 if btnVis else 0))
            self.attach(self.button, top="FORM", bottom="FORM", left=None, right="FORM", margin=(0,0,0,0))
            self.applyAttach()

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent, h=35)
            self.field = cmds.scrollField(parent=self.layout, editable=False, h=27, wordWrap=False, bgc=self.color, text=self.path, vis=self.pathVisibility)
            if self.image is not None:
                self.button = cmds.iconTextButton(parent=self.layout, w=35, bgc=Publisher.COLOR_LIGHTGREY, ann=self.annotation, image=self.image)
            else:
                self.button = cmds.iconTextButton(parent=self.layout, w=35, bgc=Publisher.COLOR_LIGHTGREY, ann=self.annotation)
            self._setButtonVis()

    class MT_Paths(Module):
        def __init__(self, parent):
            Module.__init__(self, parent)
            self.lockColor = False
            self.pathsLays = []
            self.savePaths = Publisher.readPref("savePaths")
            if self.savePaths is None:
                self.savePaths = {}

        def attachPaths(self):
            '''Apply the change (or not) of the path layout to display all the fields
            '''
            top = None
            listPathLays = []
            listPathLays.append(self.localPath)
            listPathLays += self.pathsLays
            listPathLays.append(self.addPath)
            listPathLays.append(self.relativePath)
            af = []
            ac = []
            an = []
            for pl in listPathLays:
                if top is None:
                    af.append((pl.layout, "top", 4))
                else:
                    ac.append((pl.layout, "top", 4, top.layout))
                af.append((pl.layout, "left", 4))
                af.append((pl.layout, "right", 4))
                top = pl
            cmds.formLayout(self.layout, e=True, af=af, ac=ac)

        def addPathLay(self, path):
            '''Add a line in the interface for a saving path (server, extrnal hdd, usb stick, etc)
            path: str of the path to a 'set project' of a maya project
            Use attachPaths() to apply change
            '''
            fieldPath = Publisher.MC_PathLine(self.layout).load()
            fieldPath.image = Publisher.Image.DELETE
            fieldPath.annotation = Publisher.lg.Button.delete
            fieldPath.color = Publisher.Theme.SAVE
            fieldPath.func = self.cb_removePathEvent(fieldPath)
            fieldPath.path = path
            self.pathsLays.append(fieldPath)

        @callback
        def cb_getProjectEvent(self, *args):
            path = cmds.workspace( q=True, rootDirectory=True )
            path = os.path.abspath(path)
            if not os.path.isdir(path):
                return
            self.localPath.path = path

        @callback
        def cb_getRelativePathEvent(self, *args):
            '''button action: will set the relative path
            to the value of the absolute filepath minus the local path
            '''
            localPath = self.localPath.path
            filepath = os.path.abspath(cmds.file(q=True, sn=True))
            relativePath = filepath.replace(localPath, "")
            if len(relativePath) > 0:
                if relativePath[0] == "/" or relativePath[0] == "\\":
                    relativePath = relativePath[1:]
            self.relativePath.path = relativePath

        @callback
        def cb_addPathEvent(self, *args):
            path = cmds.fileDialog2(fm=2, cap="Set project on server or hdd")
            if path == None or len(path) < 1:
                return
            path = os.path.abspath(path[0])
            if self.localPath.path == path:
                return
            for pl in self.pathsLays:
                if pl.path == path:
                    return
            self.addPathLay(path)
            self.attachPaths()

            if self.localPath.path in self.savePaths:
                self.savePaths[self.localPath.path].append(path)
            else:
                self.savePaths[self.localPath.path] = [path]
            Publisher.writePref("savePaths", self.savePaths)

        @callback
        def cb_removePathEvent(self, pf, *args):
            '''button action: Will remove the pathField (pf) from the interface
            '''
            self.pathsLays.remove(pf)
            cmds.deleteUI(pf.layout)

            self.attachPaths()
            if self.localPath.path in self.savePaths:
                self.savePaths[self.localPath.path].remove(pf.path)
            Publisher.writePref("savePaths", self.savePaths)

        @callback
        def cb_reloadPathEvent(self, *args):
            
            for pl in self.pathsLays:
                cmds.deleteUI(pl.layout)
            self.pathsLays = []

            if self.localPath.path in self.savePaths:
                for p in self.savePaths[self.localPath.path]:
                    self.addPathLay(p)
            self.attachPaths()

        @callback
        def cb_refreshUI(self):
            self.cb_getProjectEvent()()
            self.cb_getRelativePathEvent()()
            self.cb_reloadPathEvent()()

        def changeColor(self, path, color):
            allpaths = self.pathsLays + [self.relativePath] 
            for fp in allpaths:
                if fp.path == path:
                    fp.color = color
                    break
        
        def getLocalPath(self):
            return self.localPath.path
        def getRelativePath(self):
            return self.relativePath.path
        def getDrivesPath(self):
            if self.localPath.path in self.savePaths:
                return [p for p in self.savePaths[self.localPath.path]]
            return []

        def infoColorPath(self, paths):
            if self.lockColor:
                return
            for path, state in paths:
                color = Publisher.Theme.WARNING if state is None else Publisher.Theme.VALIDATION if state else Publisher.Theme.ERROR
                self.changeColor(path, color)
            self.t_resetColor()

        @thread
        def t_resetColor(self):
            if self.lockColor:
                return
            self.lockColor = True
            fps = 20
            duration = 0.25
            gap = int(fps * duration)

            colorsList = []
            for fp in self.pathsLays:
                colorsList.append([(e-s) / gap for s,e in zip(fp.color[:], Publisher.Theme.SAVE)])
            allpaths = self.pathsLays + [self.relativePath] 
            colorsList.append([(e-s) / gap for s,e in zip(self.relativePath.color[:], Publisher.Theme.RELATIVE)])

            time.sleep(0.5)

            for i in range(0, gap):
                time.sleep(1.0 / fps)
                for fp, colorGap in zip(allpaths, colorsList):
                    fp.color = [n + g for n, g in zip(fp.color, colorGap)]
            self.lockColor = False

        def _loadJobs(self):
            self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", self.cb_refreshUI()]))
            self._scriptJobIndex.append(cmds.scriptJob(event=["SceneSaved", self.cb_refreshUI()]))
            self._scriptJobIndex.append(cmds.scriptJob(event=["workspaceChanged", self.cb_refreshUI()]))

        def load(self):
            self.layout = cmds.formLayout("Paths_lay", parent=self.parent, bgc=Publisher.Theme.SEC_BGC)
 
            # Path layout
            #   local path layout
            self.localPath = Publisher.MC_PathLine(self.layout, color=Publisher.Theme.LOCAL).load()
            self.localPath.func = self.cb_getProjectEvent()
            self.cb_getProjectEvent()()

            if self.localPath.path in self.savePaths:
                for p in self.savePaths[self.localPath.path]:
                    self.addPathLay(p)

            #   add Path Layout
            self.addPath = Publisher.MC_PathLine(self.layout, color=Publisher.Theme.SAVE, image=Publisher.Image.ADD, annotation=Publisher.lg.Button.add).load()
            self.addPath.pathVisibility = False
            self.addPath.func = self.cb_addPathEvent()
            
            #   relative path layout
            self.relativePath = Publisher.MC_PathLine(self.layout, color=Publisher.Theme.RELATIVE).load()
            self.relativePath.func = self.cb_getRelativePathEvent()

            # attach aboves' layout to self.layout
            self.attachPaths()
            self.cb_getProjectEvent()()
            self.cb_getRelativePathEvent()()

    class MC_Tab(Module):
        def __init__(self, parent, name=None, startIndex=0):
            Module.__init__(self, parent)
            self.topTabs = []
            self.botTabs = []
            self.tabsContent = []
            self.tabsButtons = []
            self.activeTab = startIndex
            self.currentTabLay = None
            self.tabDimensions = []
        
        def addTopTabs(self, mod, image, ann=""):
            self.topTabs.append((mod, image, ann))
            return mod
        
        def addBoTTabs(self, mod, image, ann=""):
            self.botTabs.append((mod, image, ann))
            return mod

        @callback
        def cb_resize(self):
            if self.currentTabLay is None:
                return
            if self.tabDimensions[self.activeTab][0] <= cmds.layout(self.scrlLay, q=True, h=True) + 20:
                cmds.formLayout(self.childrenLayout,e=True, h=cmds.scrollLayout(self.scrlLay, q=True, h=True) - 20)
            if self.tabDimensions[self.activeTab][1] <= cmds.layout(self.scrlLay, q=True, w=True) + 5:
                cmds.formLayout(self.childrenLayout,e=True, w=cmds.scrollLayout(self.scrlLay, q=True, w=True) - 5)

        def setActiveTab(self, id):
            self.activeTab = id
            for b, e in zip(self.tabsButtons, self.tabsContent):
                cmds.control(b, e=True, bgc=Publisher.Theme.BUTTON)
                if e is None:
                    continue
                lay = e.layout if isinstance(e, Module) else e
                cmds.layout(lay, e=True, vis=False)
            cmds.control(self.tabsButtons[id], e=True, bgc=Publisher.Theme.SEC_BGC)
            e = self.tabsContent[id]
            if e is None:
                return
            self.currentTabLay = e.layout if isinstance(e, Module) else e
            cmds.control(self.currentTabLay, e=True, vis=True)

        def getActiveTab(self):
            return self.activeTab

        @callback
        def switch(self, id):
            if id == self.activeTab:
                return
            self.setActiveTab(id)

        def load(self):
            self.layout = cmds.formLayout("tab_lay", parent=self.parent, bgc=Publisher.Theme.MAIN_BGC)
            # self.rszLay = self.attach(cmds.scrollLayout("rszLay", parent=self.layout, cr=True), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,2,30,2))
            # self.scrlLay = cmds.scrollLayout("scrlLay", parent=self.rszLay, cr=True, rc=self.cb_resize())
            self.scrlLay = self.attach(cmds.scrollLayout("scrlLay", parent=self.layout, rc=self.cb_resize()), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,2,30,2))
            self.childrenLayout = cmds.formLayout("tab_content",p=self.scrlLay, bgc=Publisher.Theme.SEC_BGC)
            it = 0
            
            prev = "FORM"
            for m, i, a in self.topTabs:
                prev = self.attach(cmds.iconTextButton(image=i, p=self.layout, h=30, w=30, bgc=Publisher.Theme.BUTTON, c=self.switch(it), ann=a), top=prev, bottom=None, left="FORM", right=None, margin=(2,2,2,2))
                self.tabsButtons.append(prev)
                it += 1
                if isinstance(m, Module):
                    m.load()
                if m is None:
                    self.tabsContent.append(None)
                    continue
                self.tabsContent.append(self.attach(m, top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(2,2,2,2)))
                self.tabDimensions.append((cmds.layout(m.layout, q=True, h=True), cmds.layout(m.layout, q=True, w=True)))
            prev = "FORM"
            tmp = 20
            for m, i, a in self.botTabs:
                prev = self.attach(cmds.iconTextButton(image=i, p=self.layout, h=30, w=30, bgc=Publisher.Theme.BUTTON, c=self.switch(it), ann=a), top=None, bottom=prev, left="FORM", right=None, margin=(2,tmp,2,2))
                tmp = 2
                self.tabsButtons.append(prev)
                it += 1
                if isinstance(m, Module):
                    m.load()
                if m is None:
                    self.tabsContent.append(None)
                    continue
                self.tabsContent.append(self.attach(m, top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(2,2,2,2)))
                self.tabDimensions.append((cmds.layout(m.layout, q=True, h=True), cmds.layout(m.layout, q=True, w=True)))
            self.applyAttach()
            self.setActiveTab(self.activeTab)

    class MT_SyncCommon(Module):
        def lockPrepPublish(self, lock):
            cmds.control(self.btn_prep, e=True, en=not lock)
            cmds.control(self.btn_rollBack, e=True, en=lock)

        @callback
        def cb_publishEvent(self):
            msg = cmds.scrollField(self.lay_comment, q=True, tx=True)
            self.runEvent("btn_publish", msg)
            cmds.scrollField(self.lay_comment, e=True, tx="")

        def load(self):
            m = 2
            self.layout = cmds.formLayout(parent=self.parent)

            self.btn_prep = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.CLEAN,      h=30, w=30, bgc=Publisher.Theme.BUTTON,     c=Callback(self.runEvent, "btn_prep"), ann=Publisher.lg.Button.prepare), top="FORM", bottom=None, left="FORM", right=None, margin=(m,m,m,m))
            self.btn_rollBack = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.UNDO,   h=30, w=30, bgc=Publisher.Theme.BUTTON,     c=Callback(self.runEvent, "btn_rollBack"), ann=Publisher.lg.Button.rollback, en=False), top="FORM", bottom=None, left=self.btn_prep, right=None, margin=(m,m,m,m))

            self.btn_backup = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.SAVE,     h=30, w=30, bgc=Publisher.Theme.RELATIVE,   c=Callback(self.runEvent, "btn_backup"), ann=Publisher.lg.Button.backup), top=None, bottom="FORM", left=None, right="FORM", margin=(m,m,m,m))

            self.btn_test = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.CHECK,      h=30, w=30, bgc=Publisher.Theme.RELATIVE,   c=Callback(self.runEvent, "btn_test"), ann=Publisher.lg.Button.check, en=False), top=None, bottom="FORM", left="FORM", right=None, margin=(m,m,m,m))
            self.btn_publish = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.PUBLISH, h=30, w=30, bgc=Publisher.Theme.LOCAL,      c=self.cb_publishEvent(), ann=Publisher.lg.Button.publish), top=None, bottom="FORM", left=self.btn_test , right=None, margin=(m,m,m,m))
            self.btn_upload = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.NETWORK,  h=30, w=30, bgc=Publisher.Theme.SAVE,       c=Callback(self.runEvent, "btn_upload"), ann=Publisher.lg.Button.upload), top=None, bottom="FORM", left=self.btn_publish, right=None, margin=(m,m,m,m))

            self.lab_comment = self.attach(cmds.text(p=self.layout, l=Publisher.lg.Label.comment), top=self.btn_prep, bottom=None, left="FORM", right=None, margin=(m,m,m,m))
            self.lay_stf = self.attach(cmds.formLayout(p=self.layout, w=20, h=10), top=self.lab_comment, bottom=self.btn_test, left="FORM", right="FORM", margin=(m,m,m,m))
            self.lay_comment = self.attach(cmds.scrollField(p=self.lay_stf, editable=True, wordWrap=False, vis=True, fn="smallPlainLabelFont"), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,0,0,0))

            self.applyAttach()

    class MT_SyncAnimation(Module):
        def backupEvent(self, localpath, relativePath, drivesPaths):
            #TODO set the real state of sync by path
            info = [(p, bool(random.randint(0,1))) for p in drivesPaths]
            self.runEvent("outputInfoPath", info)

        def uploadToDriveshEvent(self, localpath, relativePath, drivesPaths):
            #TODO set the real state of sync by path
            info = [(p, bool(random.randint(0,1))) for p in drivesPaths]
            self.runEvent("outputInfoPath", info)

        @callback
        def cb_confoEvent(self):
            msg = cmds.scrollField(self.lay_comment, q=True, tx=True)
            self.runEvent("btn_publish", msg)
            cmds.scrollField(self.lay_comment, e=True, tx="")

        def load(self):
            m = 2
            self.layout = cmds.formLayout(parent=self.parent)

            self.btn_backup   = self.attach(cmds.iconTextButton(image=Publisher.Image.SAVE, h=30, w=30, bgc=Publisher.Theme.RELATIVE, c=Callback(self.runEvent, "btn_backup"), ann="Backup current WIP to drives"), top=None, bottom="FORM", left=None, right="FORM", margin=(m,m,m,m))

            self.btn_publish  = self.attach(cmds.iconTextButton(image=Publisher.Image.PUBLISH, h=30, w=30, bgc=Publisher.Theme.LOCAL, c=self.cb_confoEvent(), ann="Confo"), top=None, bottom="FORM", left="FORM" , right=None, margin=(m,m,m,m))
            self.btn_upload   = self.attach(cmds.iconTextButton(image=Publisher.Image.NETWORK, h=30, w=30, bgc=Publisher.Theme.SAVE, c=Callback(self.runEvent, "btn_upload"), ann="Upload to drives"), top=None, bottom="FORM", left=self.btn_publish, right=None, margin=(m,m,m,m))

            self.lab_comment  = self.attach(cmds.text(l="Commentaire : "), top="FORM", bottom=None, left="FORM", right=None, margin=(m,m,m,m))
            self.lay_comment = self.attach(cmds.scrollField(p=self.layout, editable=True, wordWrap=True, w=5), top=self.lab_comment, bottom=self.btn_publish, left="FORM", right="FORM", margin=(m,m,m,m))

            self.applyAttach()

    class MC_SettingSection(Module):
        def __init__(self, parent, name):
            Module.__init__(self, parent)
            self.name = name

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            self.title = self.attach(cmds.text(l=self.name), top="FORM", left="FORM")
            self.separator = self.attach(cmds.separator( height=10, style='in' ), top="FORM", left=self.title, right="FORM", margin=(3,3,15,3))
            self.childrenLayout = self.attach(cmds.formLayout(parent=self.layout, bgc=Publisher.Theme.MAIN_BGC, h=50), top=self.title, left="FORM", right="FORM", margin=(3,3,25,3))


            self.applyAttach()

    class MT_SettingLanguage(Module):
        @callback
        def cb_changeLanguage(self, lg):
            print(lg)

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            self.btn_En = self.attach(cmds.button(p=self.layout, l="En", c=self.cb_changeLanguage("En")), top="FORM", left="FORM", margin=(3,3,3,3))
            self.btn_Fr = self.attach(cmds.button(p=self.layout, l="Fr", c=self.cb_changeLanguage("Fr")), top="FORM", left=self.btn_En, margin=(3,3,3,3))
            self.btn_folder = self.attach(cmds.iconTextButton(image=Publisher.Image.FOLDER, h=30, w=30, bgc=Publisher.Theme.BUTTON, c=Callback(self.runEvent, "btn_upload"), ann="Upload to drives"), top="FORM", right="FORM", margin=(3,3,3,3))
            self.applyAttach()

    class MT_Settings(Module):
        def __init__(self, parent):
            Module.__init__(self, parent)
            self.section = {}

        @callback
        def cb_switchToEnglish(self):
            Publisher.lg = Publisher.Language.En if Publisher.lg == Publisher.Language.Fr else Publisher.Language.Fr
            Publisher().reload()
            Publisher.writePref("lg", Publisher.lg.__name__)

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            self.tmp = self.attach(cmds.text(p=self.layout, l="WIP"), top="FORM", left="FORM")
            self.btn = self.attach(cmds.button(p=self.layout, l="switch To English", c=self.cb_switchToEnglish()), top=self.tmp, left="FORM", margin=(3,3,3,3))
            self.section["language"] = self.attach(Publisher.MC_SettingSection(self.layout, "Language").load(), top=self.btn, left="FORM", right="FORM", margin=(3,3,3,3))
            self.section["nameDef"] = self.attach(Publisher.MC_SettingSection(self.layout, "Publish/Version name definition").load(), top=self.btn, left="FORM", right="FORM", margin=(3,3,3,3))
            self.section["test"] = self.attach(Publisher.MC_SettingSection(self.layout, "Test Definition").load(), top=self.btn, left="FORM", right="FORM", margin=(3,3,3,3))
            self.applyAttach()

    class MT_info(Module):
        style = """
            <style>
            *        {{text-align: left;}}
            .local   {{background-color: {THEME_RELATIVE}; color:{COLOR_BLACK}}}
            .publish {{background-color: {THEME_LOCAL}; color:{COLOR_BLACK}}}
            .drives  {{background-color: {THEME_SAVE}; color:{COLOR_BLACK}}}
            .button  {{background-color: {THEME_BUTTON};}}
            ul       {{margin-left&#58; 30px;}}
            img      {{width: 30; height:30;}}
            p        {{margin-left&#58; 30px;}}
            </style>
        """
        @callback
        def openTicket(self):
            subject = "[Ticket] // {} v{}// ...".format(str(Publisher().__class__.__name__), __version__)
            subject = urllib.quote_plus(subject)
            body = r"Your message here%0D%0AChange the ... in the subject to the name of the issue%0D%0ABe precise, short and nice"
            # body = "%0D%0A".join(body.splitlines())
            webbrowser.open("mailto:{}?subject={}&body={}".format(__email__, subject, body))

        __iconsPath = os.path.expanduser('~/') + "maya/2020/prefs/icons/default/"
        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            self.scrlLay = self.attach(cmds.scrollLayout("scrlLay", parent=self.layout, cr=True), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,0,0,0))
            self.childrenLayout = cmds.formLayout(parent=self.scrlLay)
            # self.childrenLayout = cmds.formLayout(parent=self.scrlLay)
            # for img in Publisher.__dir__
            themes = {"THEME_{}".format(c):'#%02x%02x%02x' % (getattr(Publisher.Theme, c)[0] * 255, getattr(Publisher.Theme, c)[1] * 255, getattr(Publisher.Theme, c)[2] * 255) for c in dir(Publisher.Theme) if c.isupper()}
            colors = {c:'#%02x%02x%02x' % (getattr(Publisher, c)[0] * 255, getattr(Publisher, c)[1] * 255, getattr(Publisher, c)[2] * 255) for c in dir(Publisher) if c.startswith("COLOR_")}
            images = {i:getattr(Publisher.Image, i) for i in dir(Publisher.Image) if i.isupper()}
            if not os.path.exists(self.__iconsPath):
                os.makedirs(self.__iconsPath)
            for name, path in images.items():
                if not os.path.exists(os.path.join(self.__iconsPath, path)):
                    cmds.resourceManager(s=(path, os.path.join(self.__iconsPath, path)))
            images = {"IMAGE_{}".format(i):os.path.join(self.__iconsPath, getattr(Publisher.Image, i)) for i in dir(Publisher.Image) if i.isupper()}
            info = {
                "NAME": str(Publisher().__class__.__name__),
                "AUTHOR": __author__,
                "EMAIL": __email__,
                "VERSION": __version__,
                "COPYRIGHT": __copyright__,
                }
            context = dict(themes)
            context.update(colors)
            context.update(images)
            context.update(info)
            # modules = [Publisher.MT_Paths, Publisher.MT_SyncCommon, Publisher.MT_SyncAnimation, Publisher.MT_Settings]
            # txt = self.style + Publisher.lg.About.Publisher + "".join([m.__doc__ for m in modules if m is not None and m.__doc__ is not None])
            abouts_name = ["PUBLISHER", "PATHS", "SYNCCOMMON", "SYNCANIMATION", "SETTINGS"]
            # abouts = [getattr(Publisher.lg.About, a) for a in dir(Publisher.lg.About) if a.isupper()]
            abouts = [getattr(Publisher.lg.About, a) for a in abouts_name]
            txt = self.style + "".join(abouts)
            txt = txt.format(**context)
            # for t in txt.splitlines():
            #     print(str(t))


            # txt = bytes(str(t).encode("utf-8"))
            prev = "FORM"
            prev = self.attach(cmds.text(p=self.childrenLayout, l=txt), top=prev, bottom=None, left="FORM", right="FORM", margin=(1,1,1,1))
            self.btn_ticket = self.attach(cmds.button(l=Publisher.lg.Button.ticket, c=self.openTicket()), top=prev, bottom=None, left="FORM", right=None, margin=(1,1,1,1))
            with io.open(os.path.join(self.__iconsPath, "test.html"), "w+", encoding="utf-8") as f:
                f.write(txt)
            self.applyAttach()

    class Sync():
        def __init__(self, pathsModule):
            self.pathsModule = pathsModule
            self.wipRollback = None
            self.command = {}

            self.datas = {}
            self.datas["PublisherVersion"] = "{}".format(__version__)

            self.datas["Comment"] = None
            self.datas["Author"] = None
            self.datas["Computer"] = None
            self.datas["Date"] = None
            self.datas["Version"] = None

        # Events
        def eventHandler(self, event, c, *args):
            if not event in self.command:
                self.command[event] = []
            self.command[event].append((c, args))
        def runEvent(self, event, *args):
            if not event in self.command:
                return
            for c in self.command[event]:
                if c[0] is None:
                    continue
                a = c[1] + args
                c[0](*a)

        def backup(self):
            print("backup")
            
            localPath = self.pathsModule.getLocalPath()
            relativePath = self.pathsModule.getRelativePath()
            drives = self.pathsModule.getDrivesPath()
            infos = []
            print(drives)
            for drive in drives:
                abs_path = os.path.join(drive, relativePath)
                if abs_path == relativePath:
                    infos.append((relativePath, False)) if (relativePath, False) not in infos else None
                    continue
                driveDir = os.path.dirname(abs_path)
                print(driveDir)
                if not os.path.exists(drive):
                    infos.append((drive, False))
                    continue
                if not os.path.exists(driveDir):
                    os.makedirs(driveDir)
                state = None if os.path.exists(os.path.join(drive, relativePath)) else True
                shutil.copy(os.path.join(localPath, relativePath), os.path.join(drive, relativePath))
                infos.append((drive, state))
            print(infos)
            self.pathsModule.infoColorPath(infos)

        def upload(self):
            info = [(p, bool(random.randint(0,1))) for p in self.pathsModule.getDrivesPath()]
            self.pathsModule.infoColorPath(info)

        def publish(self, comment):
            
            localPath = self.pathsModule.getLocalPath()
            relativePath = self.pathsModule.getRelativePath()
            paths, names = self.getPathsAndNames()
            
            # Prepare meta-data
            self.datas["Comment"] = comment
            self.setDatas()
            self.prepPublish()
            self.writeMetadata()
            cmds.file( save=True, type='mayaAscii' )

            # Check if it's a wip
            if os.path.normpath(relativePath).split(os.sep)[-2] != "wip":
                cmds.warning("The current file is not a WIP")
                return

            # create a version folder if not existing
            if not os.path.exists(os.path.join(localPath, paths["version"])):
                os.makedirs(os.path.join(localPath, paths["version"]))

            # Screenshot
            image = self.takeSnapshot()
            shutil.copy(image, os.path.join(localPath, paths["publish"], names["imgPublish"]))
            shutil.copy(image, os.path.join(localPath, paths["version"], names["imgVersion"]))

            # Publish
            print(os.path.join(localPath, relativePath))
            print(self.pubPath)
            shutil.copy(self.pubPath, os.path.join(localPath, paths["version"], names["version"]))
            shutil.copy(self.pubPath, os.path.join(localPath, paths["publish"], names["publish"]))


            # Rollback wip and increment its version
            if self.wipRollback is not None:
                cmds.file(self.wipRollback, o=True, f=True)
            self.wipRollback = None 
            cmds.file(rename="/".join([localPath, paths["wip"], names["incWip"]]))
            cmds.file(save=True, type='mayaAscii' )
            self.runEvent("lockPrepPublish", False)
            info("{} -> Published !".format(names["publish"]))
            print("Publish", comment)

        def confo(self, comment):
            self.datas["Comment"] = comment
            print("confo", comment)

        def prepPublish(self):
            # increment and save
            mel.eval("incrementAndSaveScene 1;")
            
            # store current file
            self.wipRollback = os.path.abspath(cmds.file(q=True, sn=True))
            self.pubPath = self.wipRollback[:-3] + ".pub" + self.wipRollback[-3:]
            cmds.file(rename=self.pubPath)
            cmds.file(save=True, type='mayaAscii')
            self.runEvent("lockPrepPublish", True)

        def rollBack(self):
            if self.wipRollback is None:
                return
            cmds.file(self.wipRollback, o=True, f=True)
            self.runEvent("lockPrepPublish", False)
            self.wipRollback = None

        def cleanStudent(self):
            print("cleanStudent")

        def runTest(self):
            print("runTest")

        def writeMetadata(self):
            if cmds.objExists("publisher_metadata"):
                return
            node = cmds.createNode('partition', n='publisher_metadata')

            for k, v in self.datas.items():
                print(k,v)
                cmds.addAttr(node, longName=k, dataType="string")
                cmds.setAttr("publisher_metadata.{}".format(k), str(v), type="string")

        def setDatas(self):
            self.datas["Author"] = getpass.getuser()
            self.datas["Computer"] = os.environ['COMPUTERNAME']
            self.datas["Date"] = datetime.now().strftime("%H:%M:%S")

        def getPathsAndNames(self):
            relativePath = self.pathsModule.getRelativePath()
            paths = {}
            names = {}

            paths["wip"], names["wip"] = os.path.split(relativePath)
            paths["publish"], _ = os.path.split(paths["wip"])
            paths["version"]= os.path.join(paths["publish"], "versions")
            nVersion = Publisher.Sync.getVersionFromName(names["wip"])

            self.datas["Version"] = nVersion
            
            fileName = "_".join(names["wip"].split(".")[0].split("_")[:-1])
            names["publish"] = fileName + "." + names["wip"].split(".")[-1]
            names["version"] = fileName + "_v{0:0>3d}.".format(nVersion) + names["wip"].split(".")[-1]
            names["incWip"] = fileName + "_v{0:0>3d}.0001.ma".format(nVersion + 1)
            names["imgPublish"] = "thumbnail.jpg"
            names["imgVersion"] = "thumbnail_v{0:0>3d}.jpg".format(nVersion)

            return (paths, names)

        def takeSnapshot(self, name="tmp", width=1920, height=1080):
            imagePath = "/".join([self.pathsModule.getLocalPath(), "images", name + ".jpg"])
            frame = cmds.currentTime( query=True )
            cmds.playblast(fr=frame, v=False, fmt="image", c="jpg", orn=False, cf=imagePath, wh=[width,height], p=100)
            return imagePath

        @staticmethod
        def getVersionFromName(name):
            n = name.split(".")
            if n == None or len(n) < 1:
                return 1
            n = n[0]
            n = re.findall('_v[0-9]{3}', n)[0].replace("_v", "")
            return int(n)

        @staticmethod
        def getLastVersion(path):
            i = 0
            if os.path.isdir(path + "/versions"):
                versions = os.listdir(path + "/versions")
                for v in versions:
                    j = re.findall('[0-9]{3}', v)
                    if len(j) == 1:
                        i = max(int(j[0]), i)
            return i

    def __init__(self):
        Module.__init__(self, None)
        self.name = "{} V{}".format(str(self.__class__.__name__), __version__)
        Publisher.lg = Publisher.Language.getLg(Publisher.readPref("lg"))
        if self.lg is None:
            Publisher.lg = Publisher.Language.Fr
            Publisher.writePref("lg", Publisher.lg.__name__)

    def load(self):
        '''loading The window
        '''
        # Creating Windows if not exist or reload it
        if cmds.workspaceControl(self.name, exists=1):
            cmds.deleteUI(self.name)
        self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)
        self.layout = cmds.formLayout("Publisher_layout",parent=self.win)
        self.childrenLayout = self.attach(cmds.formLayout("Publisher_childLay", parent=self.layout), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,0,0,0))

        # Main Pannels
        self.paths = self.attach(Publisher.MT_Paths(self).load(), top="FORM", bottom=None, left="FORM", right="FORM", margin=(2,2,2,2))        
        #   Active Tab
        ct = self.readPref("currentTab")
        self.tabs = Publisher.MC_Tab(self, startIndex=ct if type(ct) is int else 0)

        # Tabs definitions 
        #   Attach up
        self.SyncCommon = self.tabs.addTopTabs(Publisher.MT_SyncCommon(self.tabs), Publisher.Image.COMMON, Publisher.lg.Button.common)
        self.SyncAnimation = self.tabs.addTopTabs(Publisher.MT_SyncAnimation(self.tabs), Publisher.Image.ANIMATION, Publisher.lg.Button.animation)
        #   Attach bot
        self.tabs.addBoTTabs(Publisher.MT_info(self.tabs), Publisher.Image.HELP, Publisher.lg.Button.about)
        self.tabs.addBoTTabs(Publisher.MT_Settings(self.tabs), Publisher.Image.SETTING, Publisher.lg.Button.settings)
        # Loading tabs
        self.tabs.load()

        self.syncEvent = Publisher.Sync(self.paths)
        # Events
        #   Sync
        self.syncEvent.eventHandler("lockPrepPublish", self.SyncCommon.lockPrepPublish)
        #   Common sync 
        self.SyncCommon.eventHandler("btn_prep", self.syncEvent.prepPublish)
        self.SyncCommon.eventHandler("btn_rollBack", self.syncEvent.rollBack)
        self.SyncCommon.eventHandler("btn_backup", self.syncEvent.backup)
        self.SyncCommon.eventHandler("btn_test", self.syncEvent.runTest)
        self.SyncCommon.eventHandler("btn_publish", self.syncEvent.publish)
        self.SyncCommon.eventHandler("btn_upload", self.syncEvent.upload)

        #   Anim sync
        self.SyncAnimation.eventHandler("btn_backup", self.syncEvent.backup)
        self.SyncAnimation.eventHandler("btn_publish", self.syncEvent.confo)
        self.SyncAnimation.eventHandler("btn_upload", self.syncEvent.upload)

        self.attach(self.tabs, top=self.paths, bottom="FORM", left="FORM", right="FORM", margin=(2,2,2,2))

        self.applyAttach()
        info("[{}] -> loaded!".format(self.name))
        return self

    def _unload(self):
        if self.win == None:
            return self
        if cmds.workspaceControl(self.win, exists=1):
            cmds.deleteUI(self.win)
        return self
    def unloadEvent(self):
        self.writePref("currentTab", self.tabs.getActiveTab())
        return self

if __name__ == "__main__":
    if sys.executable.endswith(u"bin\maya.exe"):
        Publisher().load()
    else:
        ctypes.windll.user32.MessageBoxW(0, "Version : {}\n\nJust drag&drop this file to maya's viewport\n\n{}".format(__version__, __doc__), "{} info".format(__file__), 0)

def onMayaDroppedPythonFile(*args):
    '''Just to get rid of the anoying warning message of maya
    '''
    Publisher().load()

def initializePlugin(*args):
    '''To load the tool as a plugin
    '''
    Publisher().load()

def uninitializePlugin(*args):
    Publisher().unload()
