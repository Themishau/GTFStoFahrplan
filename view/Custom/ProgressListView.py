from PySide6.QtCore import QObject, QThread, Signal, Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QListView, QWidget, QVBoxLayout, QLabel, QStyledItemDelegate, QStyleOptionProgressBar, \
    QApplication, QStyle
from model.Base.Progress import ProgressSignal

class ProgressHistoryItem(QWidget):
    """Widget representing a single progress item"""
    def __init__(self, progress: ProgressSignal):
        super().__init__()
        self.title = progress.message
        self.progress = progress

    def sizeHint(self):
        return QSize(300, 60)

class ProgressHistoryModel(QAbstractTableModel):
    """Model for managing progress items"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []

    def rowCount(self, parent=None):
        return len(self.items)

    def columnCount(self, parent=None):
        return 1  # Assuming there is only one column for the progress items

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            if self.items:
                if role == Qt.DisplayRole:
                    return self.items[-1].title
                elif role == Qt.UserRole:
                    return self.items[-1].progress

        item = self.items[index.row()]
        if role == Qt.DisplayRole:
            return item.title
        elif role == Qt.UserRole:
            return item.progress

    def addItem(self, progress: ProgressSignal):
        """Add a new progress item"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(ProgressHistoryItem(progress))
        self.endInsertRows()

    def updateProgress(self, progress: ProgressSignal):
        """Update progress for an existing item"""
        for index, item in enumerate(self.items):
            if item.title == progress.message:
                self.items[index].progress = progress
                self.dataChanged.emit(self.index(row=index,column=1))
                return
        self.addItem(progress)

class ProgressHistoryListView(QListView):
    """Main view for displaying progress history"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ProgressHistoryModel())
        self.setViewMode(QListView.ListMode)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ProgressBarDelegate())

    def addTask(self, progress: ProgressSignal):
        """Add a new task to the history"""
        model = self.model()
        model.addItem(progress)

    def updateProgress(self, progress):
        """Update progress for a specific task"""
        model = self.model()
        model.updateProgress(progress)

class ProgressBarDelegate(QStyledItemDelegate):
    """Delegate for custom drawing of progress items"""
    def paint(self, painter, option, index):
        progress = index.data(Qt.UserRole)
        if isinstance(progress, ProgressSignal):
            progress_bar_option = QStyleOptionProgressBar()
            progress_bar_option.rect = option.rect
            progress_bar_option.minimum = 0
            progress_bar_option.maximum = 100
            progress_bar_option.progress = progress.value
            progress_bar_option.text = f"{progress.message} {progress.value}%"
            progress_bar_option.textVisible = True
            progress_bar_option.textAlignment = Qt.AlignCenter
            QApplication.style().drawControl(QStyle.CE_ProgressBar, progress_bar_option, painter)