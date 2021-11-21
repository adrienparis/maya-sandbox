import os
path = r"S:\a.paris\Atelier\Macaru\03_work\maya\scenes\assets\chars\macaru\mod\wip\images"
for e in os.listdir(path):
    if "mod" in e:
        continue
    n = e[:9] + "_mod" + e[9:]
    print(n)
    os.rename(os.path.join(path, e), os.path.join(path, n))
