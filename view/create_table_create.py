from PySide6.QtWidgets import QWidget

from view.pyui.create_table_create_ui import Ui_Form as Ui_CreateTableCreate


class CreateTableCreate(QWidget):
    def __init__(self):
        super(CreateTableCreate, self).__init__()
        self.ui = Ui_CreateTableCreate()
        self.ui.setupUi(self)


        # # self.tableView_sorting_stops = QtWidgets.QTableView(Form)
        # self.tableView_sorting_stops = customTableView()
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
        #                                    QtWidgets.QSizePolicy.MinimumExpanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)