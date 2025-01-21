
from PySide6.QtWidgets import QWidget

from view.pyui.general_window_information_ui import Ui_Form as Ui_GeneralInformation


class GeneralInformation(QWidget):
    def __init__(self):
        super(GeneralInformation, self).__init__()
        self.ui = Ui_GeneralInformation()
        self.ui.setupUi(self)