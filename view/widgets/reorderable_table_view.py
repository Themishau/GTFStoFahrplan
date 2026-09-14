from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QProxyStyle,
    QStyle,
    QStyleOption,
    QTableView,
)

from view.widgets.sortable_data_frame_table_model import SortableDataFrameTableModel

"""
based on
https://mountcreo.com/article/pyqtpyside-drag-and-drop-qtableview-reordering-rows/
"""


class ReorderableTableView(QTableView):
    class DropMarkerStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            if (
                    element == QStyle.PrimitiveElement.PE_IndicatorItemViewItemDrop
                    and not option.rect.isNull()
            ):
                option_new = QStyleOption(option)
                option_new.rect.setLeft(0)
                if widget:
                    option_new.rect.setRight(widget.width())
                option = option_new
            super().drawPrimitive(element, option, painter, widget)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setStyle(self.DropMarkerStyle())
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    def dropEvent(self, event):
        if (
                event.source() is not self
                or event.dropAction() != Qt.DropAction.MoveAction
                or self.dragDropMode() != QAbstractItemView.DragDropMode.InternalMove
        ):
            super().dropEvent(event)
            return

        selection = self.selectedIndexes()
        from_index = selection[0].row() if selection else -1
        to_index = self.indexAt(event.position().toPoint()).row()
        model = self.model()
        if (
                isinstance(model, SortableDataFrameTableModel)
                and 0 <= from_index < model.rowCount()
                and 0 <= to_index < model.rowCount()
                and from_index != to_index
        ):
            model.relocate_row(from_index, to_index)
            event.accept()
            return

        super().dropEvent(event)
