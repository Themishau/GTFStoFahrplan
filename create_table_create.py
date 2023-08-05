from PyQt5.QtWidgets import QWidget, QAbstractItemView


from add_files.create_table_create_ui import  Ui_Form as Ui_CreateTableCreate


class CreateTableCreate(QWidget):
    def __init__(self):
        super(CreateTableCreate, self).__init__()
        self.ui = Ui_CreateTableCreate()
        self.ui.setupUi(self)
        # self.ui.tableView_sorting_stops.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.ui.tableView_sorting_stops.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableView_sorting_stops.setSelectionBehavior(QAbstractItemView.SelectRows) #Select whole rows
        self.ui.tableView_sorting_stops.setSelectionMode(QAbstractItemView.SingleSelection) # Only select/drag one row each time
        self.ui.tableView_sorting_stops.setDragDropMode(QAbstractItemView.InternalMove) # Objects can only be drag/dropped internally and are moved instead of copied
        self.ui.tableView_sorting_stops.setDragDropOverwriteMode(True) # Removes the original item after moving instead of clearing it
