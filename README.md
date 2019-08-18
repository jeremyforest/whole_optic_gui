# whole_optic_gui


GUI to control the microscopy setup in the lab.


Changelog

Version 0.1.3
Minor bug correction.
- Stream function not working, last update broke the reshaping. Fixed it. 


Version 0.1.2
- binning function was bugged because there was a need to adjust the redimention of the image array due to the change in the number of pixel. Fixed
- implemented the function to reduce the FOV of the camera. Still kind of temporary the way its coded as it is a manual encoded delimitation and I want to later be able to pass it through the ROI delimitation of the main pyqtgraph screen.
- added a button to initialize the hardware: basically gets all the parameters of the camera for now.


Version 0.1.1

- put save function at the end of the stream function as it was taking too much time to save during steam
- rewrote a bit the save function as a consequence
