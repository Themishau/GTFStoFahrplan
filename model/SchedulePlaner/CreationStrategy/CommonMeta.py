from PySide6.QtCore import QObject

from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy


class CommonMeta(type(QObject), type(TableCreationStrategy)):
    pass