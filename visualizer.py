import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QSlider)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StackedImageVisualizer(QMainWindow):
    def __init__(self, directory):
        super().__init__()
        self.image_path = directory
        self.namelist = [file for file in os.listdir(self.image_path) if file.endswith('.tif')]
        self.length_of_namelist = len(self.namelist)
        self.mean_bright = np.zeros((self.length_of_namelist, 1))
        self.median_bright = np.zeros((self.length_of_namelist, 1))
        self.larger_100 = np.zeros((self.length_of_namelist, 1))
        self.setWindowIcon(QIcon('transparentlogo.png'))
        sample_img = cv2.imread(os.path.join(self.image_path, self.namelist[0]))
        self.rows, self.cols, self.channels = sample_img.shape
        self.stacked = np.zeros((self.rows, self.cols, self.channels, self.length_of_namelist), dtype=sample_img.dtype)

        for i, file_name in enumerate(self.namelist):
            img = cv2.imread(os.path.join(self.image_path, file_name))
            image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.mean_bright[i, 0] = np.mean(image_gray[image_gray > 0])
            self.median_bright[i, 0] = np.median(image_gray[image_gray > 0])
            self.larger_100[i, 0] = np.sum(image_gray >= 100)
            self.stacked[:, :, :, i] = img

        self.location1 = np.argmax(self.mean_bright)
        self.location2 = np.argmax(self.median_bright)
        self.location3 = np.argmax(self.larger_100)
        self.stacked = np.transpose(self.stacked, (3, 0, 1, 2))

        self.setWindowTitle("SENSE")
        self.stacked_widget = StackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        self.setWindowIcon(QIcon(''))

class StackedWidget(QWidget):
    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.parent().length_of_namelist - 1)
        self.slider.setValue(0)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.update_image)
        layout.addWidget(self.slider)

        self.layer_label = QLabel("Layer: 0")
        layout.addWidget(self.layer_label)

        self.update_image()

    def update_image(self):
        layer = self.slider.value()
        self.ax.clear()
        self.ax.imshow(cv2.cvtColor(self.parent().stacked[layer], cv2.COLOR_BGR2RGB))
        self.layer_label.setText(f"Layer: {layer}")
        self.canvas.draw()
