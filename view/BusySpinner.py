import sys
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QPen, QBrush

class BusyIndicator(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('Busy Indicator')

        layout = QVBoxLayout()
        self.indicator = IndicatorWidget()
        layout.addWidget(self.indicator)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def startAnimation(self):
        self.indicator.startAnimation()

    def stopAnimation(self):
        self.indicator.stopAnimation()

class IndicatorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.is_running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePosition)
        self.timer.start(50)  # Update every 50ms

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        pen = QPen(Qt.black, 2)
        brush = QBrush(Qt.NoBrush)
        painter.setPen(pen)
        painter.setBrush(brush)

        radius = min(self.width(), self.height()) // 2 - 5
        x = self.width() // 2
        y = self.height() // 2

        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.drawLine(int(x), int(y), int(x + radius * 0.707), int(y - radius * 0.707))
        painter.drawLine(int(x), int(y), int(x - radius * 0.707), int(y + radius * 0.707))

    def updatePosition(self):
        if self.is_running:
            self.angle = (self.angle + 10) % 360
            self.update()

    def startAnimation(self):
        self.is_running = True
        self.angle = 0
        self.update()

    def stopAnimation(self):
        self.is_running = False
        self.angle = 0
        self.update()