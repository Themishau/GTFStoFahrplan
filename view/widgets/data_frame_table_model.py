import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class DataFrameTableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame | None, parent=None):
        super().__init__(parent)
        self._data = data

    @property
    def data_frame(self):
        return self._data

    def rowCount(self, parent=QModelIndex()) -> int:
        if self._data is None:
            return 0
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()) -> int:
        if self._data is None:
            return 0
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and self._data is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def row_data(self, index):
        if index.isValid() and self._data is not None:
            return self._data.iloc[[index.row()]]
        return None

    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        if self._data is None:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._data.columns):
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical and 0 <= section < len(self._data.index):
                return str(section + 1)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def setHeaderData(
        self,
        section,
        orientation,
        value,
        role=Qt.ItemDataRole.EditRole,
    ):
        if (
            self._data is not None
            and orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.EditRole
        ):
            self._data.columns[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False
