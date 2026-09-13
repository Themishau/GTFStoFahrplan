from PySide6.QtCore import QObject
from model.planning.strategies.base import TableCreationStrategy

class QObjectABCMeta(type(QObject), type(TableCreationStrategy)):
    pass