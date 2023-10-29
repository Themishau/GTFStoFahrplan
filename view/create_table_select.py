from PyQt5.QtWidgets import QWidget, QAbstractItemView,QHeaderView
from view.pyui.create_table_select_ui import  Ui_Form as Ui_CreateTableSelect


class CreateTableSelect(QWidget):
    def __init__(self):
        super(CreateTableSelect, self).__init__()
        self.ui = Ui_CreateTableSelect()
        self.ui.setupUi(self)
        self.ui.AgenciesTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.AgenciesTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.AgenciesTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.TripsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.TripsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.TripsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


