# from libraryA import toolsA

# toolsA.plop()

import zipimport

# importer = zipimport.zipimporter(r"ToolBox\sandbox\testZipResource\Rescource.zip")
importer = zipimport.zipimporter(r"ToolBox\sandbox\testZipResource\Rescource\libraryA.zip")

for module_name in [ 'libraryA', 'libraryB' ]:
    print(module_name, ':', importer.find_module(module_name))