import re

class Balise():
    def __init__(self, content) -> None:
        self.content = content

    @staticmethod
    def read(path):
        currentParent = tag(None, "main")
        balises = []
        with open(path, "r+") as f:
            lines = f.readlines()
            last_opening = 0
            for l in lines:
                l = l.replace("\n", "")
                indexEnd = l.find(">")
                indexStart = l.rfind("<", 0, indexEnd)



class tag():
    def __init__(self, parent, type):
        self.parent = parent
        self.type = type
        self.arguments = {}

    def AddArgument(self, argument):
        name = argument
        self.arguments

    @staticmethod
    def read(path):
        currentParent = tag(None, "main")
        with open(path, "r+") as f:
            lines = f.readlines()
            for l in lines:
                l = l.replace("\n", "")
                indexEnd = l.find(">")
                indexStart = l.rfind("<", 0, indexEnd)

                indexStart = l.find("<")
                indexEnd = l[indexStart + 1:].find(">")

                indexStart = 1
                while indexStart > 0:
                    indexStart = l.find("<") + 1
                    indexEnd = l[indexStart:].find(">")
                    # print(l[indexStart + 1: indexEnd])
                    orphelin = True if l[indexStart: indexEnd].endswith("/") else False 
                    end = True if l[indexStart: indexEnd].startswith("/") else False
                    tmp = l[indexStart:indexEnd]
                    balise = l[indexStart + (1 * end):indexEnd - 1 * orphelin].split(" ")
                    print("{}\t{}\t\t\t\t(-{}-)\t(-{}-)".format(";" if orphelin else "!" if end else "@", balise, tmp, bytes(l, "utf8")))
                    # if t.startswith("/"):
                    #     type_ = re.split('[^a-zA-Z]', t)[1]
                    #     print("close", currentParent.type, type_, currentParent.parent.type)
                    #     currentParent = currentParent.parent
                    # else:
                    #     currentParent = tag(currentParent, re.split('[^a-zA-Z]', t)[0])
                    #     print("open", currentParent.type)
                    l = l[indexEnd + 1:]

filePath = r".\ToolBox\sandbox\bandeRythmo\template\Le roi lion - Scar et les hyènes.detx"
tag.read(filePath)
