#!/usr/bin/env python

"""
Script to control the hamamatsu camera orca v4 (ref: C13440-20CU) via the DCAM API on windows.

"""
import time
from OPTIMAQS.controller.camera.hamamatsu_camera import *

class MainCamera():
    def __init__(self):
        self.init = initCam()
        self.hcam = HamamatsuCamera(camera_id = 0)
        self.properties = self.hcam.getProperties()

    def start_acquisition(self):
        self.hcam.startAcquisition()

    def end_acquisition(self):
        self.hcam.stopAcquisition()

    def shutdown(self):
        self.hcam.shutdown()

    def write_exposure(self, value):
        self.hcam.setPropertyValue("exposure_time", value)

    def read_exposure(self):
        return self.hcam.getPropertyValue("exposure_time")[0]

    def write_binning(self, value):
        return self.hcam.setPropertyValue("binning", value) ## value can be 1, 2 or 4

    def read_binning(self):
        return self.hcam.getPropertyValue("binning")[0]

    def write_sensor_mode(self, value):
        self.hcam.setPropertyValue("sensor_mode", value) ##value can be 1, 12, 14, 16

    def read_sensor_mode(self):
        return self.hcam.getPropertyValue("sensor_mode")[0]

    def write_subarray_mode(self, value):
        self.hcam.setPropertyValue("subarray_mode", value)  ###1 OFF or 2 ON

    def read_subarray_mode(self):
        return self.hcam.getPropertyValue("subarray_mode")[0]

    def write_subarray_size(self, value_hpos, value_hsize, value_vpos, value_vsize):
        self.hcam.setPropertyValue("subarray_hpos", value_hpos)
        self.hcam.setPropertyValue("subarray_hsize", value_hsize)
        self.hcam.setPropertyValue("subarray_vpos", value_vpos)
        self.hcam.setPropertyValue("subarray_vsize", value_vsize)

    def get_subarray_size(self):
        hpos = self.hcam.getPropertyValue("subarray_hpos")[0]
        hsize = self.hcam.getPropertyValue("subarray_hsize")[0]
        vpos = self.hcam.getPropertyValue("subarray_vpos")[0]
        vsize = self.hcam.getPropertyValue("subarray_vsize")[0]
        return hpos, hsize, vpos, vsize

    def get_images(self):
        [frames, dims, times] = self.hcam.getFrames()
        # print(times)
        images = []
        for i in range(len(frames)):
            image = frames[i].getData()
            images.append(image)
        return images, times

    def get_internal_frame_rate(self):
        return self.hcam.getPropertyValue("internal_frame_rate")[0]




if (__name__ == "__main__"):
    cam = MainCamera()
    print("camera 0 model:", cam.hcam.getModelInfo(0))
    print(cam.getPropertyValue("exposure_time"))
    print(cam.read_exposure())
    print(cam.get_subarray_size)
    print(cam.get_internal_frame_rate)
    
    cam.start_acquisition()
    nb = 0
    start_time = time.time()
    for i in range(100):
        [frames, times] = cam.get_images()
        nb += 1
        print(frames)
    end_time = time.time()
    cam.end_acquisition()
    print('FPS is ' + str(nb/(end_time-start_time)))
    


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
