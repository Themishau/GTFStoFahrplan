from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import logging

class TableModelSort(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModelSort, self).__init__()
        self._data = data

    def getData(self):
        return self._data

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

    def mimeData(self, indices):
        """
        Move all data, including hidden/disabled columns
        """
        index = indices[0]
        new_data = []

        for col in range(self.columnCount()):
            new_data.append(index.sibling(index.row(), col))

        # item = self.data(index.row(),3)
        item = self.data(index, 3)
        if item is not None:
            self.was_enabled = item.isEnabled()
            item.setEnabled(True)  # Hack// Fixes copying instead of moving when item is disabled

        return super().mimeData(new_data)

    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        print("dropMimeData(data: %r, action: %r, row: %r, col: %r, parent: %r)" % (
            data.formats(), action, row, col, self._index2str(parent)))
        assert action == QtCore.Qt.MoveAction
        return super().dropMimeData(data, action, row, 0, parent)

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        # https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        if index.row() < len(self._data):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def supportedDropActions(self) -> bool:
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    def relocateRow(self, row_source, row_target) -> None:
        row_a, row_b = max(row_source, row_target), min(row_source, row_target)
        sequence_a = self._data.loc[row_source, 'stop_sequence'].copy()
        sequence_b = self._data.loc[row_target, 'stop_sequence'].copy()
        self._data.at[row_source, 'stop_sequence'] = int(sequence_b)
        self._data.at[row_target, 'stop_sequence'] = int(sequence_a)
        self.beginMoveRows(QtCore.QModelIndex(), row_a, row_a, QtCore.QModelIndex(), row_b)
        # also change column stop_sequence
        logging.debug(f'sequence_a: {sequence_a}')
        logging.debug(f'sequence_b: {sequence_b}')
        logging.debug(f"self._data.loc[row_source][stop_sequence]: {self._data.loc[row_source]['stop_sequence']}")
        logging.debug(f"self._data.loc[row_target][stop_sequence]: {self._data.loc[row_target]['stop_sequence']}")

        self._data.loc[row_source], self._data.loc[row_target] = self._data.loc[row_target], self._data.loc[row_source]

        self.endMoveRows()

