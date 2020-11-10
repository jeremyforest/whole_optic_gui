# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 21:34:55 2020

@author: jeremy
"""

import json, os

class jsonFunctions():
    def __init__(self):
        pass

    def write_to_json(data, file_path):
        """
        Write the data to file as json format
        """
        with open(file_path, 'w') as f:
            f.write(json.dumps(data, default=lambda x:list(x), indent=4, sort_keys=True))


    def append_to_json(data, file_path):
        """
        Write the data to file as json format
        """
        with open(file_path, 'a') as f:
            f.write(json.dumps(data, default=lambda x:list(x), indent=4, sort_keys=True))

    def find_json(file_path):
        """ 
        Does the json file exist ? 
        Return bool
        """
        return os.path.exists(file_path)
    
    def open_json(file_path):
        """
        Open json file
        """
        with open(file_path) as f:
            data = json.load(f)
        return data