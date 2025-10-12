from typing import override

from PySide6.QtCore import QObject, QThread, Signal, Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QListView, QWidget, QVBoxLayout, QLabel, QStyledItemDelegate, QStyleOptionProgressBar, \
    QApplication, QStyle, QStylePainter
from model.Base.Progress import ProgressSignal
import time as Time

class ProgressHistoryItem(QWidget):
    def __init__(self, progress: ProgressSignal):
        super().__init__()
        self.title = progress.message
        self.progress = progress

class ProgressHistoryModel(QAbstractTableModel):
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

        if role == Qt.DisplayRole:
            item = self.progress_items[index.row()]
            return item

        return None

    def add_progress_item(self, progress: ProgressSignal):
        if progress.value < 0 or progress.value > 100:
            raise ValueError("Progress value must be between 0 and 100")

        for index, item in enumerate(self.progress_items):
            if item.process_name == progress.process_name:
                self.progress_items[index].value = progress.value
                self.progress_items[index].message = progress.message
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ProgressHistoryModel())
        self.setViewMode(QListView.ListMode)
        self.setItemDelegate(ProgressBarDelegate())
        self.setUniformItemSizes(True)
        self.setSpacing(10)

    def updateProgress(self, progress):
        model = self.model()
        model.add_progress_item(progress)

class ProgressBarDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        progress = index.model().data(index, Qt.DisplayRole)

        # Ensure proper sizing
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect.adjusted(0, -20, 0, 20)  # Add padding
        # Configure progress bar properties
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress.value
        opt.textVisible = True
        opt.text = f"{progress.process_name} {progress.message}: {progress.value}%"
        opt.textVisible = False

        painter.save()
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
        painter.setPen(QColor(0, 0, 0))
        text = f"{progress.process_name} {progress.message}: {progress.value}%"
        painter.drawText(opt.rect, Qt.AlignCenter, text)
        painter.restore()