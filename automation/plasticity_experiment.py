
'''
steps needed
1. Define ROI in the GUI that are then saved for later reuse.
        Need ROI for test portion and ROI for sync stim stored in json and imported here
2. Test :
    Need specific order of hardware activation:
            laser on at t=0s
            camera on at t=1s
            dlp ROI stim starts at t= 2s for a specific frequency f
            camera off 200 ms after dlp finishes
            laser off 20 ms after camera

3. Inducing plasticity:
    Need custom but dynamic dlp activation on ROIs with parameters:
        - duration ON
        - duration OFF
        - number of repetition
        - interstimulation interval



'''


import numpy as np

Class PlasticityExperiment(camera, dlp, laser, controler):
    def __init__(self):
        super().__init__()
        self.camera = camera
        self.dlp = dlp
        self.laser = laser
        # self.controler = controler

    def import_ROI(self, path_json_file):
        """Import ROIs from the JSON file where their coordinates
        were saved with the GUI """
        roi = []
        return roi


    def dlp_auto_stim(self, dlp_on, dlp_off, dlp_sequence, dlp_repeat_sequence, dlp_interval):
        for i in range(dlp_repeat_sequence):
            for j in range(dlp_sequence):
                ## OFF
                self.dlp.set_display_mode('internal')
                self.dlp.black()
                time.sleep(dlp_off/1000)
                ## ON
                self.dlp.set_display_mode('static')
                time.sleep(dlp_on/1000)
            time.sleep(dlp_interval/1000)

    def test_protocol(self, dlp_on, dlp_off, dlp_repeat, dlp_interval):
        """ General protocol used in the plasticity experiment. This is
        general enough to allow multiple parameters. The specific considered
        protocol is written down as a JSON file when running the experiment"""

        self.laser.turn_on()
        time.sleep(1)

        self.camera.start_acquisition()
        self.stream(500)
        time.sleep(1)

        self.dlp_auto_stim(dlp_on, dlp_off, dlp_repeat, dlp_interval)
        time.sleep(200/1000)

        self.camera.end_acquisition()
        time.sleep(20/1000)

        self.laser.turn_off()


    def train_protocol(self, dlp_on, dlp_off, dlp_repeat, dlp_interval):
        self.dlp.stim(dlp_on, dlp_off, dlp_repeat, dlp_interval)


    def save_protocol():
        self.experiment_info = {}

        self.experiment_info['camera'] = {}
        self.experiment_info['camera']['on'] = []
        self.experiment_info['camera']['off'] = []

        self.experiment_info['dlp'] = {}
        self.experiment_info['dlp']['on'] = []
        self.experiment_info['dlp']['off'] = []

        self.experiment_info['laser'] = {}
        self.experiment_info['laser']['on'] = []
        self.experiment_info['laser']['off'] = []

        self.experiment_info['controler_position'] = {}
        self.experiment_info['roi_coord'] = {}

    def load_protocol():
        pass
