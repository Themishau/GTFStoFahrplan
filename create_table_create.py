from PyQt5.QtWidgets import QWidget

from add_files.create_table_create_ui import  Ui_Form as Ui_CreateTableCreate

class CreateTableCreate(QWidget):
    def __init__(self):
        super(CreateTableCreate, self).__init__()
        self.ui = Ui_CreateTableCreate()
        self.ui.setupUi(self)