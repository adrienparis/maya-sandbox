#!/usr/bin/env python
# -- coding: utf-8 --

import os
import shlex
from datetime import datetime

class Tag():
    def __init__(self, content):
        if content.startswith('/'):
            self.state = "end"
            content = content[1:]
        elif content.endswith('/'):
            self.state = "orphelin"
            content = content[:-1]
        elif content.startswith('?') and content.endswith('?'):
            content = content[1:-1]
            self.state = "info"
        else:
            self.state = "start"
        token = shlex.split(content)
        self.type = token.pop(0)
        self.arguments = {x.split("=")[0]: x.split('=')[1].replace('"', '') for x in token}
        self.line = 0
        self.start = 0
        self.end = 0
        # print("{} \t- {} \t- {}".format(self.type, self.state, self.arguments))


    @staticmethod
    def read(path):
        tags = []
        with open(path, "r+") as f:
            lines = f.readlines()
            for cursorLine, l in enumerate(lines):
                while ">" in l:
                    l = l.replace("\n", "")
                    indexEnd = l.find(">")
                    indexStart = l.rfind("<", 0, indexEnd) + 1
                    if len(l[indexStart:indexEnd]) == 0:
                        continue
                    t = Tag(l[indexStart:indexEnd])
                    t.line = cursorLine
                    t.start = indexStart
                    t.end = indexEnd
                    tags.append(t)
                    l = l[indexEnd + 1:]
        return tags
    def __repr__(self):
        return "{} - {}".format(self.type, self.state)

class Balise():
    def __init__(self, parent=None, tag=None):
        self.childrens = []
        self.content = None
        self.parent = None
        self.setParent(parent)
        if tag is None:
            self.arguments = None
            self.type = None
            return
        self.tagStart = tag
        self.tagEnd = None
        self.type = tag.type
        self.arguments = tag.arguments

    def setParent(self, parent):
        if self.parent is not None:
            if isinstance(self.parent, Balise):
                self.parent.childrens.remove(self)
        self.parent = parent
        if isinstance(self.parent, Balise):
            self.parent.childrens.append(self)

    @staticmethod
    def getStrFromFileByIndex(filePath, indexLine, start, end):
        with open(filePath, "r+") as f:
            for i, line in enumerate(f.readlines()):
                if i == indexLine:
                    return line[start + 1:start + end]

    @staticmethod
    def read(filePath):
        tags = Tag.read(filePath)
        currentParent = Balise(None)
        gap = 0
        for t in tags:
            if t.state == "start":
                b = Balise(currentParent, t)
                currentParent = b
                gap += 1
            elif t.state == "orphelin":
                b = Balise(currentParent, t)
            elif t.state == "end":
                currentParent.tagEnd = t
                if len(currentParent.childrens) == 0:
                    currentParent.content = Balise.getStrFromFileByIndex(filePath, currentParent.tagStart.line, currentParent.tagStart.end, currentParent.tagEnd.start)
                currentParent = currentParent.parent
                gap -= 1

        return currentParent
    
    def __iter__(self):
        self._it = 0
        return self

    def __next__(self):
        if self._it < len(self.childrens):
            res = self.childrens[self._it]
            self._it += 1
            return res
        else:
            raise StopIteration


    def __getitem__(self, i):
        return self.childrens[i]

    def printChildrens(self, gap=0):
        print("  " * gap + str(self.type) + " - " + str(self.arguments))
        if len(self.childrens) != 0:
            for c in self:
                c.printChildrens(gap + 1)
        elif self.content is not None:
            print("{}[{}]".format("  " * (gap + 1),str(self.content)))

class Role():
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.lines = []

    def countParolTime(self):
        time = None
        for l in self.lines:
            for t in l.text:
                txt = t[2]
                txt = txt.split()
                if len(txt) != 0:
                    if time is None:
                        time = datetime.strptime(t[1], '%H:%M:%S:%f') - datetime.strptime(t[0], '%H:%M:%S:%f')
                    else:
                        time += datetime.strptime(t[1], '%H:%M:%S:%f') - datetime.strptime(t[0], '%H:%M:%S:%f')
        return time
    @staticmethod
    def getRoles(balises):
        if balises.type != "roles":
            return
        roles = {}
        for b in balises:
            if b.type == "role":
                l = Role(b.arguments['name'], b.arguments['color'])
                roles[b.arguments['id']] = l
        return roles
    def __repr__(self):
        return "{} - {}".format(self.name, self.color)


class Line():
    def __init__(self, role):
        self.role = role
        self.timecode = 0
        self.track = 0
        self.text = []
        #[timecodeStart, timecodeEnd, type, text]
    
    @staticmethod
    def getTexts(balise):
        if balise.type != "line":
            return
        texts = []
        oldT = None
        t = None
        for b in balise:
            if b.type == "lipsync":
                oldT = t
                t = [b.arguments['timecode'], None, "", b.arguments['type']]
                if oldT is not None:
                    oldT[1] = b.arguments['timecode']
                    texts.append(oldT)
            if b.type == "text":
                t[2] = t[2] + b.content
        return texts


    @staticmethod
    def getLines(balises, roles):
        if balises.type != "body":
            return
        for b in balises:
            if b.type == "line":
                r = b.arguments['role']
                l = Line(roles[r])
                roles[r].lines.append(l)
                l.track = b.arguments['track']
                l.text = Line.getTexts(b)
                l.timecode = l.text[0][0]

# filePath = r".\ToolBox\sandbox\bandeRythmo\template\Le roi lion - Scar et les hyènes.detx"
# filePath = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\banderythmo\Robots.meet_the_rusties.detx"
# balises = Balise.read(filePath)
# balises.printChildrens()
# roles = Role.getRoles(balises[0][1])
# print(">", roles)
# Line.getLines(balises[0][2], roles)
# for _, r in roles.items():
#     print(">>", r, r.countParolTime())

from tkinter import Tk
from tkinter.filedialog import askdirectory
folder = askdirectory(title='Select Folder') # shows dialog box and return the path
# folder = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\banderythmo"
print(folder)
with open("./temps_de_Parol.txt", "w+") as log:
    for files in os.listdir(folder):
        if not files.endswith(".detx"):
            continue
        print(files)
        log.write("{}\n".format(files))
        balises = Balise.read(os.path.join(folder, files))
        roles = Role.getRoles(balises[0][1])
        Line.getLines(balises[0][2], roles)
        for _, r in roles.items():
            print(">> {} {}".format(r.name.ljust(20), r.countParolTime()))
            log.write("  >> {} {}\n".format(r.name.ljust(20), r.countParolTime()))
        log.write("\n ")
    
