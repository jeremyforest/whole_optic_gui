from PyQt5.QtWidgets import QApplication
import time

def custom_sleep_function(ms):
    c = time.perf_counter()
    while (time.perf_counter() - c)*1000 < ms:
        QApplication.processEvents()   #### this should probably be put in its own thread to avoid forcing gui update
    return (time.perf_counter() - c)*1000
