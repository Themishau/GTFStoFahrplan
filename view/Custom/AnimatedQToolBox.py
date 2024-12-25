from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve
from PySide6.QtWidgets import QToolBox, QWidget, QGraphicsOpacityEffect

class AnimatedQToolBox(QToolBox):
    def __init__(self, parent=None):
        super().__init__(parent)