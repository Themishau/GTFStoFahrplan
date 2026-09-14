import logging
from collections.abc import Sequence

import pandas as pd
from PySide6.QtCore import QMimeData, QModelIndex, QPersistentModelIndex, Qt

from view.widgets.data_frame_table_model import DataFrameTableModel


class SortableDataFrameTableModel(DataFrameTableModel):

    def mimeData(
            self,
            indices: Sequence[QModelIndex],
    ) -> QMimeData:
        if not indices:
            return super().mimeData(indices)
        index = indices[0]
        row_indices = [index.sibling(index.row(), column) for column in range(self.columnCount())]
        return super().mimeData(row_indices)

    def dropMimeData(
            self,
            data: QMimeData,
            action: Qt.DropAction,
            row: int,
            column: int,
            parent: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if action != Qt.DropAction.MoveAction:
            return False
        return super().dropMimeData(data, action, row, 0, parent)

    def flags(
            self,
            index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
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
        data_frame = self._data_frame
        if data_frame is None:
            return
        if row_source == row_target:
            return
        if not (
                0 <= row_source < len(data_frame)
                and 0 <= row_target < len(data_frame)
        ):
            return

        logging.debug("Relocating row %s to %s", row_source, row_target)
        self.layoutAboutToBeChanged.emit()

        source_sequence = data_frame.iloc[row_source]["stop_sequence"]
        row_data = data_frame.iloc[row_source].copy()

        data_frame = data_frame.drop(
            data_frame.index[row_source]
        ).reset_index(drop=True)
        insert_at = row_target
        if row_target > row_source:
            insert_at -= 1

        data_frame = pd.concat(
            [
                data_frame.iloc[:insert_at],
                row_data.to_frame().T,
                data_frame.iloc[insert_at:],
            ],
            ignore_index=True,
        )

        if "stop_sequence" in data_frame.columns:
            data_frame["stop_sequence"] = range(
                1,
                len(data_frame) + 1,
            )
        self._data_frame = data_frame

        logging.debug("Moved row with original stop_sequence %s", source_sequence)
        self.layoutChanged.emit()

        top_left = self.index(min(row_source, row_target), 0)
        bottom_right = self.index(max(row_source, row_target), self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])
