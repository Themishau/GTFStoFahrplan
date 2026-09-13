from PySide6.QtCore import QObject
from model.planning.strategies.base import TimetableCreationStrategy


class QObjectABCMeta(type(QObject), type(TimetableCreationStrategy)):
    pass
