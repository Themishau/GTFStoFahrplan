from PyQt5.QtWidgets import QWidget

from add_files.create_table_import_ui import  Ui_Form as Ui_CreateTableImport

class CreateTableImport(QWidget):
    def __init__(self):
        super(CreateTableImport, self).__init__()
        self.ui = Ui_CreateTableImport()
        self.ui.setupUi(self)