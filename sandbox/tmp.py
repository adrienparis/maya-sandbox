import os

def CheckPermission(path):
    tmpFile = os.path.join(path, ".CheckPermissionTmp")
    try:
        f = open(tmpFile, "w+")
        f.write("test")
    except:
        return False
    os.remove(tmpFile)
    return True

# for i in range(1, 6):
#     path = r'Q:\annee0{}\rendusAteliers'.format(i)
#     print(path, os.access(path, os.W_OK))

print(CheckPermission(r'Q:\annee01\rendusAteliers'))