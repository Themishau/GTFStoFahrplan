from PyQt5.QtWidgets import QWidget

from add_files.download_gtfs_ui import Ui_Form as Ui_CreateTable

class DownloadGTFS(QWidget):
    def __init__(self):
        super(DownloadGTFS, self).__init__()
        self.ui = Ui_CreateTable()
        self.ui.setupUi(self)
