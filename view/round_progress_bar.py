from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import math

"""
https://www.youtube.com/watch?v=E7lhFwcDpMI
"""
class RoundProgress(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.value = 0
        self.current_value = 0
        self.target_value = 0 # Initialize current_valu
        self.width = 120
        self.height = 120
        self.progress_width = 10
        self.progress_round_cap = True
        self.progress_color = 0x498BD1
        self.max_value = 100
        self.font_family = "Segoe UI"
        self.font_size = 12
        self.suffix = "%"
        self.text_color = 0x498BD1
        self.enable_shadow = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_value)
        self.timer.start(100) # Update every 100 ms
        self.start_time = QTime.currentTime() # Initialize start_time

        # Set the timer interval to make the update slower
        fps = 20 # Desired frames per second
        self.timer.setInterval(round(1000 / fps)) # Calculate interval in milliseconds
        self.timer.start(500) # Update every 100 ms


        self.resize(self.width, self.height)

    def set_value(self, value):
        self.target_value = value
        self.current_value = self.value # Update current_value to the current value
        self.start_time = QTime.currentTime() # Reset start_time for each new value
        self.timer.start(100) # Start the timer to smoothly update the value

    def update_value(self):
        elapsed = QTime.currentTime().msecsSinceStartOfDay() - self.start_time.msecsSinceStartOfDay()
        progress = elapsed / 1000.0 # Convert to seconds
        if progress >= 1.0:
            self.timer.stop()
            self.value = self.target_value
        else:
            # Use a sine function to smoothly interpolate the value
            self.value = round(self.current_value + (self.target_value - self.current_value) * (math.sin(progress * math.pi) / 2 + 0.5))
            if self.value == self.target_value:
                self.timer.stop()
        self.repaint()
        self.valueChanged.emit(self.value)

    def paintEvent(self, event):
        width = self.width - self.progress_width
        height = self.height - self.progress_width
        margin = self.progress_width / 2
        value = self.value * 360 / self.max_value

        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)

        rect = QRect(0,0, self.width, self.height)
        paint.setPen(Qt.NoPen)
        paint.drawRect(rect)

        pen = QPen()
        pen.setColor(QColor(self.progress_color))
        pen.setWidth(self.progress_width)
        if self.progress_round_cap:
            pen.setCapStyle(Qt.RoundCap)

        paint.setPen(pen)
        paint.drawArc(int(margin), int(margin), width, height, -90 * 16, int(-value * 16))

        pen.setColor(QColor(self.text_color))
        paint.setPen(pen)
        paint.drawText(rect, Qt.AlignCenter, f"{self.value}{self.suffix}")

        paint.end()



