from PyQt5.QtWidgets import QWidget, QAbstractItemView

from add_files.create_table_select_ui import  Ui_Form as Ui_CreateTableSelect


class CreateTableSelect(QWidget):
    def __init__(self):
        super(CreateTableSelect, self).__init__()
        self.ui = Ui_CreateTableSelect()
        self.ui.setupUi(self)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableView.setSelectionMode(QAbstractItemView.SingleSelection)



