import re


class tag():
    def __init__(self, parent, type):
        self.parent = parent
        self.type = type

    @staticmethod
    def read(path):
        currentParent = tag(None, "main")
        with open(path, "r+") as f:
            lines = f.readlines()
            for l in lines:
                indexStart = l.find("<")
                indexEnd = l[indexStart + 1:].find(">")

                indexStart = 1
                while indexStart > 0:
                    indexStart = l.find("<")
                    indexEnd = l[indexStart + 1:].find(">")
                    print()
                    balise = l[indexStart + 1:]
                    # if t.startswith("/"):
                    #     type_ = re.split('[^a-zA-Z]', t)[1]
                    #     print("close", currentParent.type, type_, currentParent.parent.type)
                    #     currentParent = currentParent.parent
                    # else:
                    #     currentParent = tag(currentParent, re.split('[^a-zA-Z]', t)[0])
                    #     print("open", currentParent.type)
                    l = l[indexEnd + 1:]

filePath = r"S:\a.paris\Rescources\ToolBox\sandbox\bandeRythmo\template\Le roi lion - Scar et les hyènes.detx"
tag.read(filePath)
