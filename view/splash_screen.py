from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QMainWindow

from view.pyui.ui_splash_screen import Ui_SplashScreen


class SplashScreen(QMainWindow):
    def __init__(self, application_window):
        super().__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self._application_window = application_window
        self._progress_value = 0

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.advance_progress)
        self._timer.start(35)

        self.ui.label_description.setText("<strong>WELCOME</strong> GTFS TimeTabler")

        QTimer.singleShot(
            1500,
            lambda: self.ui.label_description.setText(
                "<strong>LOADING</strong> USER INTERFACE."
            ),
        )
        QTimer.singleShot(
            3000,
            lambda: self.ui.label_description.setText(
                "<strong>LOADING</strong> USER INTERFACE..."
            ),
        )

        self.show()

    def advance_progress(self) -> None:
        self.ui.progressBar.setValue(self._progress_value)
        if self._progress_value >= 100:
            self._timer.stop()
            self._application_window.show()
            self.close()
        self._progress_value += 1
