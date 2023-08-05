import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        


    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def mimeData(self,indices):
        """
        Move all data, including hidden/disabled columns
        """
        index = indices[0]
        new_data = []

        for col in range(self.columnCount()):
            new_data.append(index.sibling(index.row(),col))

        item = self._data(index.row(),3)
        self.was_enabled = item.isEnabled()
        item.setEnabled(True) # Hack// Fixes copying instead of moving when item is disabled

        return super().mimeData(new_data)

    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        response = super().dropMimeData(data, Qt.CopyAction, row, 0, parent)
        if row == -1:   #Drop after last row
            row = self.rowCount()-1
        item = self._data(row,3)
        item.setEnabled(self.was_enabled) # Hack// Fixes copying instead of moving when style column is disabled
        return response