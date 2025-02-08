from PySide6.QtCore import QObject, QThread, Signal, Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QListView, QWidget, QVBoxLayout, QLabel, QStyledItemDelegate

class ProgressHistoryItem(QWidget):
    """Widget representing a single progress item"""
    def __init__(self, title="", progress=0):
        super().__init__()
        self.title = title
        self.progress = progress

    def paintEvent(self, event):
        """Custom painting for progress bar"""
        painter = QPainter(self)
        width = self.width() - 20  # Leave padding
        height = self.height() - 20

        # Draw background
        painter.setBrush(QColor(240, 240, 240))
        painter.drawRect(10, 10, width, height)

        # Draw progress
        progress_width = int(width * (self.progress / 100))
        painter.setBrush(QColor(52, 152, 219))  # Blue color
        painter.drawRect(10, 10, progress_width, height)

        # Draw text
        painter.setPen(QColor(0, 0, 0))
        font_metrics = painter.fontMetrics()
        elided_text = font_metrics.elidedText(
            self.title,
            Qt.ElideRight,
            width
        )
        painter.drawText(10, height + 25, elided_text)

    def sizeHint(self):
        return QSize(300, 60)

class ProgressHistoryModel(QAbstractTableModel):
    """Model for managing progress items"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []

    def rowCount(self, parent=None):
        return len(self.items)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self.items[index.row()]
        if role == Qt.DisplayRole:
            return item.title
        elif role == Qt.UserRole:
            return item.progress

    def addItem(self, title, progress):
        """Add a new progress item"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(ProgressHistoryItem(title, progress))
        self.endInsertRows()

    def updateProgress(self, index, progress):
        """Update progress for an existing item"""
        if 0 <= index < len(self.items):
            self.items[index].progress = progress
            self.dataChanged.emit(index, index)

class ProgressHistoryView(QListView):
    """Main view for displaying progress history"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ProgressHistoryModel())
        self.setViewMode(QListView.ListMode)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ProgressBarDelegate())

    def addTask(self, title, initial_progress=0):
        """Add a new task to the history"""
        model = self.model()
        model.addItem(title, initial_progress)

    def updateProgress(self, index, progress):
        """Update progress for a specific task"""
        model = self.model()
        model.updateProgress(index, progress)

class ProgressBarDelegate(QStyledItemDelegate):
    """Delegate for custom drawing of progress items"""
    def paint(self, painter, option, index):
        item = index.data(Qt.UserRole)
        if isinstance(item, ProgressHistoryItem):
            item.size = option.rect.size()
            item.paint(painter, option.rect, option.palette)