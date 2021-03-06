# OPTIMAQS: WhOle-oPTical IMaging AcQuisition Software


GUI to control the hardware setup in the Reyes lab at NYU.

This software allows for the control of a whole optical electrophysiology hardware based on voltage-sensitive-dye-indicator and optogenetic stimulation. The hardware involved a microscope, its controller, a laser, a dlp and a camera as well as more classical electrophysiological hardware. 

This software is under development and release are for now quite unstable. Code is subject to major changes. 



**Changelog (brief):**

Version 0.4
* Full refactorisation following MVC pattern
* Added licence, requirement and setup files for packaging and pypi release
* Adding functionnality (dlp in hdmi streaming mode ...)
* Bug fixes



**To install with anaconda**
~~~
conda env create --file environment.yml 
conda activate OPTIMAQS
git clone git@github.com:jeremyforest/whole_optic_gui.git
cd whole_optic_gui
pip install -e .
~~~


**To run:**
~~~
conda activate OPTIMAQS
python OPTIMAQS/view/main/main.py
~~~

