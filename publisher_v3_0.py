# -- coding: utf-8 --
#!/usr/bin/env python


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
import subprocess
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

def Info(message):
    mel.eval('trace -where ""; print "{}\\n"; trace -where "";'.format(message))

def threadPrint(message):
    time.sleep(0.001)
    print(message)

def threadTitle(message, type_=0):
    if type_ == 1:
        gap = 20
        horz = u"═"
        vert = u"║"
        ctl = u"╔"
        ctr = u"╗"
        cbl = u"╚"
        cbr = u"╝"
    else:
        gap = 10
        horz = u"─"
        vert = u"│"
        ctl = u"┌"
        ctr = u"┐"
        cbl = u"└"
        cbr = u"┘"
        

    # threadPrint("")
    threadPrint("")
    threadPrint(u" " * gap + ctl + horz * len(message) + ctr)
    threadPrint(u" " * gap + vert + unicode(message) + vert)
    threadPrint(u" " * gap + cbl + horz * len(message) + cbr)
    # threadPrint("")


# @singleton
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
                revealExplorer = u"Reveal in file explorer" 

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
                loadLanguage = u"Installer une langue"
                revealExplorer = u"Afficher dans l'explorateur de fichier" 

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
                        <h1 style="background-color:{THEME_MAIN_BGC}; font-size:0.5%; color:{THEME_SAVE};text-align: left;">{NAME} </h1>
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

    LG = Language.Fr
    IMG = Image
    THM = Theme

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

        def getPath(self):
            print("path line", self.path)
            return self.path

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
            fieldPath.annotation = Publisher.LG.Button.delete
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

            # import maya.api.OpenMaya as om
            # print(om.MFileObject.expandedPath())

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
            # cmds.warning("test")
            time.sleep(1)
            if self.lockColor:
                return
            self.lockColor = True
            fps = 18
            duration = 0.3
            gap = int(fps * duration)

            colorsList = []
            for fp in self.pathsLays:
                colorsList.append([(e-s) / gap for s,e in zip(fp.color[:], Publisher.Theme.SAVE)])
            allpaths = self.pathsLays + [self.relativePath]
            colorsList.append([(e-s) / gap for s,e in zip(self.relativePath.color[:], Publisher.Theme.RELATIVE)])

            time.sleep(0.5)
            try:
                for i in range(0, gap):
                    time.sleep(1.0 / fps)
                    for fp, colorGap in zip(allpaths, colorsList):
                        fp.color = [n + g for n, g in zip(fp.color, colorGap)]
            except:
                print("error avoided")
                cmds.warning("error avoided - color change")
                pass
            finally:
                try:
                    for fp in self.pathsLays:
                        fp.color = Publisher.Theme.SAVE
                    self.relativePath.color = Publisher.Theme.RELATIVE
                except:
                    print("error avoided")
                    cmds.warning("error avoided - reset")
                    pass
                finally:
                    # cmds.warning("unlock color")
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
            self.addPath = Publisher.MC_PathLine(self.layout, color=Publisher.Theme.SAVE, image=Publisher.Image.ADD, annotation=Publisher.LG.Button.add).load()
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

            self.btn_prep = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.CLEAN,      h=30, w=30, bgc=Publisher.Theme.BUTTON,     c=Callback(self.runEvent, "btn_prep"), ann=Publisher.LG.Button.prepare), top="FORM", bottom=None, left="FORM", right=None, margin=(m,m,m,m))
            self.btn_rollBack = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.UNDO,   h=30, w=30, bgc=Publisher.Theme.BUTTON,     c=Callback(self.runEvent, "btn_rollBack"), ann=Publisher.LG.Button.rollback, en=False), top="FORM", bottom=None, left=self.btn_prep, right=None, margin=(m,m,m,m))

            self.btn_backup = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.SAVE,     h=30, w=30, bgc=Publisher.Theme.RELATIVE,   c=Callback(self.runEvent, "btn_backup"), ann=Publisher.LG.Button.backup), top=None, bottom="FORM", left=None, right="FORM", margin=(m,m,m,m))
            self.btn_revealExplorer = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.FOLDER,     h=30, w=30, bgc=Publisher.Theme.RELATIVE,   c=Callback(self.runEvent, "btn_revealExplorer"), ann=Publisher.LG.Button.revealExplorer), top=None, bottom="FORM", left=None, right=self.btn_backup, margin=(m,m,m,m))

            self.btn_test = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.CHECK,      h=30, w=30, bgc=Publisher.Theme.RELATIVE,   c=Callback(self.runEvent, "btn_test"), ann=Publisher.LG.Button.check, en=False), top=None, bottom="FORM", left="FORM", right=None, margin=(m,m,m,m))
            self.btn_publish = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.PUBLISH, h=30, w=30, bgc=Publisher.Theme.LOCAL,      c=self.cb_publishEvent(), ann=Publisher.LG.Button.publish), top=None, bottom="FORM", left=self.btn_test , right=None, margin=(m,m,m,m))
            self.btn_upload = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.NETWORK,  h=30, w=30, bgc=Publisher.Theme.SAVE,       c=Callback(self.runEvent, "btn_upload"), ann=Publisher.LG.Button.upload), top=None, bottom="FORM", left=self.btn_publish, right=None, margin=(m,m,m,m))

            self.lab_comment = self.attach(cmds.text(p=self.layout, l=Publisher.LG.Label.comment), top=self.btn_prep, bottom=None, left="FORM", right=None, margin=(m,m,m,m))
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
            self.btn_revealExplorer = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.FOLDER,     h=30, w=30, bgc=Publisher.Theme.RELATIVE,   c=Callback(self.runEvent, "btn_revealExplorer"), ann=Publisher.LG.Button.revealExplorer), top=None, bottom="FORM", left=None, right=self.btn_backup, margin=(m,m,m,m))

            self.btn_publish  = self.attach(cmds.iconTextButton(image=Publisher.Image.PUBLISH, h=30, w=30, bgc=Publisher.Theme.LOCAL, c=self.cb_confoEvent(), ann="Confo"), top=None, bottom="FORM", left="FORM" , right=None, margin=(m,m,m,m))
            self.btn_upload   = self.attach(cmds.iconTextButton(image=Publisher.Image.NETWORK, h=30, w=30, bgc=Publisher.Theme.SAVE, c=Callback(self.runEvent, "btn_upload"), ann="Upload to drives"), top=None, bottom="FORM", left=self.btn_publish, right=None, margin=(m,m,m,m))

            self.lab_comment  = self.attach(cmds.text(l="Commentaire : "), top="FORM", bottom=None, left="FORM", right=None, margin=(m,m,m,m))
            self.lay_comment = self.attach(cmds.scrollField(p=self.layout, editable=True, wordWrap=True, w=5), top=self.lab_comment, bottom=self.btn_publish, left="FORM", right="FORM", margin=(m,m,m,m))

            self.applyAttach()

    class MC_StrSplitter(Module):
        splitFunc = {
            "str" : ('Every string', lambda x, a: x.split(a)),
            "alphaNum" : ('Alpha/Num', lambda x: re.findall(r"[^\W\d_]+|\d+", x)),
            "lowUpCase" : ('Lower/Upper', lambda x: re.findall('[A-Z][^A-Z]*', x)),
        }

        def __init__(self, parent, operations, name=None, input=lambda: "Example"):
            Module.__init__(self, parent, name=name)
            self.operations = operations
            self.input = input
            self.start = self.operations[3] >= 0

        def output(self):
            op = self.operations
            return Publisher.MC_StrSplitter.solveOperation(self.input(), op[0], op[1], op[2], op[3])

        @staticmethod
        def solveOperation(word, extract=True, typeSplit="str", args=None, index=0):
            # if typeSplit == "str":
            #     arr = word.split(args)
            # elif typeSplit == "alphaNum":
            #     arr = re.findall(r"[^\W\d_]+|\d+", word)
            # elif typeSplit == "lowUpCase":
            #     arr = re.findall('[A-Z][^A-Z]*', word)

            arr = Publisher.MC_StrSplitter.splitWords(word, typeSplit, args)
            if extract:
                output = arr[index] if index < len(arr) else arr[-1]
            else :
                arr.pop(index)
                output = arr
                if typeSplit == "str":
                    output = args.join(output)

            return output if index < len(arr) else arr[-1]

        @staticmethod
        def splitWords(word, typeSplit="str", args=None):
            if typeSplit == "str":
                arr = word.split(args)
            elif typeSplit == "alphaNum":
                arr = re.findall(r"[^\W\d_]+|\d+", word)
            elif typeSplit == "lowUpCase":
                arr = re.findall('[A-Z][^A-Z]*', word)
            else:
                arr = []
            return arr

        @staticmethod
        def getResult(operations, input_):
            '''operation : (bool: extract/exclude, str: split type, str: split args, int: iterator)
            input_ : str: fileName
            '''
            output = input_
            for op in operations:
                output = Publisher.MC_StrSplitter.solveOperation(output, op[0], op[1], op[2], op[3])
                # if op[0] == "str":
                #     arr = output.split(op[1])
                # elif op[0] == "alphaNum":
                #     arr = re.findall(r"[^\W\d_]+|\d+", output)
                # elif op[0] == "lowUpCase":
                #     arr = re.findall('[A-Z][^A-Z]*', output)
                #     arr = output.split(op[1])
                # output = arr[op[2]] if op[2] < len(arr) else arr[-1]

            return output

        @callback
        def cb_changeIndex(self, i):
            arr = Publisher.MC_StrSplitter.splitWords(self.input(), self.operations[1], self.operations[2])
            if self.operations[3] >= 0:
                last_index = self.operations[3]
            else:
                last_index = len(arr) + self.operations[3]
                i = i - len(arr)
            if last_index < len(self.childrens):
                cmds.control(self.childrens[last_index], e=True, bgc=Publisher.Theme.BUTTON)
            cmds.control(self.childrens[i], e=True, bgc=Publisher.Theme.SELECTED)
            self.operations[3] = i
            cmds.intField(self.iterSplit, e=True, v=self.operations[3])
            self.runEvent("update")


        def update(self):
            print(self.input())
            for c in self.childrens:
                cmds.deleteUI(c)
            self.childrens = []
            prev = "FORM"
            arr = Publisher.MC_StrSplitter.splitWords(self.input(), self.operations[1], self.operations[2])
            for i, elem in enumerate(arr):
                bgColor = Publisher.Theme.SELECTED if i == (self.operations[3] if self.operations[3] >= 0 else len(arr) + self.operations[3]) else Publisher.Theme.BUTTON
                prev = self.attach(cmds.button(parent=self, l=elem, bgc=bgColor, c=self.cb_changeIndex(i)), top="FORM", left=prev, margin=(0,0,5,5))
                self.childrens.append(prev)
            self.applyAttach()
            self.runEvent("update")

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent, bgc=Publisher.Theme.SEC_BGC)

            it = int(not self.operations[0]) + 1
            self.exOption = self.attach(cmds.optionMenu(parent=self.layout, bgc=Publisher.Theme.BUTTON), top="FORM", left="FORM", margin=(4,2,5,2))
            cmds.menuItem(p=self.exOption, label='Extract')
            cmds.menuItem(p=self.exOption, label='Exclude')
            cmds.optionMenu(self.exOption, e=True, sl=it)

            self.splitTypeLabel = self.attach(cmds.text(parent=self.layout, l="Split by : "), top="FORM", left=self.exOption, margin=(7,2,2,2))
            it = ["str", "alphaNum", "lowUpCase"].index(self.operations[1]) + 1
            self.splitOptions = self.attach(cmds.optionMenu(parent=self.layout, bgc=Publisher.Theme.BUTTON), top="FORM", left=self.splitTypeLabel, margin=(4,2,2,2))
            cmds.menuItem(p=self.splitOptions, label='String')
            cmds.menuItem(p=self.splitOptions, label='Alpha/Num')
            cmds.menuItem(p=self.splitOptions, label='Lower/Upper')
            cmds.optionMenu(self.splitOptions, e=True, sl=it)


            self.removeBtn = self.attach(cmds.iconTextButton(parent=self.layout, image=Publisher.Image.QUIT), top="FORM", right="FORM", margin=(5,5,5,5))
            visField = self.operations[1] == "str"
            self.iterSplit = self.attach(cmds.intField(parent=self.layout, v=self.operations[3], vis=visField, w=50), top="FORM", right=self.removeBtn, margin=(4,2,2,2))
            self.strSplit = self.attach(cmds.textField(parent=self.layout, tx=self.operations[2], vis=visField), top="FORM", left=self.splitOptions, right=self.iterSplit, margin=(4,2,2,2))

            sc, ec = (Publisher.Theme.SELECTED, Publisher.Theme.BUTTON) if self.operations[3] >= 0 else (Publisher.Theme.BUTTON, Publisher.Theme.SELECTED)
            self.indexStardBtn = self.attach(cmds.iconTextButton(parent=self.layout, h=25, w=20, image=Publisher.Image.RIGHTARROW, bgc=sc), top=self.splitTypeLabel, left="FORM", margin=(8,5,5,5))
            self.indexEndBtn = self.attach(cmds.iconTextButton(parent=self.layout, h=25, w=20, image=Publisher.Image.LEFTARROW, bgc=ec), top=self.splitTypeLabel, right="FORM", margin=(8,5,5,5))

            self.childrenLayout = self.attach(cmds.formLayout(parent=self.layout), top=self.splitTypeLabel, left=self.indexStardBtn, right=self.indexEndBtn, margin=(8,5,0,0))

            self.update()
            # prev = self.indexStardBtn
            # arr = Publisher.MC_StrSplitter.splitWords(self.input(), self.operations[1], self.operations[2])
            # for i, elem in enumerate(arr):
            #     bgColor = Publisher.Theme.SELECTED if i == (self.operations[3] if self.operations[3] >= 0 else len(arr) + self.operations[3]) else Publisher.Theme.BUTTON
            #     prev = self.attach(cmds.button(parent=self.layout, l=elem, bgc=bgColor), top=self.splitTypeLabel, left=prev, margin=(8,5,5,5))

            self.attach(cmds.formLayout(parent=self.layout, h=5), bottom="FORM")
            self.applyAttach()

    class MC_VariableEditor(Module):
        name = "Variable getter"
        def __init__(self, varName, operations, example=""):
            name = self.name
            Module.__init__(self, None)
            self.name = name
            self.example = example
            self.varName = varName
            self.operations = operations

        def getExample(self):
            return cmds.textField(self.exampleInput, q=True, tx=True)

            return self.example

        def updateOutput(self, output):
            cmds.textField(self.exampleOutput, e=True , tx=output())

        @callback
        def cb_updateInputTF(self, *args):
            print("test {}".format(args))
            self.runEvent(*args)

        @callback
        def cb_upadteName(self):
            name = cmds.textField(self.varNameInput, q=True, tx=True)
            self.runEvent("updateNameTF", lambda: name)

        def load(self):
            if cmds.workspaceControl(self.name, exists=1):
                cmds.deleteUI(self.name)
            self.win = cmds.workspaceControl(self.name, ih=240, iw=320, retain=False, floating=True, h=100, w=500)
            self.layout = cmds.formLayout(parent=self.win, bgc=Publisher.Theme.MAIN_BGC)

            # self.typeBtn = self.attach(cmds.optionMenu(parent=self.layout, bgc=Publisher.Theme.BUTTON), top="FORM", left="FORM", margin=(2,2,2,2))
            # cmds.menuItem(p=self.typeBtn, label='String')
            # cmds.menuItem(p=self.typeBtn, label='Int')
            # cmds.menuItem(p=self.typeBtn, label='Const')

            self.varNameLabel = self.attach(cmds.text(parent=self.layout, l="Variable Name"), top="FORM", left="FORM", margin=(5,2,2,2))
            self.varNameInput = self.attach(cmds.textField(parent=self.layout, tx=self.varName, ed=True, ec=self.cb_upadteName(), alwaysInvokeEnterCommandOnReturn=True), top="FORM", left=self.varNameLabel, right="FORM", margin=(2,2,2,2))

            print(self.example, self.operations)
            exOutput = Publisher.MC_StrSplitter.getResult(self.operations, self.example) if len(self.operations) != 0 else self.varName
            self.exampleInputLabel = self.attach(cmds.text(parent=self.layout, l="Input : "), top=self.varNameInput, left="FORM", margin=(5,2,2,2))
            self.exampleInput = self.attach(cmds.textField(parent=self.layout, tx=self.example, ed=True, ec=Callback(self.runEvent, "updateInputTF"), alwaysInvokeEnterCommandOnReturn=True), top=self.varNameInput, left=self.exampleInputLabel, right="FORM", margin=(5,2,2,2))
            self.exampleOutputLabel = self.attach(cmds.text(parent=self.layout, l="Output : "), top=self.exampleInput, left="FORM", margin=(5,2,2,2))
            self.exampleOutput = self.attach(cmds.textField(parent=self.layout, tx=exOutput, ed=False), top=self.exampleInput, left=self.exampleOutputLabel, right="FORM", margin=(5,2,2,2))

            self.childrenLayout = self.attach(cmds.formLayout(parent=self.layout), top=self.exampleOutput, left="FORM", right="FORM", margin=(5,5,5,5))
            prev = "FORM"
            prevInput = self.getExample
            self.splitSections = []
            for op in self.operations:
                current = self.attach(Publisher.MC_StrSplitter(self, op, input=prevInput).load(), top=prev, left="FORM", right="FORM", margin=(5,5,0,0))
                self.splitSections.append(current)
                if prev != "FORM":
                    prev.eventHandler("update", current.update)
                else:
                    print("eventhandler", op)
                    self.eventHandler("updateInputTF", current.update)
                prev = current
                prevInput = current.output
            if isinstance(prev, Module):
                prev.eventHandler("update", self.updateOutput, prev.output)
            else:
                self.eventHandler("updateNameTF", self.updateOutput)

            self.addBtn = self.attach(cmds.iconTextButton(parent=self.layout, image=Publisher.Image.ADD, bgc=Publisher.Theme.BUTTON), top=self.childrenLayout, left="FORM", right="FORM", margin=(5,5,5,5))
            self.saveBtn = self.attach(cmds.button(parent=self.layout, l="Save & exit", bgc=Publisher.Theme.BUTTON), bottom="FORM", left="FORM", right="FORM", margin=(5,5,5,5))
            self.attach(cmds.formLayout(parent=self.layout, h=20), bottom=self.saveBtn)
            self.applyAttach()

    class MC_Label(Module):
        def __init__(self, parent, name, button=False, bgc=None):
            Module.__init__(self, parent, name)
            self.button = button
            self.bgc = bgc if bgc is not None else Publisher.Theme.BUTTON

        def load(self):
            self.layout = cmds.formLayout("label_{}_{}".format(self.increment, self.name), parent=self.parent)


            # self.del_btn = self.attach(cmds.iconTextButton(image=Publisher.Image.QUIT, bgc=self.bgc, h=18, c=Callback(self.runEvent, "remove", self.name)), top="FORM", right="FORM", margin=(1,1,1,1))
            self.del_btn = "FORM"
            if self.button:
                self.title = self.attach(cmds.button(l=self.name, bgc=self.bgc, h=18, c=Callback(self.runEvent, "click", self.name)), top="FORM", left="FORM", right=self.del_btn, margin=(1,1,1,1))
            else:
                self.title = self.attach(cmds.text(l="  {}  ".format(self.name), bgc=self.bgc, h=18), top="FORM", left="FORM", right=self.del_btn, margin=(1,1,1,1))
            self.gmc = cmds.popupMenu("gmc  " + self.title, parent=self.title, button=3, pmc=Callback(self.runEvent, "remove", self.name))
            self.applyAttach()

    class MC_AddOption(Module):
        def __init__(self, parent, name=None, bgc=None, options=[]):
            Module.__init__(self, parent, name)
            self.bgc = bgc if bgc is not None else Publisher.Theme.BUTTON
            self.options = ["project", "path", "name", "state", "version", "extension", "_", ".", "v", "\\"]
            self.options = options

        def load(self):
            self.layout = cmds.formLayout("label_{}_{}".format(self.increment, self.name), parent=self.parent)

            if len(self.options) > 0:
                self.del_btn = self.attach(cmds.image(p=self.layout, image=Publisher.Image.ADD, bgc=self.bgc, h=18, w=18), top="FORM", right="FORM", bottom="FORM", left="FORM", margin=(1,1,1,1))
                self.gmc = cmds.popupMenu("gmc  " + self.del_btn, parent=self.del_btn, button=1, pmc=Callback(self.runEvent, "option", self.name))
                for opt in self.options:
                    cmds.menuItem(p=self.gmc, label=opt)
            else:
                self.del_btn = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.ADD, bgc=self.bgc, h=18, w=18, c=Callback(self.runEvent, "option", self.name)), top="FORM", right="FORM", bottom="FORM", left="FORM", margin=(1,1,1,1))
            self.applyAttach()


    class MC_stackContainer(Module):
        def __init__(self, parent):
            Module.__init__(self, parent)

        @callback
        def resize(self):
            self.clearAttach()
            self.attach(self.scrlLay, top="FORM", left="FORM", right="FORM", bottom="FORM")

            if self.layout is None:
                return
            width = 0
            height = 10
            curHeight = 0
            prevHrztl = "FORM"
            prevVrtcl = "FORM"
            margin = (3,3,-3,-3)
            child = None
            # print([x.name for x in self.childrens])
            for child in self.childrens:
                if isinstance(child, Module):
                    if width + child.width < self.width:
                        self.attach(child, top=prevVrtcl, left=prevHrztl, margin=margin)
                        width += child.width
                        prevHrztl = child
                        curHeight = max(curHeight, child.height + 10)
                    else:
                        prevVrtcl = prevHrztl
                        self.attach(child, top=prevVrtcl, left="FORM", margin=margin)
                        prevHrztl = child
                        width = 0
                        height += curHeight
                        curHeight = 0
                else:
                    childWidth = cmds.control(child, q=True, width=True)
                    childHeight = cmds.control(child, q=True, height=True)
                    if width + childWidth < self.width:
                        self.attach(child, top=prevVrtcl, left=prevHrztl, margin=margin)
                        width += childWidth
                        prevHrztl = child
                        curHeight = max(curHeight, childHeight + 10)
                    else:
                        prevVrtcl = prevHrztl
                        self.attach(child, top=prevVrtcl, left="FORM", margin=margin)
                        prevHrztl = child
                        width = 0
                        height += curHeight
                        curHeight = 0
            if child is not None:
                height += max(curHeight, child.height + 10)

            cmds.layout(self.layout, e=True, h=height)
            self.applyAttach()

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent, bgc=Publisher.Theme.MAIN_BGC)
            self.scrlLay = self.attach(cmds.scrollLayout(parent=self.layout, w=1, cr=True, rc=self.resize()), top="FORM", left="FORM", right="FORM", bottom="FORM")
            self.childrenLayout = cmds.formLayout("StackContChildLay", parent=self.scrlLay)

            for child in self.childrens:
                if isinstance(child, Module):
                    child.load()
            self.resize()()


    class MC_SettingSection(Module):
        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            self.title = self.attach(cmds.text(l=self.name), top="FORM", left="FORM")
            self.separator = self.attach(cmds.separator(parent=self.layout, height=10, style='in' ), top="FORM", left=self.title, right="FORM", margin=(3,3,15,3))
            self.childrenLayout = self.attach(cmds.formLayout("childLay", parent=self.layout), top=self.title, left="FORM", right="FORM", margin=(3,3,25,3))

            for c in self.childrens:
                c.load()
                self.attach(c, top="FORM", bottom="FORM", left="FORM", right="FORM",)

            self.applyAttach()

    class MT_SettingLanguage(Module):
        @callback
        def cb_changeLanguage(self, lg):
            new_lg = Publisher.Language.getLg(lg)
            if new_lg is not None:
                Publisher.LG = new_lg
            else :
                cmds.warning("This language, {}, is not define".format(lg))
            Publisher.writePref("lg", Publisher.LG.__name__)
            Publisher().reload()
            # Publisher.lg = Publisher.Language.En if Publisher.lg == Publisher.Language.Fr else Publisher.Language.Fr

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            self.btns = {}
            prev = "FORM"
            for lg, lgName in [("En", "English"), ("Fr", u"Français"), ("Es", u"Español"), ("Pt", u"Português")]:
                color = Publisher.Theme.SELECTED if Publisher.LG.__name__ == lg else Publisher.Theme.BUTTON
                prev = self.attach(cmds.button(p=self.layout, l=lg, c=self.cb_changeLanguage(lg), ann=lgName, h=30, w=30, bgc=color), top="FORM", left=prev, margin=(3,3,3,3))
                self.btns[lg] = prev

            self.btn_folder = self.attach(cmds.iconTextButton(p=self.layout, image=Publisher.Image.FOLDER, h=30, w=30, bgc=Publisher.Theme.BUTTON, c=Callback(self.runEvent, "btn_upload"), ann=Publisher.LG.Button.loadLanguage), top="FORM", right="FORM", margin=(3,3,3,3))
            self.applyAttach()

    class MC_NameDefinition(Module):
        def __init__(self, parent, name, lst, variables, example="/"):
            Module.__init__(self, parent, name)
            self.list = lst
            self.example = example
            self.variables = variables

        @callback
        def cb_remove(self, elem):
            print("removing {}".format(elem))

        @callback
        def cb_gapUpdateSize(self, gap, index):
            print("update")
            txt = cmds.textField(gap, q=True, tx=True)
            size = len(txt) * 7 + 11
            cmds.textField(gap, e=True, w=size)
            self.containerVar.resize()()

            self.list[index] = txt

            self.updateExample()

        def updateExample(self):
            exOutput = self.getFuseWords()
            cmds.text(self.examplePath , e=True, l=exOutput)

        def getFuseWords(self):
            exOutput = ""
            # return self.example()
            for e in self.list:
                if e in self.variables:
                    exOutput += Publisher.MC_StrSplitter.getResult(self.variables[e], self.example()) if len(self.variables[e]) != 0 else ""
                else:
                    exOutput += e

            return exOutput

        @staticmethod
        def fuseWords(words, variables, path):
            exOutput = ""

            for e in words:
                if e in variables:
                    exOutput += Publisher.MC_StrSplitter.getResult(variables[e], path) if len(variables[e]) != 0 else ""
                else:
                    exOutput += e

            return exOutput

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent, bgc=Publisher.Theme.THD_BGC)

            self.title = self.attach(cmds.text(p=self.layout, l="{} : ".format(self.name.capitalize())), top="FORM", left="FORM", margin=(3,3,5,3))
            self.containerVar = Publisher.MC_stackContainer(self.layout).load()
            for i, e in enumerate(self.list):
                if e in self.variables:
                    label = Publisher.MC_Label(self.containerVar, str(e), bgc=Publisher.Theme.BUTTON)
                    label.eventHandler("remove", self.cb_remove(str(e)))
                    label.load()
                else:
                    text = str(e)
                    textWidth = len(text) * 7 + 11
                    gap = cmds.textField(p=self.containerVar, text=text, fn="fixedWidthFont", w=textWidth, bgc=Publisher.Theme.THD_BGC) #, ed=False)
                    cmds.textField(gap, e=True, cc=self.cb_gapUpdateSize(gap, i))
                    self.containerVar.childrens.append(gap)
            print("all child create")
            Publisher.MC_AddOption(self.containerVar, options=["project", "path", "name", "state", "version", "extension", "_", ".", "v", "\\"])
            # self.containerVar.applyAttach()
            self.containerVar.resize()()
            self.attach(self.containerVar, top=self.title, left="FORM", right="FORM", margin=(3,3,15,5))
            self.exampleLabel = self.attach(cmds.text(p=self.layout, l="Example : "), top=self.containerVar, left="FORM")
            exOutput = self.getFuseWords()
            self.examplePath = self.attach(cmds.text(p=self.layout, l=exOutput, al="left"), top=self.containerVar, left=self.exampleLabel, right="FORM")
            self.attach(cmds.formLayout(p=self.layout, h=5), top=self.examplePath, left="FORM", right="FORM")


        def _loadJobs(self):
            self._scriptJobIndex.append(cmds.scriptJob(event=["SceneOpened", self.updateExample]))
            self._scriptJobIndex.append(cmds.scriptJob(event=["SceneSaved", self.updateExample]))

    class MT_SettingsNameConvertion(Module):

        NAME_DEFAULT_EMPTY = {}
        VAR_DEFAULT_CS = {
                    "project" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 0]],
                    "path" : [[False, "str", "\\wip", -1]],
                    "name" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 1]],
                    "state" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 2]],
                    "version" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 3], [True, "alphaNum", None, -1]],
                    "extension" : [[True, "str", "\\", -1], [True, "str", ".", -1]]
            }
        VAR_DEFAULT_CUSTOM = {
                    "project" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 0]],
                    "path" : [[False, "str", "\\wip", -1]],
                    "name" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 1]],
                    "state" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 3]],
                    "version" : [[True, "str", "\\", -1], [True, "str", ".", 0], [True, "str", "_", 3], [True, "alphaNum", None, -1]],
                    "extension" : [[True, "str", "\\", -1], [True, "str", ".", -1]],
                    "type" : [[True, "str", "wip", -1], [True, "str", ".", 0], [True, "str", "_", 2]]
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
                ("Publish Image", ["path", "\\", "project", "_", "name", "_", "state", "_Preview.0001.jpg"]),
                ("Version", ["path", "\\version\\", "project", "_", "name", "_", "state", "_v", "version", ".", "extension"]),
                ("Version Image", ["path", "\\version\\", "project", "_", "name", "_", "state", "_v", "version", "_Preview.0001.jpg"]),
                ("info file", ["path", "\\info.cst"]),
                ("Confo", ["path", "\\", "project", "_", "name", "_", "state", ".", "extension"]),
                ("Confo image", ["path", "\\", "project", "_", "name", "_", "state", "_Preview.0001.jpg"])
            ]
        NAME_DEFAULT_CUSTOM = [
                ("Publish", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", ".", "extension"]),
                ("Publish Image", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", "_", "thumbnail", ".", "jpg"]),
                ("Version", ["path", "\\version\\", "project", "_", "type", "_", "name", "_", "state", "_", "v", "version", ".", "extension"]),
                ("Version Image", ["path", "\\version\\", "project", "_", "type", "_", "name", "_", "state", "_", "v", "version", "_", "thumbnail", ".", "jpg"]),
                ("info file", []),
                ("Confo", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", "_", ".", "extension"]),
                ("Confo image", ["path", "\\", "project", "_", "type", "_", "name", "_", "state", "_", "thumbnail", ".", "jpg"])
            ]

        def __init__(self, parent):
            Module.__init__(self, parent)
            self.example = lambda: "Y a rien"
            self.variables = Publisher.MT_SettingsNameConvertion.VAR_DEFAULT_CS
            self.pathDefs = {}

        @callback
        def cb_editLabel(self, name=None):
            print("edit {}".format(name))
            if name is None:
                Publisher.MC_VariableEditor("", [], self.example()).load()
            else:
                Publisher.MC_VariableEditor(name, self.variables[name], self.example()).load()

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
                self.loadNameDefinitions(Publisher.MT_SettingsNameConvertion.NAME_DEFAULT_EMPTY)
            elif name == "Custom":
                self.loadNameDefinitions(Publisher.MT_SettingsNameConvertion.NAME_DEFAULT_CUSTOM)
            elif name == "CS":
                self.loadNameDefinitions(Publisher.MT_SettingsNameConvertion.NAME_DEFAULT_CS)

        def loadNameDefinitions(self, names):
            prev = self.presetDefineNamesDropMenu
            for n in names:
                buttons = [x for x in n[1]]
                prev = self.attach(Publisher.MC_NameDefinition(self.layout, n[0], buttons, self.variables, self.example).load(), top=prev, left="FORM", right="FORM", margin=(8,8,8,8))
                self.pathDefs[n[0]] = prev

        ## ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)

            self.titleDefineVar = self.attach(cmds.text(p=self.layout, l="Define Variables"), top="FORM", left="FORM", margin=(3,3,0,3))
            self.presetDropMenu = self.attach(cmds.optionMenu(p=self.layout, l="Presets : ", bgc=Publisher.Theme.BUTTON), top=self.titleDefineVar, left="FORM", margin=(3,3,0,3))
            cmds.menuItem(p=self.presetDropMenu, label='-')
            cmds.menuItem(p=self.presetDropMenu, label='Custom')
            cmds.menuItem(p=self.presetDropMenu, label='CS')
            self.loadPresetBtn = self.attach(cmds.iconTextButton(p=self.layout, i=Publisher.Image.FOLDER, bgc=Publisher.Theme.BUTTON), top=self.titleDefineVar, right="FORM", margin=(3,3,3,3))
            self.savePresetBtn = self.attach(cmds.iconTextButton(p=self.layout, i=Publisher.Image.SAVE, bgc=Publisher.Theme.BUTTON), top=self.titleDefineVar, right=self.loadPresetBtn, margin=(3,3,3,3))
            self.versionLabel = self.attach(cmds.text(p=self.layout, l=u"N° de version"), top=self.presetDropMenu, left="FORM", margin=(8,3,3,3))
            self.versiondefineBtn = self.attach(cmds.button(p=self.layout, l=u"Définir", bgc=Publisher.Theme.BUTTON, c=self.cb_editLabel("version")), top=self.presetDropMenu, left=self.versionLabel, margin=(3,3,3,3))
            self.nbDigits = self.attach(cmds.intField(p=self.layout, v=3), top=self.presetDropMenu, left=self.versiondefineBtn, margin=(3,3,3,3))


            self.containerAllVar = Publisher.MC_stackContainer(self.layout)
            for e in self.variables:
                print(e, self.variables[e])
                bgc = Publisher.Theme.BUTTON if len(self.variables[e]) > 0 else Module.COLOR_LIGHTGREYBLUE
                label = Publisher.MC_Label(self.containerAllVar, e, button=True, bgc=bgc)
                label.eventHandler("click", self.cb_editLabel(e))
                label.eventHandler("remove", self.cb_deleteLabel(e))
            Publisher.MC_AddOption(self.containerAllVar)
            self.containerAllVar.load()
            # self.attach(cmds.iconTextButton(i=Publisher.Image.ADD, c=self.cb_editLabel(), p=self.containerAllVar))
            # cmds.iconTextButton(p=self.containerAllVar, image=Publisher.Image.ADD, h=18, w=18, bgc=Publisher.Theme.BUTTON, c=self.cb_editLabel())
            self.attach(self.containerAllVar, top=self.nbDigits, left="FORM", right="FORM", margin=(15,3,3,3))


            self.titleDefineNames = self.attach(cmds.text(p=self.layout, l="Define names"), top=self.containerAllVar, left="FORM", margin=(3,3,0,3))
            self.presetDefineNamesDropMenu = self.attach(cmds.optionMenu(p=self.layout, l="Presets : ", bgc=Publisher.Theme.BUTTON), top=self.titleDefineNames, left="FORM", margin=(3,3,0,3))
            cmds.menuItem(p=self.presetDefineNamesDropMenu, label='-')
            cmds.menuItem(p=self.presetDefineNamesDropMenu, label='Custom')
            cmds.menuItem(p=self.presetDefineNamesDropMenu, label='CS')

            self.loadNameDefinitions(Publisher.MT_SettingsNameConvertion.NAME_DEFAULT_CS)

    class MT_SettingsPlugin(Module):
        @callback
        def cb_install(self):
            self.cb_uninstall()()
            PFolder = os.path.join(os.path.expanduser('~'),"maya", cmds.about(version=True), "plug-ins")
            f = str(Publisher().__class__.__name__) + ".py"
            try:
                if not os.path.exists(PFolder):
                    os.makedirs(PFolder)
                shutil.copy(__file__, os.path.join(PFolder, f))
                cmds.loadPlugin(f)
            except:
                cmds.warning("Can't install! Did you drag & drop the file into the viewport?")

        @callback
        def cb_uninstall(self):
            PFolder = os.path.join(os.path.expanduser('~'),"maya", cmds.about(version=True), "plug-ins")
            f = str(Publisher().__class__.__name__) + ".py"

            if not os.path.exists(os.path.join(PFolder, f)):
                cmds.warning("Publisher plug-in already uninstaled")
                return

            cmds.unloadPlugin(f)
            os.remove(os.path.join(PFolder, f))
            Info("Uninstalled")

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            prev = "FORM"
            PFolder = os.path.join(os.path.expanduser('~'),"maya", cmds.about(version=True), "plug-ins")
            f = str(Publisher().__class__.__name__) + ".py"
            if "__file__" in globals():
                if not os.path.normpath(os.path.join(PFolder, f)) == os.path.normpath(__file__):
                    self.attach(cmds.button(p=self.layout, l=Publisher.LG.Button.install, c=self.cb_install(), bgc=Publisher.Theme.BUTTON), top="FORM", left="FORM", right=50, margin=(3,3,3,3))
                    prev = 50
            self.attach(cmds.button(p=self.layout, l=Publisher.LG.Button.uninstall, c=self.cb_uninstall(), bgc=Publisher.Theme.ERROR), top="FORM", right="FORM", left=prev, margin=(3,3,3,3))

            self.applyAttach()

    class MGT_Settings(Module):
        def __init__(self, parent):
            Module.__init__(self, parent)
            self.section = {}
            self.defineSection()

        def defineSection(self):
            self.section["language"] = Publisher.MC_SettingSection(self, Publisher.LG.Label.language)
            self.section["nameConv"] = Publisher.MC_SettingSection(self,Publisher.LG.Label.nameConv)
            self.section["test"] = Publisher.MC_SettingSection(self,Publisher.LG.Label.TestDef)
            self.section["prefs"] = Publisher.MC_SettingSection(self,Publisher.LG.Label.loadSavePref)
            self.section["plugin"] = Publisher.MC_SettingSection(self,Publisher.LG.Label.plugin)
            self.section["colorTheme"] = Publisher.MC_SettingSection(self,Publisher.LG.Label.colorTheme)

            Publisher.MT_SettingLanguage(self.section["language"])
            Publisher.MT_SettingsNameConvertion(self.section["nameConv"])
            Publisher.MT_SettingsPlugin(self.section["plugin"])

        def load(self):
            self.layout = cmds.formLayout(parent=self.parent)
            # self.tmp = self.attach(cmds.text("plop", p=self.layout, l="WIP"), top="FORM", left="FORM")
            self.tmp = "FORM"
            self.scrlLay = self.attach(cmds.scrollLayout("scrlLay", parent=self.layout, cr=True), top="FORM", bottom="FORM", left="FORM", right="FORM", margin=(0,0,0,0))
            self.childrenLayout = cmds.formLayout(parent=self.scrlLay)

            prev = "FORM"
            for c in self.childrens:
                c.load()
                prev = self.attach(c, top=prev, left="FORM", right="FORM", margin=(3,3,3,3))
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
            abouts_name = ["PUBLISHER", "PATHS", "SYNCCOMMON", "SYNCANIMATION", "SETTINGS"]
            # abouts = [getattr(Publisher.lg.About, a) for a in dir(Publisher.lg.About) if a.isupper()]
            abouts = [getattr(Publisher.LG.About, a) for a in abouts_name]
            txt = self.style + "".join(abouts)
            txt = txt.format(**context)


            prev = "FORM"
            prev = self.attach(cmds.text(p=self.childrenLayout, l=txt), top=prev, bottom=None, left="FORM", right="FORM", margin=(1,1,1,1))
            self.btn_ticket = self.attach(cmds.button(l=Publisher.LG.Button.ticket, c=self.openTicket()), top=prev, bottom=None, left="FORM", right=None, margin=(1,1,1,1))
            with io.open(os.path.join(self.__iconsPath, "test.html"), "w+", encoding="utf-8") as f:
                f.write(unicode(txt))
            self.applyAttach()

    class Sync():
        def __init__(self, pathsModule, pathDefs):
            self.pathsModule = pathsModule
            self.pathDefs = pathDefs
            self.wipRollback = None
            self.command = {}

            self.datas = {}
            self.datas["PublisherVersion"] = "{}".format(__version__)

            self.datas["Comment"] = None
            self.datas["Author"] = None
            self.datas["Computer"] = None
            self.datas["Date"] = None
            self.datas["Version"] = None

            self.lock = False

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

        @thread
        def backup(self):
            if self.lock:
                return
            self.lock = True

            localPath = self.pathsModule.getLocalPath()
            relativePath = self.pathsModule.getRelativePath()
            drives = self.pathsModule.getDrivesPath()
            infos = []
            for drive in drives:

                abs_path = os.path.join(drive, relativePath)
                if abs_path == relativePath:
                    infos.append((relativePath, False)) if (relativePath, False) not in infos else None
                    continue
                driveDir = os.path.dirname(abs_path)
                if not os.path.exists(drive):
                    infos.append((drive, False))
                    continue
                if not os.path.exists(driveDir):
                    os.makedirs(driveDir)
                state = None if os.path.exists(os.path.join(drive, relativePath)) else True
                if state is True:
                    try:
                        shutil.copy(os.path.join(localPath, relativePath), os.path.join(drive, relativePath))
                    except:
                        state = False
                infos.append((drive, state))
            self.pathsModule.infoColorPath(infos)
            self.lock = False

        @thread
        def upload(self):
            if self.lock:
                return
            self.lock = True
            threadTitle(" Uploading last version to drives ", type_=1)
            localPath = self.pathsModule.getLocalPath()
            relativePath = self.pathsModule.getRelativePath()
            drives = self.pathsModule.getDrivesPath()
            paths, names = self.getPathsAndNames(version=0)

            # Check if it's a wip
            if os.path.normpath(relativePath).split(os.sep)[-2] != "wip":
                cmds.warning("The current file is not a WIP")
                return
            # print("localPath      : " +  str(localPath))
            # print("relativePath   : " +  str(relativePath))
            # print("drives         : " +  str(drives))
            # print("paths          : " +  str(paths))
            # print("names          : " +  str(names))

            copyFiles = []
            copyFiles.append(os.path.join(paths["publish"], names["publish"]))
            copyFiles.append(os.path.join(paths["publish"], names["imgPublish"]))
            copyFiles.append(os.path.join(paths["publish"], names["infoFile"]))


            # return
            # #TODO Get the last version in the versions' folder
            copyFiles.append(os.path.join(paths["version"], names["version"]))
            copyFiles.append(os.path.join(paths["version"], names["imgVersion"]))

            info = []

            state = True
            for f in copyFiles:
                x = os.path.join(localPath, f)
                if not os.path.exists(x):
                    threadPrint("WARNING : no such file [..\\{}]".format('\\'.join(x.split('\\')[-3:])))
                    state = None
                    continue
            if state is None:
                info.append((relativePath, state))

            for d in drives:
                threadTitle(d, type_=0)
                if not os.path.exists(d):
                    threadPrint("ERROR : Path not found [{}] ".format(d))
                    info.append((d, False))
                    cmds.warning("Somes errors might occur, check console output for details")
                    continue
                cf = [(os.path.join(localPath, x), os.path.join(d, x)) for x in copyFiles]


                state = True
                for x in cf:
                    if not os.path.exists(x[0]):
                        continue
                    if os.path.exists(x[1]):
                        if abs(os.path.getmtime(x[0]) - os.path.getmtime(x[1])) <= 10000:
                            threadPrint("WARNING : already exist [..\\{}] ".format('\\'.join(x[0].split('\\')[-3:])))
                            state = None
                            continue

                    try:
                        # pass
                        treepath = '\\'.join(x[1].split('\\')[:-1])
                        if not os.path.exists(treepath):
                            os.makedirs(treepath)
                        shutil.copy(x[0], x[1])
                        # threadPrint("copy {}\n  to {}\n".format(x[0], x[1]))
                    except Exception as e:
                        print(e)
                        state = False
                        break
                if state is True:
                    threadPrint("Copy done successfully")
                if state is not True:
                    cmds.warning("Somes errors might occur, check console output for details")
                info.append((d, state))
            # info = [(p, bool(random.randint(0,1))) for p in self.pathsModule.getDrivesPath()]
            self.pathsModule.infoColorPath(info)
            self.lock = False

        def publish(self, comment):
            if self.lock:
                return
            self.lock = True

            localPath = self.pathsModule.getLocalPath()
            relativePath = self.pathsModule.getRelativePath()
            paths, names = self.getPathsAndNames()

            for k, v in self.pathDefs.pathDefs.items():
                print(k)
                print("\t" + v.fuseWords(v.list, v.variables, relativePath))
                print("")
            #TODO replace paths[] and names[] by pathsDefs
            pathsDefs = {k: v.fuseWords(v.list, v.variables, relativePath) for k, v in self.pathDefs.pathDefs.items()}

            # Prepare meta-data
            self.datas["Comment"] = comment
            self.setDatas()
            if self.wipRollback is None:
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

            # optionall file info
            self.optionalInfoFile()

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
            self.pathsModule.infoColorPath([(relativePath, True)])
            Info("{} -> Published !".format(names["publish"]))
            print("Publish", comment)
            self.lock = False

        def optionalInfoFile(self):
            '''Mainly for Pilou's asset manager
            '''
            localPath = self.pathsModule.getLocalPath()
            paths, names = self.getPathsAndNames()
            now = datetime.now() # current date and time
            date_time = now.strftime(" %d/%m %H:%M:%S")
            user = getpass.getuser()
            line = 'string $user = "{}"; string $date = "{}";'.format(user, date_time)
            infoPath = os.path.join(localPath, paths["publish"], names["infoFile"])
            with open(infoPath, "w+") as f:
                f.write(line)

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
                cmds.addAttr(node, longName=k, dataType="string")
                cmds.setAttr("publisher_metadata.{}".format(k), str(v), type="string")

        def setDatas(self):
            self.datas["Author"] = getpass.getuser()
            self.datas["Computer"] = os.environ['COMPUTERNAME']
            self.datas["Date"] = datetime.now().strftime("%H:%M:%S")

        def getPathsAndNames(self, version=False):
            localPath = self.pathsModule.getLocalPath()
            relativePath = self.pathsModule.getRelativePath()
            paths = {}
            names = {}

            paths["wip"], names["wip"] = os.path.split(relativePath)
            paths["publish"], _ = os.path.split(paths["wip"])
            paths["version"]= os.path.join(paths["publish"], "versions")
            if version is False:
                nVersion = Publisher.Sync.getVersionFromName(names["wip"])
            else:
                nVersion = Publisher.Sync.getLastVersion(os.path.join(localPath, paths["publish"])) - version

            self.datas["Version"] = nVersion

            fileName = "_".join(names["wip"].split(".")[0].split("_")[:-1])
            names["publish"] = fileName + "." + names["wip"].split(".")[-1]
            names["version"] = fileName + "_v{0:0>3d}.".format(nVersion) + names["wip"].split(".")[-1]
            names["infoFile"] = "info.cst"
            names["incWip"] = fileName + "_v{0:0>3d}.0001.ma".format(nVersion + 1)
            # names["imgPublish"] = "thumbnail.jpg"
            # names["imgVersion"] = "thumbnail_v{0:0>3d}.jpg".format(nVersion)
            names["imgPublish"] = "{}_Preview.0001.jpg".format(fileName)
            names["imgVersion"] = "thumbnail_v{0:0>3d}.jpg".format(nVersion)

            return (paths, names)

        def takeSnapshot(self, name="tmp", width=1024, height=1024):
            if not os.path.exists("/".join([self.pathsModule.getLocalPath(), "images"])):
                os.makedirs("/".join([self.pathsModule.getLocalPath(), "images"]))
            imagePath = "/".join([self.pathsModule.getLocalPath(), "images", name + ".jpg"])
            frame = cmds.currentTime( query=True )
            cmds.playblast(fr=frame, v=False, fmt="image", c="jpg", orn=False, cf=imagePath, wh=[width,height], p=100)
            print(imagePath)
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
        Publisher.LG = Publisher.Language.getLg(Publisher.readPref("lg"))
        if self.LG is None:
            Publisher.LG = Publisher.Language.Fr
            Publisher.writePref("lg", Publisher.LG.__name__)

    def revealExplorer(self):
        relativePath = self.paths.getRelativePath()
        localPath = self.paths.getLocalPath()
        subprocess.Popen('explorer /select,"{}"'.format(os.path.join(localPath, relativePath)))

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
        self.SyncCommon = self.tabs.addTopTabs(Publisher.MT_SyncCommon(self.tabs), Publisher.Image.COMMON, Publisher.LG.Button.common)
        self.SyncAnimation = self.tabs.addTopTabs(Publisher.MT_SyncAnimation(self.tabs), Publisher.Image.ANIMATION, Publisher.LG.Button.animation)
        #   Attach bot
        self.tabs.addBoTTabs(Publisher.MT_info(self.tabs), Publisher.Image.HELP, Publisher.LG.Button.about)
        settingsTab = self.tabs.addBoTTabs(Publisher.MGT_Settings(self.tabs), Publisher.Image.SETTING, Publisher.LG.Button.settings)
        settingsTab.section["nameConv"].childrens[0].example = self.paths.relativePath.getPath
        # Loading tabs
        self.tabs.load()

        self.syncEvent = Publisher.Sync(self.paths, settingsTab.section["nameConv"].childrens[0])
            # passing self.paths (mt_path that contain paths) and the setting section that contain the definition of paths
            # TODO maybe change the link with definitions of name by a preference file

        # Events
        self.SyncCommon.eventHandler("btn_revealExplorer", self.revealExplorer)
        self.SyncAnimation.eventHandler("btn_revealExplorer", self.revealExplorer)
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
        Info("[{}] -> loaded!".format(self.name))
        return self

    def _unload(self):
        if "win" not in dir(self):
            return self
        if self.win == None:
            return self
        if cmds.workspaceControl(self.win, exists=1):
            cmds.deleteUI(self.win)
        return self
    def unloadEvent(self):

        if cmds.workspaceControl(Publisher.MC_VariableEditor.name, exists=1):
            cmds.deleteUI(Publisher.MC_VariableEditor.name)

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
    if os.path.exists(__file__ + "c"):
        os.remove(__file__ + "c")

PLUGIN_SHELF_NAME = "CreativeSeeds"
PLUGIN_SHELF_BUTTON = "ButtonPublisher"

def getLastCommonParent(top):
    childrens = cmds.layout(top, q=True, ca=True)
    if len(childrens) != 1:
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

def getShelfButton(tab, name):
    array = cmds.layout(tab, q=True, ca=True)
    if array == None:
        return None
    for sb in array:
        if cmds.shelfButton(sb, q=True, annotation=True) == name:
            return sb
    return None

def initializePlugin(*args):
    '''To load the tool as a plugin
    '''
    shelfLay = getPlugInShelf()
    print(shelfLay)
    if shelfLay is not None:
        plugInTab = "{}|{}".format(shelfLay, PLUGIN_SHELF_NAME)
        if not cmds.layout(plugInTab, q=True, ex=True):
            cmds.shelfLayout(PLUGIN_SHELF_NAME, p=shelfLay)
        button = getShelfButton(plugInTab, 'Publisher')
        PFolder = os.path.join(os.path.expanduser('~'),"maya", cmds.about(version=True), "plug-ins")
        f = str(Publisher().__class__.__name__) + ".py"
        cmd = "import sys;"
        cmd += "sys.path.append(r'{}') if r'{}' not in sys.path else None;".format(PFolder, PFolder)
        cmd += "from Publisher import Publisher;"
        cmd += "Publisher().load();"
        if button is None:
            cmds.shelfButton(PLUGIN_SHELF_BUTTON, p=plugInTab, annotation='Publisher', image1='SP_FileDialogForward.png', command=cmd)
        else:
            cmds.shelfButton(button, e=True, p=plugInTab, annotation='Publisher', image1='SP_FileDialogForward.png', command=cmd)

def uninitializePlugin(*args):
    shelfLay = getPlugInShelf()
    plugInTab = "{}|{}".format(shelfLay, PLUGIN_SHELF_NAME)
    if shelfLay is not None:
        if not cmds.layout(plugInTab, q=True, ex=True):
            cmds.shelfLayout(PLUGIN_SHELF_NAME, p=shelfLay)
        button = getShelfButton(plugInTab, 'Publisher')
    if shelfLay is not None and button is not None:
        if cmds.control(button, q=True, ex=True):
            cmds.deleteUI(button)

        if cmds.layout(plugInTab, q=True, ex=True):
            if cmds.layout(plugInTab, q=True, ca=True) is None:
                cmds.deleteUI(plugInTab)

