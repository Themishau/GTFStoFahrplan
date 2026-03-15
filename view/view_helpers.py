from PySide6.QtWidgets import QFileDialog, QHeaderView, QTableView
from PySide6.QtCore import QDate
import os

def get_file_path(parent):
    try:
        input_file_path = QFileDialog.getOpenFileName(parent=parent,
                                                      caption='Select GTFS Zip File',
                                                      dir='C:/Tmp',
                                                      filter='Zip File (*.zip)',
                                                      selectedFilter='Zip File (*.zip)')

    except:
        input_file_path = QFileDialog.getOpenFileName(parent=parent,
                                                      caption='Select GTFS Zip File',
                                                      dir=os.getcwd(),
                                                      filter='Zip File (*.zip)',
                                                      selectedFilter='Zip File (*.zip)')

    return input_file_path if input_file_path[0] else None

def get_output_dir_path(parent):
    output_file_path = QFileDialog.getExistingDirectory(parent,
                                                        caption='Select GTFS Zip File',
                                                        dir='C:/Tmp')
    if len(output_file_path) == 0:
        return None

    return output_file_path if output_file_path[0] else None

def get_pickle_save_path(parent):
    try:
        pickle_file_path = QFileDialog.getSaveFileName(parent=parent,
                                                       caption='Select GTFS Zip File',
                                                       dir='C:/Tmp',
                                                       filter='Zip File (*.zip)',
                                                       selectedFilter='Zip File (*.zip)')

    except:
        pickle_file_path = QFileDialog.getSaveFileName(parent=parent,
                                                       caption='Select GTFS Zip File',
                                                       dir=os.getcwd(),
                                                       filter='Zip File (*.zip)',
                                                       selectedFilter='Zip File (*.zip)')

    return pickle_file_path if pickle_file_path[0] else None

def string_to_qdate(date_string):
    if date_string is None:
        return QDate(2000, 1, 1)
    date_string = date_string.replace('-', '')

    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:])
    return QDate(year, month, day)

def qdate_to_string(qdate):
    format_str = 'yyyyMMdd'
    return qdate.toString(format_str)

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
