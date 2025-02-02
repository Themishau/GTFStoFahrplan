from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class AnimatedTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b'opacity')
        self.anim_2 = QPropertyAnimation(self, b"size")
        self.anim_group = QParallelAnimationGroup()
        self.clicked.connect(self.handle_click)

    def handle_click(self):
        self.anim_group.stop()
        self.animation.setDuration(200)
        self.animation.setStartValue(1)
        self.animation.setEasingCurve(QEasingCurve.SineCurve)
        self.animation.setEndValue(0.2)
        #self.anim_2.setStartValue(QSize(100, 50))
        #self.anim_2.setEndValue(QSize(250, 150))
        #self.anim_2.setDuration(2000)
        self.anim_group.addAnimation(self.animation)
        #self.anim_group.addAnimation(self.anim_2)
        self.anim_group.start()