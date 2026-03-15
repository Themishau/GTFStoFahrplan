import logging

import pandas as pd
from PySide6 import QtCore
from PySide6.QtCore import Qt


class TableModelSort(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModelSort, self).__init__()
        self._data = data

    def getData(self):
        return self._data

    def rowCount(self, parent=None):
        if self._data is None:
            return 0
        return self._data.shape[0]

    def columnCount(self, parnet=None):
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

    def headerData(self, col, orientation, role):
        if self._data is None:
            return None
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and 0 <= col < len(self._data.columns):
                return str(self._data.columns[col])
            if orientation == Qt.Vertical and 0 <= col < len(self._data.index):
                return str(col + 1)
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def mimeData(self, indices):
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
        if self._data is None:
            return
        if row_source == row_target:
            return
        if not (0 <= row_source < len(self._data) and 0 <= row_target < len(self._data)):
            return

        logging.debug("Relocating row %s to %s", row_source, row_target)
        self.layoutAboutToBeChanged.emit()

        source_sequence = self._data.iloc[row_source]["stop_sequence"]
        row_data = self._data.iloc[row_source].copy()

        self._data = self._data.drop(self._data.index[row_source]).reset_index(drop=True)
        insert_at = row_target
        if row_target > row_source:
            insert_at -= 1

        self._data = pd.concat(
            [
                self._data.iloc[:insert_at],
                row_data.to_frame().T,
                self._data.iloc[insert_at:],
            ],
            ignore_index=True,
        )

        if "stop_sequence" in self._data.columns:
            self._data["stop_sequence"] = range(1, len(self._data) + 1)

        logging.debug("Moved row with original stop_sequence %s", source_sequence)
        self.layoutChanged.emit()

        top_left = self.index(min(row_source, row_target), 0)
        bottom_right = self.index(max(row_source, row_target), self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])

