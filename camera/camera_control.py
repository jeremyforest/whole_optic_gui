#!/usr/bin/env python

"""
Script to control the hamamatsu camera orca v4 (ref: C13440-20CU) via the DCAM API on windows.

"""

import ctypes
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from threading import Thread

from camera.hamamatsu_camera import *




class MainCamera():
    def __init__(self):
        self.init = initCam()
        self.hcam = HamamatsuCameraMR(camera_id = 0)

        self.total_images = []
        self.properties = self.hcam.getProperties()

    def start_acquisition(self):
        self.hcam.startAcquisition()

    def end_acquisition(self):
        self.hcam.stopAcquisition()

    def exposure(self, value):
        self.hcam.setPropertyValue("exposure_time", value)

    #### need to integrate the list of all the modifiable properties here ####

    def stream_images(self):
#        nb = 0
#        start_time = time.time()
#        for i in range(1000):
        [frames, dims] = self.hcam.getFrames()
        image = frames[0].getData()
#            self.total_images.append(image)
#        nb += 1
        image_reshaped = image.reshape(2048, 2048)

#            plt.imshow(image_reshaped, interpolation=None, cmap='gray')
#            plt.draw()
#            plt.pause(0.0001)
#            plt.clf()
        return image_reshaped


    def save_image(self, image, i): ### npy format
        for i in self.total_images:
            image = self.total_images[i].getData()
            np.save(file='image{}.npy'.format(str(i)), arr=image)

#     def open_saved(self, path): ### open with pyplot
#         path_files = path
#         images_nb = len(os.listdir(path))
#         images = []
#         for i in range(images_nb):
#             image = np.load(str(path_files) + 'image{}.npy'.format(str(i)))
# #            Thread(target=self.stream_images(image))
#             image_reshaped = image.reshape(2048, 2048)
#             images.append(image_reshaped)
# #        plt.close()
#         return images

if (__name__ == "__main__"):
    #MainCamera().open_saved(path='/media/jeremy/Data/CloudStation/Postdoc/Project/Memory project/optopatch/equipment/camera/Images/')
    cam = MainCamera()
    cam.stream_images()
#    cam.open_saved('C:\\Users\\barral\\Desktop\\camera\\data\\')
    print("camera 0 model:", cam.hcam.getModelInfo(0))



"""
## Testing purposes

hcam = hc.HamamatsuCameraMR(camera_id = 0)
#hcam = HamamatsuCamera(camera_id = 0)  ### too slow
# print(hcam.setPropertyValue("defect_correct_mode", 1))
print("camera model:", hcam.getModelInfo(0))



def stream_images(image):
#    elapsed_time = time.time()
    image_reshaped = image.reshape(2048, 2048)
    plt.imshow(image_reshaped, interpolation=None, cmap='gray')
    plt.draw()
    plt.pause(0.0001)
    plt.clf()
#    print ('time for imaging: ' + str(time.time() - elapsed_time))

def save_image(image, i):
    image = aframe.getData()
    np.save(file='image{}.npy'.format(str(i)), arr=image)
#    image.tofile('image{}'.format(str(cnt))) ## is not platform independant but might be faster




total_images = []

if (__name__ == "__main__"):

    print("found:", n_cameras, "cameras")
    if (n_cameras > 0):
        print("Testing run till abort acquisition")
    os.chdir('C:\\Users\\barral\\Desktop\\camera\\data')
    print('saving data in ' + str(os.getcwd()))
    hcam.startAcquisition()
    nb = 0
    start_time = time.time()
    for i in range(100):
        [frames, dims] = hcam.getFrames()
        image = frames[0].getData()
        Thread(target=stream_images(image))
        total_images.append(image)
        nb += 1
    plt.close()

#    print("Frames acquired: " + str(cnt))
    end_time = time.time()
    hcam.stopAcquisition()
    print('FPS is' + str(nb/(end_time-start_time)))
    for i in range(len(total_images)):
        np.save(file='image{}.npy'.format(str(i)), arr=total_images[i])

"""
