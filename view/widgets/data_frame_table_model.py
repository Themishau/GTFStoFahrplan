from typing import Any

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt


class DataFrameTableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame | None, parent=None) -> None:
        super().__init__(parent)
        self._data_frame: pd.DataFrame | None = data

    @property
    def data_frame(self) -> pd.DataFrame | None:
        return self._data_frame

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if self._data_frame is None:
            return 0
        return self._data_frame.shape[0]

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if self._data_frame is None:
            return 0
        return self._data_frame.shape[1]

    def data(
            self,
            index: QModelIndex | QPersistentModelIndex,
            role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if index.isValid() and self._data_frame is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data_frame.iloc[index.row(), index.column()])
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def row_data(
            self,
            index: QModelIndex | QPersistentModelIndex,
    ) -> pd.DataFrame | None:
        if index.isValid() and self._data_frame is not None:
            return self._data_frame.iloc[[index.row()]]
        return None

    def headerData(
            self,
            section: int,
            orientation: Qt.Orientation,
            role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if self._data_frame is None:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._data_frame.columns):
                return str(self._data_frame.columns[section])
            if orientation == Qt.Orientation.Vertical and 0 <= section < len(self._data_frame.index):
                return str(section + 1)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def setHeaderData(
            self,
            section: int,
            orientation: Qt.Orientation,
            value: Any,
            role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if (
                self._data_frame is not None
                and orientation == Qt.Orientation.Horizontal
                and role == Qt.ItemDataRole.EditRole
        ):
            columns = list(self._data_frame.columns)
            columns[section] = value
            self._data_frame.columns = columns
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False
