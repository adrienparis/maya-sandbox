path = r"D:\a.paris\Atelier\macaru\03_work\maya\scenes\assets\chars\macaru\mod\cs_macaru.ma"

with open(path) as f:
    v = f.read().find("publisher_metadata")
    f.seek(v)
    lines = []
    for i in range(0, 50):
        l = f.readline()
        if "setAttr" in l:
            break
    while "setAttr" in l:
        lines.append(l)
        l = f.readline()

    dict = {}
    for l in lines:
        ws = l.split('"')
        dict[ws[1][1:]] = ws[5]
    for k, v in dict.items():
        print("{} : {}".format(k, v))