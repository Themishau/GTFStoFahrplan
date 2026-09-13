from PySide6.QtWidgets import QToolBox


class AnimatedToolBox(QToolBox):
    def __init__(self, parent=None):
        super().__init__(parent)
