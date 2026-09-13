import logging

import pandas as pd
from PySide6.QtCore import QModelIndex, Qt

from view.widgets.data_frame_table_model import DataFrameTableModel


class SortableDataFrameTableModel(DataFrameTableModel):

    def mimeData(self, indices):
        if not indices:
            return super().mimeData(indices)
        index = indices[0]
        row_indices = [index.sibling(index.row(), column) for column in range(self.columnCount())]
        return super().mimeData(row_indices)

    def dropMimeData(self, data, action, row, col, parent):
        if action != Qt.DropAction.MoveAction:
            return False
        return super().dropMimeData(data, action, row, 0, parent)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsDragEnabled
        )

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def relocate_row(self, row_source, row_target) -> None:
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
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])
