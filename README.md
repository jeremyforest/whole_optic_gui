# whole_optic_gui


GUI to control the microscopy setup in the lab.
================================================

**Changelog (brief):**

**Version 0.3 \** \
Logging, threading, more bug fixes
* Implemented dlp, laser, camera image timing data logging for hardware synchronization and averaging of traces
* Implemented threading for DLP and camera controls
* Various bug fixes and moving code around
* Modified the slider for the exposure time
* Implemented absolute coordinate label for the microscope control
* Started working on some automation for experiment designs
* Started implementing signals for global synchronization
* Fixed camera acquisition not working properly for custom FOV being non-square images
* Started woking on dlp hdmi implementation
* minimally working implementation of classical electrophysiology system

Version 0.2.2 \
More bug fixes
* Fixed several bug fixes for normal function of the program
* Also modified the on/off frequency control of the dlp to load in the dlp when selecting the image

Version 0.2.1 bug fixes \
The merge to 0.2 induced a lot of bugs that needed fixing.
* Corrected the added text from the merge done wrong.
* Fixed the snap_image function
* Fixed the save function
* Included x_init and y_init in initializing hardware
* Fixed typos
* Made the ROI works for smaller FOV (subarray function)
* Subarray size function: writing new subarray two times to camera as one time sometimes does not update correctly
* Implemented on/off frequency control for the dlp
* Implemented stop stream button

Version 0.2  \
DLP major implementations
* Interface redesign. Major rewrite / implementation of DLP functions and its interface with the camera.
* Added the possibility for the DLP to only illuminate subregions of the field of vue which is controlled from the ROI interface of the camera.

Version 0.1.3
* Minor bug correction.
* Stream function not working, last update broke the reshaping. Fixed it.

Version 0.1.2
* Binning function was bugged because there was a need to adjust the redimention of the image array due to the change in the number of pixel. Fixed
* Implemented the function to reduce the FOV of the camera. Still kind of temporary the way its coded as it is a manual encoded delimitation and I want to later be able to pass it through the ROI delimitation of the main pyqtgraph screen.
* Added a button to initialize the hardware: basically gets all the parameters of the camera for now.

Version 0.1.1
* Put save function at the end of the stream function as it was taking too much time to save during steam
* Rrewrote a bit the save function as a consequence
