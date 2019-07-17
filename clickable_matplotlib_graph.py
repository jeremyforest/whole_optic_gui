### modified from https://stackoverflow.com/questions/28758079/python-how-to-get-coordinates-on-mouse-click-using-matplotlib-canvas

import cv2
import matplotlib.pyplot as plt

class Clickable_matplotlib_graph():
    def __init__(self, calibration_image_path):
        self.dlp_image = calibration_image_path
        self.img = cv2.imread(self.dlp_image)
        self.points = []

    def getCoord(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(self.img)
        cid = fig.canvas.mpl_connect('button_press_event', self.__onclick__)
        plt.show()
        return self.points

    def __onclick__(self,click):
        self.point = [click.xdata,click.ydata]
        return self.points.append(self.point)


if __name__== '__main__':
    graph = Clickable_matplotlib_graph()
    coords = graph.getCoord()
    print(coords)
    print(len(coords))
