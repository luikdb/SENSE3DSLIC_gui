from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

def show_splash_screen(mainWin):
    splash_pix = QPixmap('splash.png')
    splash_pix = splash_pix.scaled(splash_pix.width() // 2, splash_pix.height() // 2, Qt.KeepAspectRatio)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    progressBar = QProgressBar(splash)
    progressBar.setStyleSheet("""
        QProgressBar {
            border: 2px solid #141414;
            border-radius: 6px;
            text-align: center;
            color: #000;
            background: #E0E0E0;
        }
        QProgressBar::chunk {
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0, 
                stop:0 #bdff50, stop:1 #74a319);
            border-radius: 6px;
        }
    """)
    progressBar.setGeometry(46, splash_pix.height() - 260, splash_pix.width() - 510, 20)
    splash.show()

    def update_progress():
        value = progressBar.value()
        if value < 100:
            progressBar.setValue(value + 1)
        else:
            progressTimer.stop()
            splash.close()
            mainWin.show()

    progressTimer = QTimer()
    progressTimer.timeout.connect(update_progress)
    progressTimer.start(50)

    return splash
