
# standard imports
import json
import time
import os

## custom package
from OPTIMAQS.utils.json_functions import jsonFunctions



## this needs to be rewritten so that import can work in both automation and main.

def initialize_experiment(self):
    """
    Initialize/Reinitilize experiment logfiles and variables
    """
    ## reinitilize JSON files
    self.init_log_dict()

    self.images = []
    self.image_list = []
    self.image_reshaped = []
    self.ephy_data = []

    ## init perf_counter for timing events
    self.perf_counter_init = time.perf_counter()
    jsonFunctions.write_to_json(self.perf_counter_init, 'OPTIMAQS/config_files/perf_counter_init.json')

    ## generate folder to save the data
    self.path = self.path_init
    self.path_raw_data = self.path + '\\raw_data'
    date = time.strftime("%Y_%m_%d")
    self.path = os.path.join(self.path, date)
    if not os.path.exists(self.path):
        os.makedirs(self.path) ## make a folder with the date of today if it does not already exists
    n = 1
    self.path_temp = os.path.join(self.path, 'experiment_' + str(n))  ## in case of multiple experiments a day, need to create several subdirectory
    while os.path.exists(self.path_temp):                             ## but necesarry to check which one aleady exists
        n += 1
        self.path_temp = os.path.join(self.path, 'experiment_' + str(n))
    self.path = self.path_temp
    self.path_raw_data = self.path + '\\raw_data'
    os.makedirs(self.path)
    os.makedirs(self.path + '\\dlp_images')
    os.makedirs(self.path + '\\raw_data')
    jsonFunctions.write_to_json(self.path, 'OPTIMAQS/config_files/last_experiment.json')

    ## generate log files
    self.info_logfile_path = self.path + "/experiment_{}_info.json".format(n)
    experiment_time = time.asctime(time.localtime(time.time())) 
    self.info_logfile_dict['experiment creation date'] = experiment_time
#        with open(self.info_logfile_path,"w+") as file:       ## store basic info and comments
#            json.dump(self.info_logfile_dict, file)
    jsonFunctions.write_to_json(self.info_logfile_dict, self.info_logfile_path)

    self.timings_logfile_path = self.path + "/experiment_{}_timings.json".format(n)
#        with open(self.timings_logfile_path, "w+") as file:
#            json.dump(self.timings_logfile_dict, file)
    jsonFunctions.write_to_json(self.timings_logfile_dict, self.timings_logfile_path)

    self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI




def init_log_dict(self):
    """
    Initialize dictionaries that will populate the json files saving info
    and timings
    """
    ## initilizing dict for timings
    self.timings_logfile_dict = {}
    self.timings_logfile_dict['timer_init'] = {}
    self.timings_logfile_dict['timer_init']['main'] = []
    self.timings_logfile_dict['timer_init']['camera'] = []
    self.timings_logfile_dict['timer_init']['dlp'] = []
    self.timings_logfile_dict['timer_init']['laser'] = []
    self.timings_logfile_dict['timer_init']['ephy'] = []
    self.timings_logfile_dict['timer_init']['ephy_stim'] = [] # do I need this one ?
    self.timings_logfile_dict['laser'] = {}
    self.timings_logfile_dict['laser']['on'] = []
    self.timings_logfile_dict['laser']['off'] = []
    self.timings_logfile_dict['dlp'] = {}
    self.timings_logfile_dict['dlp']['on'] = []
    self.timings_logfile_dict['dlp']['off'] = []
    self.timings_logfile_dict['camera'] = []
    self.timings_logfile_dict['camera_bis'] = []
    self.timings_logfile_dict['ephy'] = {}
    self.timings_logfile_dict['ephy']['on'] = []
    self.timings_logfile_dict['ephy']['off'] = []
    self.timings_logfile_dict['ephy_stim'] = {}
    self.timings_logfile_dict['ephy_stim']['on'] = []
    self.timings_logfile_dict['ephy_stim']['off'] = []
    ## initilizing dict for info
    self.info_logfile_dict = {}
    self.info_logfile_dict['experiment creation date'] = None
    self.info_logfile_dict['roi'] = []
    self.info_logfile_dict['exposure time'] = []
    self.info_logfile_dict['binning'] = []
    self.info_logfile_dict['fov'] = []
    self.info_logfile_dict['fps'] = []
    
    