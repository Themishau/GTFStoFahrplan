from PySide6.QtCore import QObject, QThread, Signal, Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QListView, QWidget, QVBoxLayout, QLabel, QStyledItemDelegate, QStyleOptionProgressBar, \
    QApplication, QStyle, QStylePainter
from model.Base.Progress import ProgressSignal
import time as Time

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
        self.progress_items = []

    def rowCount(self, parent=None):
        return len(self.progress_items)

    def columnCount(self, parent=None):
        return 1  # Assuming there is only one column for the progress items

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        # DisplayRole handles main visible text
        if role == Qt.DisplayRole:
            item = self.progress_items[index.row()]
            return item

        return None

    def add_progress_item(self, progress: ProgressSignal):
        if progress.value < 0 or progress.value > 100:
            raise ValueError("Progress value must be between 0 and 100")

        for index, item in enumerate(self.progress_items):
            if item.message == progress.message:
                self.progress_items[index].value = progress.value
                self.progress_items[index].timestamp = Time.time()
                self.dataChanged.emit(self.index(index, 0), self.index(index, 0))
                return

        # Create new item
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.progress_items.append(progress)
        self.endInsertRows()
        self.dataChanged.emit(
            self.index(self.rowCount() - 1, 0),
            self.index(self.rowCount() - 1, 0)
        )

class ProgressHistoryListView(QListView):
    """Main view for displaying progress history"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ProgressHistoryModel())
        self.setViewMode(QListView.ListMode)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ProgressBarDelegate())

    def updateProgress(self, progress):
        """Update progress for a specific task"""
        model = self.model()
        model.add_progress_item(progress)

class ProgressBarDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        progress = index.model().data(index, Qt.DisplayRole)

        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress.value
        opt.textVisible = True
        opt.text = f"{progress.message} {progress.value}%"
        opt.textAlignment = Qt.AlignCenter

        painter.save()
        # Pass both the paint device and the parent widget
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
        painter.restore()