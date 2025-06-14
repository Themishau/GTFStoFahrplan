from PySide6.QtCore import Qt
from PySide6.QtWidgets import QProxyStyle, QStyleOption, QTableView, QHeaderView, QAbstractItemView, QStyle

"""
based on
https://mountcreo.com/article/pyqtpyside-drag-and-drop-qtableview-reordering-rows/
"""


class Customtableview(QTableView):
    class DropmarkerStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            if element == QStyle.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
                option_new = QStyleOption(option)
                option_new.rect.setLeft(0)
                if widget:
                    option_new.rect.setRight(widget.width())
                option = option_new
            super().drawPrimitive(element, option, painter, widget)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().hide()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # Fixed line
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setStyle(self.DropmarkerStyle())
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def dropEvent(self, event):
        if (event.source() is not self or
                (event.dropAction() != Qt.MoveAction and
                 self.dragDropMode() != self.InternalMove)):
            super().dropEvent(event)

        selection = self.selectedIndexes()
        from_index = selection[0].row() if selection else -1
        to_index = self.indexAt(event.pos()).row()
        if (0 <= from_index < self.model().rowCount() and
                0 <= to_index < self.model().rowCount() and
                from_index != to_index):
            self.model().relocateRow(from_index, to_index)
            event.accept()
        super().dropEvent(event)
