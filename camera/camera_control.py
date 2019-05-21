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

import hamamatsu_camera as hc



class MainCamera(HamamatsuCameraMR):
    def __init__(self):
        self.camera_id = camera_id
        self.camera_model = hc.HamamatsuCamera(camera_id=0)
        self.hcam = hc.HamamatsuCameraMR(camera_id = 0)

        self.total_images = []

    def start_acquisition(self):
        self.hcam.startAcquisition()

    def end_acquisition(self):
        self. hcam.stopAcquisition()

    def stream_images(self, image):
        image_reshaped = image.reshape(2048, 2048)
        plt.imshow(image_reshaped, interpolation=None, cmap='gray')
        plt.draw()
        plt.pause(0.0001)
        plt.clf()

    def save_image(image, i):
        image = aframe.getData()
        np.save(file='image{}.npy'.format(str(i)), arr=image)

    def open_saved(self):
        os.chdir(os.getcwd() + '/Images/')
        images_nb = len(os.listdir())
        for i in range(images_nb):
            image = np.load('image{}.npy'.format(str(i)))
            Thread(target=stream_images(image))
        plt.close()







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
