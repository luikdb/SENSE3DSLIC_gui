import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QFileDialog, QLabel, QHBoxLayout, QMainWindow, 
                             QSlider, QStackedWidget, QDesktopWidget, QLineEdit, 
                             QComboBox, QFormLayout, QSpinBox, QProgressDialog)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PIL import Image
from visualizer import StackedImageVisualizer
from mayavi import mlab
from sense_v2 import perform_cell_counting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CellCountingThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("Image histogram matching is running...")
        # Execute cell counting algorithm
        num_cells = perform_cell_counting(**self.params)
        self.finished.emit(num_cells)

class VolumeRenderingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        self.setWindowTitle('SENSE - Cell Counting at Ease')
        icon_path = 'transparentlogo.png'
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon file {icon_path} not found")
        self.setGeometry(700, 100, 800, 600)
        self.center()

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QHBoxLayout(self.mainWidget)
        
        self.sidebar = QWidget(self)
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #282b30;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #3B4252;
                color: white;
                border: none;
                padding: 10px;
                margin: 5px 5px;
                border-radius: 5px;
                font-size: 16px;
                font-family: Arial;
            }
            QPushButton:hover {
                background-color: #4C566A;
            }
            QPushButton:pressed {
                background-color: #D08770;
            }
        """)
        
        self.sidebarLayout = QVBoxLayout(self.sidebar)
        self.homeButton = QPushButton('Home')
        self.homeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.homeButton.clicked.connect(self.show_home)
        self.sidebarLayout.addWidget(self.homeButton)

        self.visualizerButton = QPushButton('Visualizer')
        self.visualizerButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.visualizerButton.clicked.connect(self.show_visualizer)
        self.sidebarLayout.addWidget(self.visualizerButton)

        self.cellCountButton = QPushButton('Cell Counting')
        self.cellCountButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.cellCountButton.clicked.connect(self.show_cell_counting)
        self.sidebarLayout.addWidget(self.cellCountButton)

        self.sidebarLayout.addStretch(1)

        self.content = QStackedWidget(self)
        self.homeWidget = QWidget()
        self.visualizerWidget = QWidget()
        self.cellCountingWidget = QWidget()
        
        self.initHomeUI()
        self.initVisualizerUI()
        self.initCellCountingUI()

        self.content.addWidget(self.homeWidget)
        self.content.addWidget(self.visualizerWidget)
        self.content.addWidget(self.cellCountingWidget)
        
        self.mainLayout.addWidget(self.sidebar)
        self.mainLayout.addWidget(self.content)

        self.show_home()

    def initHomeUI(self):
        layout = QVBoxLayout(self.homeWidget)

        self.titleLabel = QLabel('SENSE')
        self.titleLabel.setFont(QFont('Monument Extended', 32, QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.titleLabel)
        
        self.descLabel = QLabel('Simplifying Cell Analysis in 3D')
        self.descLabel.setFont(QFont('Arial', 13))
        self.descLabel.setAlignment(Qt.AlignCenter)
        self.descLabel.setStyleSheet('color: #555555')
        layout.addWidget(self.descLabel)

        self.loadButton = QPushButton('Browse your files')
        self.loadButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.loadButton.clicked.connect(self.load_slices)
        self.loadButton.setStyleSheet("""
            QPushButton {
                background-color: #8DE800;
                color: black;
                padding: 15px 15px;
                font-size: 20px;
                margin: 20px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #8bc221;
            }
        """)
        self.loadButton.setFixedSize(290, 90)

        layout.addWidget(self.loadButton, alignment=Qt.AlignCenter)

        self.statusLabel = QLabel('')
        self.statusLabel.setFont(QFont('Arial', 7))
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet('color: #808080;')
        layout.addWidget(self.statusLabel)

    def initVisualizerUI(self):
        layout = QVBoxLayout(self.visualizerWidget)

        self.visualizationButtonsLayout = QHBoxLayout()

        self.visualize2DButton = QPushButton('Visualize 2D Slices')
        self.visualize2DButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.visualize2DButton.clicked.connect(self.visualize_2d_slices)
        self.visualize2DButton.setStyleSheet("""
            QPushButton {
                background-color: #015f9b;
                color: white;
                padding: 15px 15px;
                font-size: 16px;
                margin: 20px;
                border-radius: 13px;
            }
            QPushButton:hover {
                background-color: #023555;
            }
        """)
        self.visualize2DButton.setFixedSize(250, 100)

        self.visualize3DButton = QPushButton('Visualize 3D Volume')
        self.visualize3DButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.visualize3DButton.clicked.connect(self.visualize_3d_volume)
        self.visualize3DButton.setStyleSheet("""
            QPushButton {
                background-color: #015f9b;
                color: white;
                padding: 15px 15px;
                font-size: 16px;
                margin: 20px;
                border-radius: 13px;
            }
            QPushButton:hover {
                background-color: #023555;
            }
        """)
        self.visualize3DButton.setFixedSize(250, 100)

        self.visualizationButtonsLayout.addWidget(self.visualize2DButton, alignment=Qt.AlignCenter)
        self.visualizationButtonsLayout.addWidget(self.visualize3DButton, alignment=Qt.AlignCenter)

        layout.addLayout(self.visualizationButtonsLayout)
        self.statusLabel = QLabel('')
        self.statusLabel.setFont(QFont('Arial', 7))
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet('color: #808080;')
        layout.addWidget(self.statusLabel)

    def initCellCountingUI(self):
        layout = QVBoxLayout(self.cellCountingWidget)

        formLayout = QFormLayout()

        self.filenameTemplateEdit = QLineEdit('HepaRG_n1 P3 D7_1000_4_C001Z{:03d}.tif')
        formLayout.addRow('Filename Template:', self.filenameTemplateEdit)

        self.referTypeCombo = QComboBox()
        self.referTypeCombo.addItems(['mean', 'median', 'larger100'])
        formLayout.addRow('Reference Type:', self.referTypeCombo)

        self.numOfSupervoxelSpin = QSpinBox()
        self.numOfSupervoxelSpin.setRange(1, 100000)
        self.numOfSupervoxelSpin.setValue(25000)
        formLayout.addRow('Number of Supervoxels:', self.numOfSupervoxelSpin)

        self.compactnessSpin = QSpinBox()
        self.compactnessSpin.setRange(1, 1000)
        self.compactnessSpin.setValue(50)
        formLayout.addRow('Compactness:', self.compactnessSpin)

        self.atLeastBrightSpin = QSpinBox()
        self.atLeastBrightSpin.setRange(1, 255)
        self.atLeastBrightSpin.setValue(10)
        formLayout.addRow('At Least Bright:', self.atLeastBrightSpin)

        self.atLeastVolSpin = QSpinBox()
        self.atLeastVolSpin.setRange(1, 100000)
        self.atLeastVolSpin.setValue(800)
        formLayout.addRow('At Least Volume:', self.atLeastVolSpin)

        self.thresholdSpin = QSpinBox()
        self.thresholdSpin.setRange(0, 255)
        self.thresholdSpin.setValue(40)
        formLayout.addRow('Threshold:', self.thresholdSpin)

        self.widthSpin = QSpinBox()
        self.widthSpin.setRange(1, 4096)
        self.widthSpin.setValue(512)
        formLayout.addRow('Width:', self.widthSpin)

        self.heightSpin = QSpinBox()
        self.heightSpin.setRange(1, 4096)
        self.heightSpin.setValue(512)
        formLayout.addRow('Height:', self.heightSpin)

        self.stackNumSpin = QSpinBox()
        self.stackNumSpin.setRange(1, 100)
        self.stackNumSpin.setValue(2)
        formLayout.addRow('Stack Number:', self.stackNumSpin)

        self.cellCountButton = QPushButton('Count Cells')
        self.cellCountButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.cellCountButton.clicked.connect(self.perform_cell_counting)
        self.cellCountButton.setStyleSheet("""
            QPushButton {
                background-color: #3B4252;
                color: white;
                padding: 15px 15px;
                font-size: 16px;
                margin: 20px;
                border-radius: 13px;
            }
            QPushButton:hover {
                background-color: #4C566A;
            }
        """)
        self.cellCountButton.setFixedSize(250, 100)

        layout.addLayout(formLayout)
        layout.addWidget(self.cellCountButton, alignment=Qt.AlignCenter)

        self.statusLabel = QLabel('')
        self.statusLabel.setFont(QFont('Arial', 7))
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet('color: #808080;')
        layout.addWidget(self.statusLabel)

    def show_home(self):
        self.content.setCurrentWidget(self.homeWidget)

    def show_visualizer(self):
        self.content.setCurrentWidget(self.visualizerWidget)

    def show_cell_counting(self):
        self.content.setCurrentWidget(self.cellCountingWidget)

    def load_slices(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Select Slice Directory')
        if self.directory:
            self.statusLabel.setText(f'Selected directory: {self.directory}')
        else:
            self.statusLabel.setText('No directory selected.')

    def visualize_2d_slices(self):
        if hasattr(self, 'directory') and self.directory:
            self.visualizer = StackedImageVisualizer(self.directory)
            self.visualizer.show()
        else:
            self.statusLabel.setText('Please select a directory first.')

    def visualize_3d_volume(self):
        if hasattr(self, 'directory') and self.directory:
            slices = self.load_slices_from_directory(self.directory)
            if slices:
                volume = np.stack(slices, axis=2)
                self.render_volume(volume)
                self.statusLabel.setText('3D volume rendering complete.')
            else:
                self.statusLabel.setText('No slices were loaded. Please check the directory path and file format.')
        else:
            self.statusLabel.setText('Please select a directory first.')

    def load_slices_from_directory(self, directory):
        slices = []
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.tif'):
                filepath = os.path.join(directory, filename)
                img = Image.open(filepath).convert('L')
                slices.append(np.array(img))
        return slices

    def render_volume(self, volume):
        fig = mlab.figure(size=(800, 800), bgcolor=(0, 0, 0))
        fig.scene._title = 'SENSE - Simplifying Complex Cell Analysis'
        mlab.pipeline.volume(mlab.pipeline.scalar_field(volume), figure=fig)
        mlab.show()

    def perform_cell_counting(self):
        if hasattr(self, 'directory') and self.directory:
            filename_template = self.filenameTemplateEdit.text()
            refer_type = self.referTypeCombo.currentText()
            numOfSupervoxel = self.numOfSupervoxelSpin.value()
            compactness = self.compactnessSpin.value()
            atLeastBright = self.atLeastBrightSpin.value()
            atLeastVol = self.atLeastVolSpin.value()
            threshold = self.thresholdSpin.value()
            width = self.widthSpin.value()
            height = self.heightSpin.value()
            stack_num = self.stackNumSpin.value()

            params = {
                "image_path": self.directory,
                "refer_type": refer_type,
                "numOfSupervoxel": numOfSupervoxel,
                "compactness": compactness,
                "atLeastBright": atLeastBright,
                "atLeastVol": atLeastVol,
                "threshold": threshold,
                "width": width,
                "height": height,
                "stack_num": stack_num
            }

            self.progress_dialog = QProgressDialog("Starting cell counting...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowTitle("Cell Counting in Progress")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setValue(0)

            self.cell_counting_thread = CellCountingThread(params)
            self.cell_counting_thread.progress.connect(self.update_progress)
            self.cell_counting_thread.finished.connect(self.cell_counting_finished)
            self.cell_counting_thread.start()

            self.progress_dialog.show()
        else:
            self.statusLabel.setText('Please select a directory first.')

    def update_progress(self, message):
        self.progress_dialog.setLabelText(message)
        value = self.progress_dialog.value()
        self.progress_dialog.setValue(value + 20)  # Increment progress

    def cell_counting_finished(self, num_cells):
        self.progress_dialog.setValue(100)
        self.progress_dialog.close()
        self.statusLabel.setText(f'Number of cells counted: {num_cells}')
        self.statusLabel.setStyleSheet(
            'font-size: 18px'
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VolumeRenderingApp()
    ex.show()
    sys.exit(app.exec_())
