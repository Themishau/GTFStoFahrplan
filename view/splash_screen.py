from PySide6 import QtCore
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QMainWindow

from view.pyui.ui_splash_screen import Ui_SplashScreen

class SplashScreen(QMainWindow):
    def __init__(self, application_window):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.application_window = application_window
        self.progress_value = 0

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)

        self.ui.label_description.setText("<strong>WELCOME</strong> GTFS TimeTabler")

        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>LOADING</strong> USER INTERFACE."))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>LOADING</strong> USER INTERFACE..."))

        self.show()

    def progress(self):
        self.ui.progressBar.setValue(self.progress_value)
        if self.progress_value > 100:
            self.timer.stop()
            self.main = self.application_window
            self.main.show()
            self.close()
        self.progress_value += 1
