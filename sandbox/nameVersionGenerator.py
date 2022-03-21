# -- coding: utf-8 --
#!/usr/bin/env python


"""nameVersionGenerator.py: A little tool to help syncronise maya file for a CreativeSeeds pipeline"""

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
import re
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
    COLOR_DARKESTGREY = [0.16, 0.16, 0.16]
    COLOR_DARKGREY = [0.21, 0.21, 0.21]
    COLOR_GREY = [0.26, 0.26, 0.26]
    COLOR_LIGHTGREY = [0.36, 0.36, 0.36]
    COLOR_GREEN = [0.48, 0.67, 0.27]
    COLOR_RED = [0.85, 0.34, 0.34]
    COLOR_YELLOW = [0.86,0.81,0.53]
    COLOR_LIGHTGREYGREEN = [0.42, 0.51, 0.49]
    COLOR_LIGHTGREYBLUE = [0.39, 0.47, 0.54]
    COLOR_LIGHTGREYRED = [0.51, 0.42, 0.42]

    increment = 0
    drag = None

    def __init__(self, parent, name=None):

        Module.increment += 1
        self.increment = Module.increment
        if name is None:
            name = self.__class__.__name__ + str(Module.increment)
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
        self.an = []

    def __str__(self):
        return str(self.childrenLayout)

    def __getattribute__(self, name):
        if name == 'load':
            return object.__getattribute__(self, "_load")
        if name == 'unload':
            return object.__getattribute__(self, "_unload")
        if name == "height":
            if self.layout is not None:
                return cmds.layout(self.layout, q=True, h=True)
            else:
                 return 0
        if name == "width":
            if self.layout is not None:
                return cmds.layout(self.layout, q=True, w=True)
            else:
                 return 0
        return object.__getattribute__(self, name)

    def setParent(self, parent):
        if self.parent is not None:
            if isinstance(self.parent, Module):
                self.parent.childrens.remove(self)
        self.parent = parent
        if isinstance(self.parent, Module):
            self.parent.childrens.append(self)

    def attach(self, elem, top=False, bottom=False, left=False, right=False, margin=(0,0,0,0)):
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
            if s is False:
                continue
            if s is None:
                self.an.append((e, n))
            if s is True:
                self.af.append((e, n, m))
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
        self.an = []

    @staticmethod
    def _getParentLayout(attachList):
        parLayout = {}
        for af in attachList:
            e = af[0]
            if isinstance(e, Module):
                parLayout[e.parent] = [af] if e.parent not in parLayout else parLayout[e.parent] + [af]
            elif e is None:
                continue
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
        parLayoutAn = Module._getParentLayout(self.an)
        parentlayouts = parLayoutAf.keys() + parLayoutAc.keys() + parLayoutAp.keys() + parLayoutAn.keys()
        parentlayouts = list(dict.fromkeys(parentlayouts))
        for pl in parentlayouts:
            af = parLayoutAf[pl] if pl in parLayoutAf else []
            ac = parLayoutAc[pl] if pl in parLayoutAc else []
            ap = parLayoutAp[pl] if pl in parLayoutAp else []
            an = parLayoutAn[pl] if pl in parLayoutAn else []
            try:
                cmds.formLayout(pl, e=True, af=af, ac=ac, ap=ap, an=an)
            except Exception as inst:
                print(inst)
                raise Exception("Can't attach {} {}".format(pl, inst))

    def _load(self):
        # Create a workspaceControl if there is no parent
        par = self.parent
        if self.parent == None:
            if cmds.workspaceControl(self.name, exists=1):
                cmds.deleteUI(self.name)
            self.win = cmds.workspaceControl(self.name, ih=100, iw=500, retain=False, floating=True, h=100, w=500)
            par = self.win

        # Create Default layout and ChildrenLayout
        self.layout = cmds.formLayout(parent=par)
        self.childrenLayout = cmds.formLayout(p=self.layout)
        defaultLayout = self.layout
        defaultChildrenLay = self.childrenLayout

        # Execute The function develope by the user
        object.__getattribute__(self, "load")()

        # Delete Default Layout & ChildrenLayout if not used
        if self.childrenLayout != defaultChildrenLay:
            if cmds.layout(defaultChildrenLay, q=True, ex=True):
                cmds.deleteUI(defaultChildrenLay)
        else:
            self.attach(self.childrenLayout, top=True, bottom=True, left=True, right=True)

        if self.layout != defaultLayout:
            if cmds.layout(defaultLayout, q=True, ex=True):
                cmds.deleteUI(defaultLayout)

        # Apply Attach to the form Layout
        self.applyAttach()

        # log UnloadEvent
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self.unloadEvent)])

        # manage ScriptJob events
        cmds.scriptJob(ro=True, uid=[self.layout, Callback(self._killJobs)])
        self._loadJobs()

        # so the function load() can be callable
        return self

    def load(self):
        ''' Put your main layout in the self.layout
        If you use a formeLayout use self.attach()
        Put the layout where the childrens will go in self.childrenLayout
        '''
        # raise Exception('load function not implemented')

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
        pass
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

class Preferences():
    class Theme():
        SAVE = Module.COLOR_BLUE
        SELECTED = Module.COLOR_BLUE
        LOCAL = Module.COLOR_TURQUOISE
        RELATIVE = Module.COLOR_ORANGE
        MAIN_BGC = Module.COLOR_GREY
        SEC_BGC = Module.COLOR_DARKGREY
        THD_BGC = Module.COLOR_DARKESTGREY
        BUTTON = Module.COLOR_LIGHTGREY
        VALIDATION = Module.COLOR_GREEN
        ERROR = Module.COLOR_RED
        WARNING = Module.COLOR_YELLOW

    class Image():
        ADD = "QR_add.png"
        ANIMATION = "animateSnapshot.png"
        DELETE = "deleteClip.png"
        CHECK = "SP_FileDialogContentsView.png"
        CLEAN = "brush.png"
        COMMON = "volumeCube.png"
        FOLDER = "fileOpen.png"
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
        QUIT = "SP_TitleBarCloseButton.png"
        LEFTARROW = "tabs_scroll_left.png"
        RIGHTARROW = "tabs_scroll_right.png"

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
                install = "Install"
                uninstall = "Uninstall"
                loadLanguage = "Install a language"

            class Label():
                comment = "Comments : "
                language = "Language"
                nameConv = "Publication's paths definitions"
                TestDef = "Test definition"
                loadSavePref = "Load/Save Preferences"
                plugin = "Install Plug-in"
                colorTheme = "Color Theme"

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
                upload = u"Télécharger votre publication ainsi que \nla dernière version vers vos périphérique de sauvegarde"
                confo = u"Confo"
                ticket = u"Ouvrir un ticket"
                delete = u"Supprimer"
                add = u"Ajouter"
                common = u"Commun"
                animation = u"Animation"
                about = u"À propos"
                settings = u"Paramètre"
                install = u"Installer"
                uninstall = u"Désinstaller"
                loadLanguage = "Installer une langue"

            class Label():
                comment = u"Commentaires : "
                language = u"Langues"
                nameConv = u"Définition des chemins de publication"
                TestDef = u"Définition des test"
                loadSavePref = u"Charger/Sauvegarder les préférences"
                plugin = u"Installer le Plug-in"
                colorTheme = u"Thème de couleur"

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
                return Preference.Language.Fr
            if name.upper() == "EN":
                return Preference.Language.En

    lg = Language.Fr


class MC_NameDefinition(Module):
    def __init__(self, parent, name, lst):
        Module.__init__(self, parent, name)
        self.list = lst

    @callback
    def cb_remove(self, elem):
        print("removing {}".format(elem))

    def load(self):
        self.layout = cmds.formLayout(parent=self.parent, bgc=Preference.Theme.THD_BGC)

        self.title = self.attach(cmds.text(p=self.layout, l="{} : ".format(self.name.capitalize())), top="FORM", left="FORM", margin=(3,3,5,3))
        self.containerVar = MC_stackContainer(self.layout)
        for e in self.list:
            label = MC_Label(self.containerVar, str(e[0]), bgc=e[1])
            label.eventHandler("remove", self.cb_remove(str(e[0])))
        MC_AddOption(self.containerVar, options=["project", "path", "name", "state", "version", "extension", "_", ".", "v", "\\"])
        self.containerVar.load()
        self.attach(self.containerVar, top=self.title, left="FORM", right="FORM", margin=(3,3,15,5))
        self.attach(cmds.formLayout(p=self.layout, h=5), top=self.containerVar, left="FORM", right="FORM")

class MT_SettingsNameConvertion(Module):

    NAME_DEFAULT_EMPTY = {}
    VAR_DEFAULT_CS = {
                "project" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 0]],
                "path" : [[False, "str", "\\wip", -1]],
                "name" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 1]],
                "state" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 2]],
                "version" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 3], [True, "alphaNum", None, -1]],
                "extension" : [[True, "str", "\\", -1], [True, "str", ".", -1]],
                "_" : [],
                "." : [],
                "v" : [],
                "\\" : [],
        }
    VAR_DEFAULT_CUSTOM = {
                "project" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 0]],
                "path" : [[False, "str", "\\wip", -1]],
                "name" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 1]],
                "state" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 3]],
                "version" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 3], [True, "alphaNum", None, -1]],
                "extension" : [[True, "str", "\\", -1], [True, "str", ".", -1]],
                "type" : [[True, "str", "wip", -1], [True, "str", ".", 0], [True, "str", "_", 2]],
                "_" : [],
                "." : [],
                "v" : [],
                "\\" : [],
        }

    NAME_DEFAULT_EMPTY = [
            ("Publish", []),
            ("Publish Image", []),
            ("Version", []),
            ("Version Image", []),
            ("Confo", []),
            ("Confo image", [])
    ]
    NAME_DEFAULT_CS = [
            ("Publish", ["path", "\\", "project", "_", "name", "_", "state", ".", "extension"]),
            ("Publish Image", ["path", "\\", "project", "_", "name", "_", "state", "_", "thumbnail", ".", "jpg"]),
            ("Version", ["path", "\\", "versionPath", "\\", "project", "_", "name", "_", "state", "_", "v", "version", ".", "extension"]),
            ("Version Image", ["path", "\\", "versionPath", "\\", "project", "_", "name", "_", "state", "_", "v", "version", "_", "thumbnail", ".", "jpg"]),
            ("Confo", ["path", "\\", "project", "_", "name", "_", "state", "_", ".", "extension"]),
            ("Confo image", ["path", "\\", "project", "_", "name", "_", "state", "_", "thumbnail", ".", "jpg"])
        ]
    NAME_DEFAULT_CUSTOM = [
            ("Publish", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", ".", "extension"]),
            ("Publish Image", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", "_", "thumbnail", ".", "jpg"]),
            ("Version", ["path", "\\", "versionPath", "\\", "project", "_", "type", "_", "name", "_", "state", "_", "v", "version", ".", "extension"]),
            ("Version Image", ["path", "\\", "versionPath", "\\", "project", "_", "type", "_", "name", "_", "state", "_", "v", "version", "_", "thumbnail", ".", "jpg"]),
            ("Confo", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", "_", ".", "extension"]),
            ("Confo image", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", "_", "thumbnail", ".", "jpg"])
        ]

    def __init__(self, parent):
        Module.__init__(self, parent)
        self.example = lambda: "Y a rien"
        self.variables = MT_SettingsNameConvertion.VAR_DEFAULT_CS

    @callback
    def cb_editLabel(self, name=None):
        print("edit {}".format(name))
        if name is None:
            MC_VariableEditor("", [], self.example()).load()
        else:
            MC_VariableEditor(name, self.variables[name], self.example()).load()

    @callback
    def cb_deleteLabel(self, name=None):
        print("delete {}".format(name))
        if name in self.variables:
            pass
            # self.variables.pop(name)



    ## TODO Not a good solution
    ## ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
    @callback
    def cb_switchNamesDefs(self, name):
        if name == "-":
            self.loadNameDefinitions(MT_SettingsNameConvertion.NAME_DEFAULT_EMPTY)
        elif name == "Custom":
            self.loadNameDefinitions(MT_SettingsNameConvertion.NAME_DEFAULT_CUSTOM)
        elif name == "CS":
            self.loadNameDefinitions(MT_SettingsNameConvertion.NAME_DEFAULT_CS)


    def loadNameDefinitions(self, names):
        prev = self.presetDefineNamesDropMenu
        for n in names:
            buttons = [(x, Module.COLOR_LIGHTGREYRED if not x in self.variables else Module.COLOR_LIGHTGREYBLUE if len(self.variables[x]) == 0 else Preference.Theme.BUTTON) for x in n[1]]
            prev = self.attach(MC_NameDefinition(self.layout, n[0], buttons).load(), top=prev, left="FORM", right="FORM", margin=(8,8,8,8))

    ## ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

    def load(self):
        self.layout = cmds.formLayout(parent=self.parent)

        self.titleDefineVar = self.attach(cmds.text(p=self.layout, l="Define Variables"), top="FORM", left="FORM", margin=(3,3,0,3))
        self.presetDropMenu = self.attach(cmds.optionMenu(p=self.layout, l="Presets : ", bgc=Preference.Theme.BUTTON), top=self.titleDefineVar, left="FORM", margin=(3,3,0,3))
        cmds.menuItem(p=self.presetDropMenu, label='-')
        cmds.menuItem(p=self.presetDropMenu, label='Custom')
        cmds.menuItem(p=self.presetDropMenu, label='CS')
        self.loadPresetBtn = self.attach(cmds.iconTextButton(p=self.layout, i=Preference.Image.FOLDER, bgc=Preference.Theme.BUTTON), top=self.titleDefineVar, right="FORM", margin=(3,3,3,3))
        self.savePresetBtn = self.attach(cmds.iconTextButton(p=self.layout, i=Preference.Image.SAVE, bgc=Preference.Theme.BUTTON), top=self.titleDefineVar, right=self.loadPresetBtn, margin=(3,3,3,3))
        self.versionLabel = self.attach(cmds.text(p=self.layout, l=u"N° de version"), top=self.presetDropMenu, left="FORM", margin=(8,3,3,3))
        self.versiondefineBtn = self.attach(cmds.button(p=self.layout, l=u"Définir", bgc=Preference.Theme.BUTTON, c=self.cb_editLabel("version")), top=self.presetDropMenu, left=self.versionLabel, margin=(3,3,3,3))
        self.nbDigits = self.attach(cmds.intField(p=self.layout, v=3), top=self.presetDropMenu, left=self.versiondefineBtn, margin=(3,3,3,3))


        self.containerAllVar = MC_stackContainer(self.layout)
        for e in self.variables:
            print(e, self.variables[e])
            bgc = Preference.Theme.BUTTON if len(self.variables[e]) > 0 else Module.COLOR_LIGHTGREYBLUE
            label = MC_Label(self.containerAllVar, e, button=True, bgc=bgc)
            label.eventHandler("click", self.cb_editLabel(e))
            label.eventHandler("remove", self.cb_deleteLabel(e))
        MC_AddOption(self.containerAllVar)
        self.containerAllVar.load()
        # self.attach(cmds.iconTextButton(i=Preference.Image.ADD, c=self.cb_editLabel(), p=self.containerAllVar))
        # cmds.iconTextButton(p=self.containerAllVar, image=Preference.Image.ADD, h=18, w=18, bgc=Preference.Theme.BUTTON, c=self.cb_editLabel())
        self.attach(self.containerAllVar, top=self.nbDigits, left="FORM", right="FORM", margin=(15,3,3,3))


        self.titleDefineNames = self.attach(cmds.text(p=self.layout, l="Define names"), top=self.containerAllVar, left="FORM", margin=(3,3,0,3))
        self.presetDefineNamesDropMenu = self.attach(cmds.optionMenu(p=self.layout, l="Presets : ", bgc=Preference.Theme.BUTTON), top=self.titleDefineNames, left="FORM", margin=(3,3,0,3))
        cmds.menuItem(p=self.presetDefineNamesDropMenu, label='-')
        cmds.menuItem(p=self.presetDefineNamesDropMenu, label='Custom')
        cmds.menuItem(p=self.presetDefineNamesDropMenu, label='CS')

        self.loadNameDefinitions(MT_SettingsNameConvertion.NAME_DEFAULT_CS)
