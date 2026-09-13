from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHeaderView, QTableView

class AnimatedTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b'opacity')
        self.anim_group = QParallelAnimationGroup()
        self.clicked.connect(self.handle_click)

    def handle_click(self):
        self.anim_group.stop()
        self.animation.setDuration(200)
        self.animation.setStartValue(1)
        self.animation.setEasingCurve(QEasingCurve.SineCurve)
        self.animation.setEndValue(0.2)
        self.anim_group.addAnimation(self.animation)
        self.anim_group.start()
