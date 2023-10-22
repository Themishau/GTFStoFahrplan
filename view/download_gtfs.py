from PyQt5.QtWidgets import QWidget

from view.pyui.download_gtfs_ui import Ui_Form as Ui_Download

class DownloadGTFS(QWidget):
    def __init__(self):
        super(DownloadGTFS, self).__init__()
        self.ui = Ui_Download()
        self.ui.setupUi(self)
