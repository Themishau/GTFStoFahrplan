import math
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

class BusySpinner(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spinner)
        self.timer.start(33)  # Update every ~30ms

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Busy Spinner')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw spinner lines
        for i in range(12):  # 12 lines total
            angle = i * 30  # Each line is 30 degrees apart
            x1 = self.width() // 2 + 50 * math.cos(math.radians(angle))
            y1 = self.height() // 2 + 50 * math.sin(math.radians(angle))
            x2 = self.width() // 2 + 100 * math.cos(math.radians(angle))
            y2 = self.height() // 2 + 100 * math.sin(math.radians(angle))

            pen = QPen(Qt.black, 2)
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)

    def update_spinner(self):
        self.update()

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()


# how to implement

# def show_spinner(parent):
#     spinner = BusySpinner(parent)
#     parent.layout().addWidget(spinner)
#     spinner.start()
