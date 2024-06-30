import sys
from PyQt5.QtWidgets import QApplication
from ui import VolumeRenderingApp
from splash import show_splash_screen

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = VolumeRenderingApp()
    splash = show_splash_screen(mainWin)
    sys.exit(app.exec_())
