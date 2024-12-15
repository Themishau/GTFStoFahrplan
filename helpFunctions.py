from PySide6.QtCore import QDate


def string_to_qdate(date_string):
    """
    Convert a date string in the format 'YYYYMMDD' to a QDate object.

    :param date_string: The date string in 'YYYYMMDD' format.
    :return: A QDate object representing the given date.
    """
    if date_string is None:
       return QDate(2000, 1, 1)

    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:])
    return QDate(year, month, day)

def qdate_to_string(qdate):
    """
    Convert a QDate object to a string in the format 'YYYYMMDD'.

    :param qdate: The QDate object to convert.
    :return: A string representation of the date in 'YYYYMMDD' format.
    """
    # Construct the format string for 'YYYYMMDD'
    format_str = 'yyyyMMdd'
    return qdate.toString(format_str)