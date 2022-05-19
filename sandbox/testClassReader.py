

class test(object):
    get_Alpha = None
    get_Beta = None
    get_Charlie = None
    get_Delta = None


    def __getattribute__(self, __name):
        print("hey")
        if __name.startswith("get_"):
            return "Hello"
        else:
            return object.__getattribute__(self, __name)




print(test.get_Alpha)


import os
import json
from pathlib import Path


def read_prefs():
    user_folder = Path.home()
    prefs_folder = os.path.join(user_folder, "HUNTER", "prefs")
    prefs_file = os.path.join(prefs_folder, "user_pref.json")
    with open(prefs_file) as f:
        data_dict = json.load(f)
    return data_dict


def get_username():
    data = read_prefs()
    return data["username"]


def get_local_project_path():
    data = read_prefs()
    return data["local_project_path"]


def get_server_project_path():
    data = read_prefs()
    return data["server_project_path"]


def get_departement():
    data = read_prefs()
    return data["departement"]


def get_useSimLink():
    data = read_prefs()
    return data["useSimLink"]


def get_library_path():
    data = read_prefs()
    return data["library_path"]


class PreferencesObject(object):

    def __init__(self):
        # self.__init_datas()
        # self.check_global_prefs()
        # self.read_global_prefs()
        # self.__init_library_data()
        # self.read_library_prefs()
        self.__init_datas()

    def __init_datas(self):
        self.user_doc_folder = os.path.expanduser('~/Documents')
        self.user_pref_folder = os .path.join(self.user_doc_folder, "hunter", "prefs")
        self.user_pref_file = os.path.join(self.user_pref_folder, "Hlibrary.pref")
        self.user_collections_file = os.path.join(self.user_pref_folder, "user_collections.pref")
        self.__init_global_data()
        self.__init_library_data()
        self.__init_user_collections()

        self.has_lib_pref = False
    
    def __init_global_data(self):
        self.library_path = None
        self.user_name = os.getlogin()

        self.read_global_prefs()

    def __init_library_data(self):

        self.library_tags = ["wood", "character", "natural", "scifi", "texture", "rock", "paint", "cartoon", "realistic", "old", "concrete", "damaged", "plant", "3D", "2D"]

        self.base_tag = {
            "3DModels":["landscape", "characters", "weapons", "kitbash"],
            "Textures":["hdr", "bricks", "skin", "clothes", "wood"],
            "Hdr":["indoor", "outdoor"],
            "Materials":["substance", "maya", "fabric"],
            "FX": ["cloud", "smoke"],
            "Brushes":["photoshop", "Zbrush"],
            "Utilities": ["tutorial", "documents"]
            }

        self.package_preset = {

            "3DModels": {
                "infos": ["uv=yes", "maps=yes", "polycount=int", "format=str"], 
                "var_field": ["mesh", "Diffuse", "Roughness", "Normale", "Displacement"]
            },
            "Textures": {
                "infos": ["pbr=bool", "tileable=bool", "format=str"], 
                "var_field": ["Diffuse", "Roughness", "Normale", "Displacement"]
            },
            "Hdr": {
                "infos": ["type=indoor", "format"], 
                "var_field": ["file"]
            },

            "Materials": {
                "infos": ["pbr", "tileable"], 
                "var_field": ["Diffuse", "Roughness", "Normale", "Displacement"]
            },
            "FX": {
                "infos": ["animated=yes", "format"], 
                "var_field": ["file"]
            },
            "Brushes": {
                "infos": ["software", "format"], 
                "var_field": ["file"]
            },
            "Utilities": {
                "infos": ["type=video", "format"], 
                "var_field": ["file"]
            }
        }

        self.read_library_prefs()

    def __init_user_collections(self):

        self.collections = {"Favorites": []}

        self.read_user_collections()

    def read_global_prefs(self):

        # check global pref
        if not os.path.isfile(self.user_pref_file):
            self.commit_global_prefs()

        # open global prefs
        with open(self.user_pref_file) as f:
            self.global_prefs_dict = json.load(f)
        
        self.library_path = self.global_prefs_dict["library_path"]
        self.user_name = self.global_prefs_dict["user_name"]

    def read_library_prefs(self):
        if self.library_path:
            if os.path.isdir(self.library_path):
                self.library_config_path = os.path.join(self.library_path, ".config")
                self.library_tag_file = os.path.join(self.library_config_path, "lib_tags.pref")
                self.library_main_pref_file = os.path.join(self.library_config_path, "lib_packages.pref")
        # check library path
        if not self.library_path or not os.path.isdir(self.library_path):
            return
        # read tag pref if exists
        if os.path.isfile(self.library_tag_file):
            with open(self.library_tag_file) as f:
                library_tags_dict = json.load(f)
            self.library_tags = library_tags_dict["tags"]
        # read lib pref if exists
        if os.path.isfile(self.library_main_pref_file):
            with open(self.library_main_pref_file) as f:
                library_package_dict = json.load(f)
            self.base_tag = library_package_dict["base_tag"]
            self.package_preset = library_package_dict["package_presets"]
            self.collections = library_package_dict["collections"]

    def read_user_collections(self):
        if not os.path.isfile(self.user_collections_file):
            return
        with open(self.user_collections_file) as f:
            self.collections = json.load(f)

    def commit_global_prefs(self):

        if not os.path.exists(self.user_pref_folder):
            os.makedirs(self.user_pref_folder)
        
        global_dict = dict()

        global_dict["library_path"] = self.library_path
        global_dict["user_name"] = self.user_name

        with open(self.user_pref_file, "w") as f:
            json.dump(global_dict, f, indent=4, sort_keys=True)

        self.__init_datas()

    def commit_library_prefs(self):
        # check variables
        if not self.library_path:
            return
        elif not os.path.isdir(self.library_path):
            return
        # create config file if missing
        if not os.path.exists(self.library_config_path):
            os.mkdir(self.library_config_path)
        # build dict
        library_dict = dict()
        library_dict["base_tag"] = self.base_tag
        library_dict["package_presets"] = self.package_preset
        library_dict["collections"] = self.collections
        # write file
        with open(self.library_main_pref_file, "w") as f:
            json.dump(library_dict, f, indent=4, sort_keys=True)

        self.__init_library_data()

    def commit_library_tags(self):
        # check variables
        if not self.library_path:
            return
        elif not os.path.isdir(self.library_path):
            return
        # create config file if missing
        if not os.path.exists(self.library_config_path):
            os.mkdir(self.library_config_path)

        # commit library tag file (lib_tags.pref)
        library_tag_dict = dict()
        library_tag_dict["tags"] = self.library_tags
        with open(self.library_tag_file, "w") as f:
                json.dump(library_tag_dict, f, indent=4, sort_keys=True)

        self.__init_library_data()

    def commit_user_collections_prefs(self):

        if not os.path.exists(self.user_pref_folder):
            os.makedirs(self.user_pref_folder)

        with open(self.user_collections_file, "w") as f:
            json.dump(self.collections, f, indent=4, sort_keys=True)

        self.__init__()

