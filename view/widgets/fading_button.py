from PySide6.QtCore import QByteArray, QEasingCurve, QParallelAnimationGroup, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QPushButton


class FadingButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._animation = QPropertyAnimation(
            self._opacity_effect,
            QByteArray(b"opacity"),
            self,
        )
        self._animation.setDuration(1000)
        self._animation.setStartValue(1)
        self._animation.setEasingCurve(QEasingCurve.Type.SineCurve)
        self._animation.setEndValue(0.2)
        self._animation_group = QParallelAnimationGroup(self)
        self._animation_group.addAnimation(self._animation)
        self.clicked.connect(self._start_fade)

    def _start_fade(self) -> None:
        self._animation_group.stop()
        self._animation_group.start()
