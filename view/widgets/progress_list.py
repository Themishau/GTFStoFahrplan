import time

from PySide6.QtCore import QAbstractListModel, QModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QListView, QStyledItemDelegate

from model.planning.progress import ProgressUpdate


class ProgressHistoryModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress_items: list[ProgressUpdate] = []

    def rowCount(self, parent=None):
        return len(self._progress_items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item = self._progress_items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item
        if role == Qt.ItemDataRole.UserRole:
            return item
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"{item.process_kind} {item.message}: {item.value}%"

        return None

    def add_progress_item(self, progress: ProgressUpdate):
        if progress.value < 0 or progress.value > 100:
            raise ValueError("Progress value must be between 0 and 100")

        progress_copy = ProgressUpdate(
            value=int(progress.value or 0),
            process_kind=progress.process_kind,
            message=progress.message,
            timestamp=time.time(),
        )

        matching_indices = [
            index
            for index, item in enumerate(self._progress_items)
            if item.process_kind == progress_copy.process_kind
        ]
        if matching_indices:
            last_index = matching_indices[-1]
            last_item = self._progress_items[last_index]
            is_new_run = progress_copy.value < last_item.value
            if not is_new_run:
                self._progress_items[last_index] = progress_copy
                self.dataChanged.emit(
                    self.index(last_index, 0),
                    self.index(last_index, 0),
                    [
                        Qt.ItemDataRole.DisplayRole,
                        Qt.ItemDataRole.UserRole,
                        Qt.ItemDataRole.ToolTipRole,
                    ],
                )
                return

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._progress_items.append(progress_copy)
        self.endInsertRows()


class ProgressHistoryListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ProgressHistoryModel())
        self.setViewMode(QListView.ViewMode.ListMode)
        self.setItemDelegate(ProgressBarDelegate())
        self.setUniformItemSizes(False)
        self.setSpacing(4)
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSelectionMode(QListView.SelectionMode.NoSelection)
        self.setEnabled(True)

    def update_progress(self, progress):
        model = self.model()
        model.add_progress_item(progress)
        self.scrollToBottom()


class ProgressBarDelegate(QStyledItemDelegate):
    BAR_HEIGHT = 22
    ITEM_HEIGHT = 30
    ITEM_PADDING_Y = 4
    ITEM_PADDING_X = 8

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        progress = index.model().data(index, Qt.ItemDataRole.UserRole)
        if progress is None:
            return

        bar_rect = option.rect.adjusted(
            self.ITEM_PADDING_X,
            self.ITEM_PADDING_Y,
            -self.ITEM_PADDING_X,
            -self.ITEM_PADDING_Y,
        )
        bar_rect.setHeight(self.BAR_HEIGHT)
        bar_rect.moveTop(option.rect.top() + ((option.rect.height() - self.BAR_HEIGHT) // 2))

        value = max(0, min(100, int(progress.value or 0)))
        fill_width = int((bar_rect.width() * value) / 100)
        fill_rect = QRect(bar_rect.left(), bar_rect.top(), fill_width, bar_rect.height())
        formatted_time = time.strftime(
            "%H:%M:%S",
            time.localtime(progress.timestamp or time.time()),
        )
        text = f"{formatted_time} | {progress.process_kind} | {progress.message} | {value}%"

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#d7dee7"))
        painter.drawRoundedRect(bar_rect, 6, 6)

        painter.setBrush(QColor("#4f8fba"))
        if fill_rect.width() > 0:
            painter.drawRoundedRect(fill_rect, 6, 6)

        painter.setPen(QPen(QColor("#1f2933")))
        painter.drawText(bar_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), self.ITEM_HEIGHT)
