from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QFileDialog, QHeaderView, QTableView

def get_file_path(parent):
    selected = QFileDialog.getOpenFileName(
        parent=parent,
        caption="Select GTFS ZIP file",
        dir=str(Path.home()),
        filter="ZIP file (*.zip)",
        selectedFilter="ZIP file (*.zip)",
    )
    return selected if selected[0] else None

def get_output_dir_path(parent):
    selected = QFileDialog.getExistingDirectory(
        parent,
        caption="Select timetable output directory",
        dir=str(Path.home()),
    )
    return selected or None

def string_to_qdate(date_string):
    if not date_string:
        return QDate(2000, 1, 1)
    value = QDate.fromString(str(date_string).replace("-", ""), "yyyyMMdd")
    return value if value.isValid() else QDate(2000, 1, 1)

def qdate_to_string(qdate):
    return qdate.toString("yyyyMMdd")

def configure_table_view(table_view: QTableView):
    horizontal_header = table_view.horizontalHeader()
    vertical_header = table_view.verticalHeader()

    horizontal_header.setVisible(True)
    vertical_header.setVisible(False)
    horizontal_header.setStretchLastSection(False)
    horizontal_header.setMinimumSectionSize(24)
    horizontal_header.setSectionResizeMode(QHeaderView.Interactive)

    table_view.setWordWrap(False)
    table_view.setAlternatingRowColors(True)


def update_table_sizes(table_view: QTableView):
    configure_table_view(table_view)

    model = table_view.model()
    if model is None:
        return

    column_count = model.columnCount()
    if column_count <= 0:
        return

    horizontal_header = table_view.horizontalHeader()

    for column in range(column_count):
        resize_mode = QHeaderView.ResizeToContents if column == 0 else QHeaderView.Interactive
        horizontal_header.setSectionResizeMode(column, resize_mode)

    horizontal_header.setStretchLastSection(True)
    table_view.resizeColumnsToContents()
