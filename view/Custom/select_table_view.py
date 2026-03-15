
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def getData(self, data):
        return self._data

    def rowCount(self, parent=None):
        if self._data is None:
            return 0
        return self._data.shape[0]

    def columnCount(self, parent=None):
        if self._data is None:
            return 0
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and self._data is not None:
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.TextAlignmentRole:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def wholeData(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._data.iloc[[index.row()]]
        return None

    def headerData(self, section, orientation, role):
        if self._data is None:
            return None
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and 0 <= section < len(self._data.columns):
                return str(self._data.columns[section])
            if orientation == Qt.Vertical and 0 <= section < len(self._data.index):
                return str(section + 1)
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            self._data.columns[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False

