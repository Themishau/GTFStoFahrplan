from PyQt5.QtCore import    (Qt)
from PyQt5.QtGui import     (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QProxyStyle,QStyleOption,
                             QTableView, QHeaderView,
                             QItemDelegate,
                             QApplication)
from SortTableView import TableModelSort
"""
based on
https://mountcreo.com/article/pyqtpyside-drag-and-drop-qtableview-reordering-rows/
"""


class customTableView(QTableView):


    class DropmarkerStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            """Draw a line across the entire row rather than just the column we're hovering over.
            This may not always work depending on global style - for instance I think it won't
            work on OSX."""
            if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
                option_new = QStyleOption(option)
                option_new.rect.setLeft(0)
                if widget:
                    option_new.rect.setRight(widget.width())
                option = option_new
            super().drawPrimitive(element, option, painter, widget)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().hide()
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setStyle(self.DropmarkerStyle())



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