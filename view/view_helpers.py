from PySide6.QtWidgets import QFileDialog, QHeaderView
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

def update_table_sizes(qViewTable):
    qViewTable.horizontalHeader().setSectionResizeMode(
        qViewTable.horizontalHeader().logicalIndex(0), QHeaderView.Interactive)
    qViewTable.horizontalHeader().setSectionResizeMode(
        qViewTable.horizontalHeader().logicalIndex(1), QHeaderView.Stretch)
