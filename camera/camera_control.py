#!/usr/bin/env python

"""
Script to control the hamamatsu camera orca v4 (ref: C13440-20CU) via the DCAM API on windows.

"""


import numpy as np
import matplotlib.pyplot as plt
import os
import time
from threading import Thread

import hamamatsu_camera as hc


# dcam = ctypes.windll.dcamapi

# paraminit = DCAMAPI_INIT(0, 0, 0, 0, None, None)
# paraminit.size = ctypes.sizeof(paraminit)
# error_code = dcam.dcamapi_init(ctypes.byref(paraminit))
# if (error_code != DCAMERR_NOERROR):
#     raise DCAMException("DCAM initialization failed with error code " + str(error_code))



hcam = hc.HamamatsuCameraMR(camera_id = 0)
#hcam = HamamatsuCamera(camera_id = 0)  ### too slow
# print(hcam.setPropertyValue("defect_correct_mode", 1))
print("camera 0 model:", hcam.getModelInfo(0))



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


'''
def stream_video(image):
    image_reshaped = image.reshape(2048, 2048)
    stream = cv2.imread(image_reshaped, cv2.IMREAD_UNCHANGED) ### #try with 0, 1 ... to try and access the hamamatsu camera. If it works that would be great
    return stream

def stream_video(video):
    cap = cv2.VideoCapture(image)### #try with 0, 1 ... to try and access the hamamatsu camera. If it works that would be great
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        ret, frame = cap.read() # Capture frame-by-frame
        if not ret:  # if frame is read correctly ret is True
            print("Stream ends. Exiting ...")
            break
        cv2.imshow('frame', frame)  # Display the resulting frame
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()      # When everything done, release the capture
    cv2.destroyAllWindows()  # Exiting properly
'''

total_images = []

if (__name__ == "__main__"):

    print("found:", n_cameras, "cameras")
    if (n_cameras > 0):
        print("Testing run till abort acquisition")
    os.chdir('C:\\Users\\barral\\Desktop\\camera\\data')
    print('saving data in ' + str(os.getcwd()))
    hcam.startAcquisition()
    cnt = 0
    nb = 0
    for i in range(5000):
        [frames, dims] = hcam.getFrames()
        image = frames[0].getData()
        Thread(target=stream_images(image))
        total_images.append(image)
    plt.close()

#    print("Frames acquired: " + str(cnt))
    cv2.destroyAllWindows()  # Exiting properly
    hcam.stopAcquisition()

    for i in range(len(total_images)):
        np.save(file='image{}.npy'.format(str(i)), arr=total_images[i])

'''
os.chdir(os.getcwd() + '/Images/')
images_nb = len(os.listdir())
for i in range(images_nb):
    i=i+1
    image = np.load('image{}.npy'.format(str(i)))
    Thread(target=stream_images(image))
    plt.close()
'''
