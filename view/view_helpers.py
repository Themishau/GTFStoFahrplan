from pathlib import Path
from typing import cast

from PySide6.QtCore import QAbstractItemModel, QDate
from PySide6.QtWidgets import QFileDialog, QHeaderView, QTableView


def select_gtfs_zip(parent) -> Path | None:
    selected_path, _ = QFileDialog.getOpenFileName(
        parent=parent,
        caption="Select GTFS ZIP file",
        dir=str(Path.home()),
        filter="ZIP file (*.zip)",
        selectedFilter="ZIP file (*.zip)",
    )
    return Path(selected_path) if selected_path else None


def select_output_directory(parent) -> Path | None:
    selected_path = QFileDialog.getExistingDirectory(
        parent,
        caption="Select timetable output directory",
        dir=str(Path.home()),
    )
    return Path(selected_path) if selected_path else None


def string_to_qdate(date_string: str | None) -> QDate:
    if not date_string:
        return QDate(2000, 1, 1)
    value = QDate.fromString(str(date_string).replace("-", ""), "yyyyMMdd")
    return value if value.isValid() else QDate(2000, 1, 1)


def qdate_to_string(qdate: QDate) -> str:
    return qdate.toString("yyyyMMdd")


def configure_table_view(table_view: QTableView) -> None:
    horizontal_header = table_view.horizontalHeader()
    vertical_header = table_view.verticalHeader()

    horizontal_header.setVisible(True)
    vertical_header.setVisible(False)
    horizontal_header.setStretchLastSection(False)
    horizontal_header.setMinimumSectionSize(24)
    horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    table_view.setWordWrap(False)
    table_view.setAlternatingRowColors(True)


def update_table_sizes(table_view: QTableView) -> None:
    configure_table_view(table_view)

    model = cast(QAbstractItemModel | None, table_view.model())
    if model is None:
        return

    column_count = model.columnCount()
    if column_count <= 0:
        return

    horizontal_header = table_view.horizontalHeader()

    for column in range(column_count):
        resize_mode = (
            QHeaderView.ResizeMode.ResizeToContents
            if column == 0
            else QHeaderView.ResizeMode.Interactive
        )
        horizontal_header.setSectionResizeMode(column, resize_mode)

    horizontal_header.setStretchLastSection(True)
    table_view.resizeColumnsToContents()
