import unittest
# from OPTIMAQS.controller.camera.hamamatsu_camera import HamamatsuCamera, initCam

class TestCamera(unittest.TestCase):
    def test_connection(self):
        """Test if the camera is present"""
        connection = initCam()
        self.assert  connection =! None
