# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDateEdit, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLayout, QLineEdit,
    QMainWindow, QPlainTextEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSplitter, QStackedWidget, QTabWidget,
    QTableView, QVBoxLayout, QWidget)

from view.Custom.AnimatedQToolBox import AnimatedQToolBox
from view.Custom.AnimatedTableView import AnimatedTableView
from view.Custom.FadingButton import FadingButton
from view.Custom.ProgressListView import ProgressHistoryListView
from view.Custom.custom_table_view import Customtableview
from view.Custom.round_progress_bar import RoundProgress
from view.ui.res import resource_boot
from view.ui.res import resource_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1600, 800)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QSize(1600, 800))
        font = QFont()
        font.setPointSize(12)
        font.setStyleStrategy(QFont.PreferAntialias)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(u"QPushButton {\n"
"    background-color: #ae636f;\n"
"    border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#f2b198;\n"
"}\n"
"\n"
"QLineEdit {\n"
"	background-color: #F0FCF7;\n"
"    border-radius: 1px;\n"
"	padding: 1px 1px 1px 1px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QLabel {\n"
"   border-radius: 1px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QComboBox {\n"
"    background-color: #ae636f;\n"
"    border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#f2b198;\n"
"    \n"
"}\n"
"\n"
"QPushButton:hover {\n"
"   background-color: #408d49;\n"
"   border-radius: 10px;\n"
"   color:#fde1d6;\n"
"}\n"
"\n"
"QTableView {\n"
"	background-color: #F0FCF7;\n"
"    border-radius: 1px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QLabel {\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;"
                        "\n"
"    font-weight: bold;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QComboBox {\n"
"	background-color: #587b6d;\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 100px;\n"
"	text-align: left;\n"
"    color:#41312b;\n"
"    border: 1px solid #ccc;\n"
"    appearance: none;\n"
"    -webkit-appearance: none;\n"
"    -moz-appearance: none;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: right bottom;\n"
"    width: 40px;\n"
"    border-left: 1px solid #ccc;\n"
"}\n"
"ProgressHistoryListView {\n"
"   color:#fde1d6;\n"
"}\n"
"")
        MainWindow.setTabShape(QTabWidget.TabShape.Triangular)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QSize(1600, 800))
        self.centralwidget.setStyleSheet(u"* {\n"
"background-color: #f4d6b7;\n"
"color: #1e1e1e;\n"
"font: bold;\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setMinimumSize(QSize(0, 0))
        self.splitter.setMaximumSize(QSize(1608, 800))
        self.splitter.setFrameShape(QFrame.Shape.Box)
        self.splitter.setFrameShadow(QFrame.Shadow.Raised)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setOpaqueResize(False)
        self.splitter.setChildrenCollapsible(False)
        self.menu_widget = QWidget(self.splitter)
        self.menu_widget.setObjectName(u"menu_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.menu_widget.sizePolicy().hasHeightForWidth())
        self.menu_widget.setSizePolicy(sizePolicy1)
        self.menu_widget.setMinimumSize(QSize(200, 800))
        self.menu_widget.setMaximumSize(QSize(200, 800))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        font1.setBold(True)
        font1.setItalic(False)
        font1.setStyleStrategy(QFont.NoAntialias)
        self.menu_widget.setFont(font1)
        self.menu_widget.setStyleSheet(u"* {\n"
"\n"
"color: #1e1e1e;\n"
"font: bold;\n"
"}\n"
"\n"
"#frame  {\n"
"\n"
"    border-style: solid;\n"
"}\n"
"\n"
"#textBrowser {\n"
"	text-align: center;\n"
"}\n"
"\n"
"\n"
"#toolBox::tab {\n"
"	padding-left: 5px;\n"
"	text-align: left;\n"
"    border-style: solid;\n"
"}\n"
"\n"
"#toolBox::tab:selected {\n"
"	background-color: #ae636f;\n"
"	font-weight: bold;\n"
"}\n"
"\n"
"#toolBox QPushButton {\n"
"	padding: 5px 0px 5px 20px;\n"
"	text-align: left;\n"
"	border-radius: 3px;\n"
"}\n"
"\n"
"#toolBox QPushButton:hover {\n"
"	background-color: #f8a196;\n"
"   border-radius: 3px;\n"
"}\n"
"\n"
"#toolBox QPushButton:checked {\n"
"	background-color: #ae636f;\n"
"	font-weight: bold;\n"
"}\n"
"\n"
"#toolBox label {\n"
"text-align: center;\n"
"}\n"
"\n"
"#btnExit {\n"
"background-color: #ae636f;\n"
"}")
        self.gridLayout = QGridLayout(self.menu_widget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.menu_widget)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(200, 800))
        self.frame.setMaximumSize(QSize(200, 800))
        self.frame.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.frame.setStyleSheet(u"")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self._2 = QVBoxLayout(self.frame)
        self._2.setObjectName(u"_2")
        self._2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.toolBox = AnimatedQToolBox(self.frame)
        self.toolBox.setObjectName(u"toolBox")
        sizePolicy1.setHeightForWidth(self.toolBox.sizePolicy().hasHeightForWidth())
        self.toolBox.setSizePolicy(sizePolicy1)
        self.toolBox.setMinimumSize(QSize(0, 0))
        self.toolBox.setMaximumSize(QSize(16777215, 300))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setItalic(False)
        self.toolBox.setFont(font2)
        self.toolBox.setMouseTracking(True)
        self.toolBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.toolBox.setStyleSheet(u"")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 182, 130))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.page.sizePolicy().hasHeightForWidth())
        self.page.setSizePolicy(sizePolicy2)
        self.gridLayout_6 = QGridLayout(self.page)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.pushButton_5 = FadingButton(self.page)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setCheckable(True)

        self.gridLayout_6.addWidget(self.pushButton_5, 0, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.verticalSpacer, 1, 0, 1, 1)

        icon = QIcon()
        icon.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/house-door.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolBox.addItem(self.page, icon, u"General")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 182, 134))
        sizePolicy2.setHeightForWidth(self.page_2.sizePolicy().hasHeightForWidth())
        self.page_2.setSizePolicy(sizePolicy2)
        self.page_2.setStyleSheet(u"")
        self.gridLayout_5 = QGridLayout(self.page_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.pushButton_3 = FadingButton(self.page_2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/layout-text-window-reverse.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_3.setCheckable(True)

        self.gridLayout_5.addWidget(self.pushButton_3, 1, 0, 1, 2)

        self.pushButton_2 = FadingButton(self.page_2)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/file-earmark-arrow-up.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_2.setIcon(icon2)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setChecked(False)
        self.pushButton_2.setFlat(False)

        self.gridLayout_5.addWidget(self.pushButton_2, 0, 0, 1, 2)

        self.pushButton_4 = FadingButton(self.page_2)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/arrow-repeat.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_4.setIcon(icon3)
        self.pushButton_4.setCheckable(True)

        self.gridLayout_5.addWidget(self.pushButton_4, 2, 0, 1, 2)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.verticalSpacer_2, 3, 0, 1, 1)

        icon4 = QIcon()
        icon4.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/table.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolBox.addItem(self.page_2, icon4, u"Create Table")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setGeometry(QRect(0, 0, 182, 90))
        sizePolicy2.setHeightForWidth(self.page_3.sizePolicy().hasHeightForWidth())
        self.page_3.setSizePolicy(sizePolicy2)
        self.gridLayout_2 = QGridLayout(self.page_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.pushButton_6 = FadingButton(self.page_3)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setCheckable(True)

        self.gridLayout_2.addWidget(self.pushButton_6, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 1, 0, 1, 1)

        icon5 = QIcon()
        icon5.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/download.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolBox.addItem(self.page_3, icon5, u"Download GTFS")

        self._2.addWidget(self.toolBox, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self._2.addItem(self.verticalSpacer_4)

        self.btnExit = FadingButton(self.frame)
        self.btnExit.setObjectName(u"btnExit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btnExit.sizePolicy().hasHeightForWidth())
        self.btnExit.setSizePolicy(sizePolicy3)
        self.btnExit.setMinimumSize(QSize(100, 40))
        self.btnExit.setMaximumSize(QSize(200, 100))
        font3 = QFont()
        font3.setPointSize(12)
        font3.setBold(True)
        font3.setItalic(False)
        self.btnExit.setFont(font3)
        self.btnExit.setStyleSheet(u"")

        self._2.addWidget(self.btnExit, 0, Qt.AlignmentFlag.AlignBottom)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop)

        self.splitter.addWidget(self.menu_widget)
        self.main_widget = QWidget(self.splitter)
        self.main_widget.setObjectName(u"main_widget")
        sizePolicy.setHeightForWidth(self.main_widget.sizePolicy().hasHeightForWidth())
        self.main_widget.setSizePolicy(sizePolicy)
        self.main_widget.setMinimumSize(QSize(0, 0))
        self.main_widget.setMaximumSize(QSize(1400, 800))
        self.main_widget.setStyleSheet(u"\n"
"* {\n"
"  background-color: #f4d6b7;\n"
"}\n"
"\n"
"#bottom_info_widget {\n"
"  border-top: 1px solid #1e1e1e;\n"
"  border-left: 1px solid #1e1e1e;\n"
"}\n"
"#ProgressHistoryListView{\n"
"  border-top: 1px solid #1e1e1e;\n"
"  border-left: 1px solid #1e1e1e;\n"
"}\n"
"")
        self.gridLayout_4 = QGridLayout(self.main_widget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.bottom_info_widget = QWidget(self.main_widget)
        self.bottom_info_widget.setObjectName(u"bottom_info_widget")
        sizePolicy3.setHeightForWidth(self.bottom_info_widget.sizePolicy().hasHeightForWidth())
        self.bottom_info_widget.setSizePolicy(sizePolicy3)
        self.bottom_info_widget.setMaximumSize(QSize(1400, 175))
        self.bottom_info_widget.setStyleSheet(u"")
        self.info_widget = QGridLayout(self.bottom_info_widget)
        self.info_widget.setObjectName(u"info_widget")
        self.info_widget.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.progess_log = QGridLayout()
        self.progess_log.setObjectName(u"progess_log")
        self.progress_history_list_view = ProgressHistoryListView(self.bottom_info_widget)
        self.progress_history_list_view.setObjectName(u"progress_history_list_view")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.progress_history_list_view.sizePolicy().hasHeightForWidth())
        self.progress_history_list_view.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.progess_log.addWidget(self.progress_history_list_view, 0, 0, 1, 1)


        self.info_widget.addLayout(self.progess_log, 2, 0, 1, 1)

        self.selection_box = QWidget(self.bottom_info_widget)
        self.selection_box.setObjectName(u"selection_box")
        self.selection_box.setMaximumSize(QSize(16777215, 125))
        self.selection_box.setStyleSheet(u"border-style: solid;\n"
"border-width: 1px;\n"
"border-radius: 1px;")
        self.selection_grid = QGridLayout(self.selection_box)
        self.selection_grid.setObjectName(u"selection_grid")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.line_Selection_format = QLineEdit(self.selection_box)
        self.line_Selection_format.setObjectName(u"line_Selection_format")
        self.line_Selection_format.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.line_Selection_format.sizePolicy().hasHeightForWidth())
        self.line_Selection_format.setSizePolicy(sizePolicy3)
        self.line_Selection_format.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.line_Selection_format)

        self.line_Selection_agency = QLineEdit(self.selection_box)
        self.line_Selection_agency.setObjectName(u"line_Selection_agency")
        self.line_Selection_agency.setEnabled(False)
        self.line_Selection_agency.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.line_Selection_agency)

        self.line_Selection_trips = QLineEdit(self.selection_box)
        self.line_Selection_trips.setObjectName(u"line_Selection_trips")
        self.line_Selection_trips.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.line_Selection_trips.sizePolicy().hasHeightForWidth())
        self.line_Selection_trips.setSizePolicy(sizePolicy3)
        self.line_Selection_trips.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.line_Selection_trips)


        self.selection_grid.addLayout(self.verticalLayout_2, 1, 0, 1, 1)

        self.label_16 = QLabel(self.selection_box)
        self.label_16.setObjectName(u"label_16")
        sizePolicy3.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy3)
        font4 = QFont()
        font4.setFamilies([u"72"])
        font4.setPointSize(8)
        font4.setBold(True)
        font4.setItalic(False)
        self.label_16.setFont(font4)
        self.label_16.setStyleSheet(u"")

        self.selection_grid.addWidget(self.label_16, 0, 0, 1, 1)


        self.info_widget.addWidget(self.selection_box, 2, 2, 1, 1)


        self.gridLayout_4.addWidget(self.bottom_info_widget, 3, 0, 1, 1)

        self.top_widget = QWidget(self.main_widget)
        self.top_widget.setObjectName(u"top_widget")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.top_widget.sizePolicy().hasHeightForWidth())
        self.top_widget.setSizePolicy(sizePolicy5)
        self.top_widget.setMaximumSize(QSize(1400, 75))
        self.top_widget.setStyleSheet(u"#pushButton  {\n"
"    border: 1px solid #1e1e1e;\n"
"    border-style: solid;\n"
"}")
        self.horizontalLayout = QHBoxLayout(self.top_widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.pushButton = QPushButton(self.top_widget)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy3.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy3)
        self.pushButton.setSizeIncrement(QSize(30, 30))
        self.pushButton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.pushButton.setStyleSheet(u"")
        icon6 = QIcon()
        icon6.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/arrow-left-square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon6.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/arrow-right-square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.pushButton.setIcon(icon6)
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(False)

        self.horizontalLayout.addWidget(self.pushButton)

        self.horizontalSpacer = QSpacerItem(40, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout_4.addWidget(self.top_widget, 0, 0, 1, 1)

        self.main_view_stacked_widget = QStackedWidget(self.main_widget)
        self.main_view_stacked_widget.setObjectName(u"main_view_stacked_widget")
        self.main_view_stacked_widget.setEnabled(True)
        sizePolicy4.setHeightForWidth(self.main_view_stacked_widget.sizePolicy().hasHeightForWidth())
        self.main_view_stacked_widget.setSizePolicy(sizePolicy4)
        self.main_view_stacked_widget.setMinimumSize(QSize(1400, 600))
        self.main_view_stacked_widget.setMaximumSize(QSize(1400, 600))
        self.main_view_stacked_widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.main_view_stacked_widget.setAutoFillBackground(False)
        self.main_view_stacked_widget.setStyleSheet(u"* {\n"
"background-color:#f2ccae;\n"
"  color:  #1e1e1e;\n"
"   font: bold;\n"
"}\n"
"\n"
"#create_import_page {\n"
"border-style: solid;\n"
"background-color:#f2ccae;\n"
"\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #ae636f;\n"
"    border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#f2b198;\n"
"}\n"
"\n"
"QLineEdit {\n"
"	background-color: #F0FCF7;\n"
"    border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QLabel {\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"\n"
"QPushButton:hover {\n"
"   background-color: #408d49;\n"
"   border-radius: 10px;\n"
"   color:#fde1d6;\n"
"}\n"
"\n"
"QTableView {\n"
"	background-color: #F0FCF7;\n"
"    border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QLabel {\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	te"
                        "xt-align: center;\n"
"    font-weight: bold;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"QComboBox {\n"
"    background-color: #ae636f;\n"
"    color:#f2b198;\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 40px;\n"
"	text-align: left;\n"
"    border: 1px solid #ccc;\n"
"    appearance: none;\n"
"    -webkit-appearance: none;\n"
"    -moz-appearance: none;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: right bottom;\n"
"    width: 40px;\n"
"    border-left: 1px solid #ccc;\n"
"}\n"
"QTableView::item:selected {\n"
"     background-color: #0078d4;\n"
"     color: white;\n"
"}\n"
"")
        self.main_view_stacked_widget.setFrameShape(QFrame.Shape.Box)
        self.main_view_stacked_widget.setFrameShadow(QFrame.Shadow.Plain)
        self.general_information_page = QWidget()
        self.general_information_page.setObjectName(u"general_information_page")
        sizePolicy4.setHeightForWidth(self.general_information_page.sizePolicy().hasHeightForWidth())
        self.general_information_page.setSizePolicy(sizePolicy4)
        self.general_information_page.setMinimumSize(QSize(0, 0))
        self.general_information_page.setMaximumSize(QSize(1400, 600))
        self.gridLayoutWidget = QWidget(self.general_information_page)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(9, 19, 1402, 434))
        self.verticalLayout_3 = QVBoxLayout(self.gridLayoutWidget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit = QPlainTextEdit(self.gridLayoutWidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setMinimumSize(QSize(1000, 400))
        font5 = QFont()
        font5.setFamilies([u"MS Reference Sans Serif"])
        font5.setBold(True)
        font5.setItalic(False)
        self.plainTextEdit.setFont(font5)

        self.verticalLayout_3.addWidget(self.plainTextEdit, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalSpacer_2 = QSpacerItem(1000, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.verticalLayout_3.addItem(self.horizontalSpacer_2)

        self.main_view_stacked_widget.addWidget(self.general_information_page)
        self.create_import_page = QWidget()
        self.create_import_page.setObjectName(u"create_import_page")
        sizePolicy4.setHeightForWidth(self.create_import_page.sizePolicy().hasHeightForWidth())
        self.create_import_page.setSizePolicy(sizePolicy4)
        self.create_import_page.setMaximumSize(QSize(1400, 600))
        self.create_import_page.setStyleSheet(u"")
        self.gridLayoutWidget_3 = QWidget(self.create_import_page)
        self.gridLayoutWidget_3.setObjectName(u"gridLayoutWidget_3")
        self.gridLayoutWidget_3.setGeometry(QRect(0, 0, 1391, 591))
        self.horizontalLayout_3 = QHBoxLayout(self.gridLayoutWidget_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout_11.setContentsMargins(-1, 0, -1, -1)
        self.lineInputPath = QLineEdit(self.gridLayoutWidget_3)
        self.lineInputPath.setObjectName(u"lineInputPath")
        self.lineInputPath.setFont(font3)
        self.lineInputPath.setStyleSheet(u"")
        self.lineInputPath.setReadOnly(True)

        self.gridLayout_11.addWidget(self.lineInputPath, 0, 1, 1, 1)

        self.btnGetPickleFile = FadingButton(self.gridLayoutWidget_3)
        self.btnGetPickleFile.setObjectName(u"btnGetPickleFile")
        self.btnGetPickleFile.setEnabled(True)
        self.btnGetPickleFile.setFont(font3)
        self.btnGetPickleFile.setStyleSheet(u"")
        self.btnGetPickleFile.setIcon(icon2)

        self.gridLayout_11.addWidget(self.btnGetPickleFile, 2, 2, 1, 1)

        self.label_11 = QLabel(self.gridLayoutWidget_3)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font5)
        self.label_11.setStyleSheet(u"")

        self.gridLayout_11.addWidget(self.label_11, 0, 0, 1, 1)

        self.btnGetOutputDir = FadingButton(self.gridLayoutWidget_3)
        self.btnGetOutputDir.setObjectName(u"btnGetOutputDir")
        self.btnGetOutputDir.setEnabled(True)
        self.btnGetOutputDir.setFont(font3)
        self.btnGetOutputDir.setStyleSheet(u"")
        self.btnGetOutputDir.setIcon(icon2)

        self.gridLayout_11.addWidget(self.btnGetOutputDir, 1, 2, 1, 1)

        self.lineOutputPath = QLineEdit(self.gridLayoutWidget_3)
        self.lineOutputPath.setObjectName(u"lineOutputPath")
        self.lineOutputPath.setFont(font3)
        self.lineOutputPath.setStyleSheet(u"")
        self.lineOutputPath.setReadOnly(True)

        self.gridLayout_11.addWidget(self.lineOutputPath, 1, 1, 1, 1)

        self.btnGetFile = FadingButton(self.gridLayoutWidget_3)
        self.btnGetFile.setObjectName(u"btnGetFile")
        self.btnGetFile.setEnabled(True)
        self.btnGetFile.setFont(font3)
        self.btnGetFile.setStyleSheet(u"")
        self.btnGetFile.setIcon(icon2)

        self.gridLayout_11.addWidget(self.btnGetFile, 0, 2, 1, 1)

        self.btnImport = FadingButton(self.gridLayoutWidget_3)
        self.btnImport.setObjectName(u"btnImport")
        self.btnImport.setEnabled(True)
        self.btnImport.setFont(font3)
        self.btnImport.setStyleSheet(u"")

        self.gridLayout_11.addWidget(self.btnImport, 3, 0, 1, 1)

        self.picklesavename = QLineEdit(self.gridLayoutWidget_3)
        self.picklesavename.setObjectName(u"picklesavename")
        self.picklesavename.setFont(font3)
        self.picklesavename.setStyleSheet(u"")
        self.picklesavename.setReadOnly(True)

        self.gridLayout_11.addWidget(self.picklesavename, 2, 1, 1, 1)

        self.label_10 = QLabel(self.gridLayoutWidget_3)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font5)
        self.label_10.setStyleSheet(u"")

        self.gridLayout_11.addWidget(self.label_10, 1, 0, 1, 1)

        self.checkBox_savepickle = QCheckBox(self.gridLayoutWidget_3)
        self.checkBox_savepickle.setObjectName(u"checkBox_savepickle")
        sizePolicy4.setHeightForWidth(self.checkBox_savepickle.sizePolicy().hasHeightForWidth())
        self.checkBox_savepickle.setSizePolicy(sizePolicy4)

        self.gridLayout_11.addWidget(self.checkBox_savepickle, 2, 0, 1, 1)

        self.btnRestart = FadingButton(self.gridLayoutWidget_3)
        self.btnRestart.setObjectName(u"btnRestart")
        self.btnRestart.setEnabled(False)
        self.btnRestart.setFont(font3)
        self.btnRestart.setStyleSheet(u"")

        self.gridLayout_11.addWidget(self.btnRestart, 4, 0, 1, 1)


        self.horizontalLayout_3.addLayout(self.gridLayout_11)

        self.gridLayout_14 = QGridLayout()
        self.gridLayout_14.setSpacing(0)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_14.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.gridLayout_14.setContentsMargins(0, -1, -1, -1)
        self.label_2 = QLabel(self.gridLayoutWidget_3)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMaximumSize(QSize(300, 100))
        self.label_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_2.setWordWrap(False)

        self.gridLayout_14.addWidget(self.label_2, 0, 0, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_14.addItem(self.verticalSpacer_8, 4, 0, 1, 1)

        self.tableView = Customtableview(self.gridLayoutWidget_3)
        self.tableView.setObjectName(u"tableView")
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMaximumSize(QSize(500, 200))

        self.gridLayout_14.addWidget(self.tableView, 3, 0, 1, 1)


        self.horizontalLayout_3.addLayout(self.gridLayout_14)

        self.main_view_stacked_widget.addWidget(self.create_import_page)
        self.create_select_page = QWidget()
        self.create_select_page.setObjectName(u"create_select_page")
        sizePolicy4.setHeightForWidth(self.create_select_page.sizePolicy().hasHeightForWidth())
        self.create_select_page.setSizePolicy(sizePolicy4)
        self.create_select_page.setMaximumSize(QSize(1400, 600))
        self.create_select_page.setStyleSheet(u"")
        self.gridLayoutWidget_4 = QWidget(self.create_select_page)
        self.gridLayoutWidget_4.setObjectName(u"gridLayoutWidget_4")
        self.gridLayoutWidget_4.setGeometry(QRect(0, 0, 1681, 711))
        self.gridLayout_10 = QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_13.addItem(self.verticalSpacer_10, 4, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_13.addItem(self.horizontalSpacer_3, 1, 2, 1, 1)

        self.AgenciesTableView = QTableView(self.gridLayoutWidget_4)
        self.AgenciesTableView.setObjectName(u"AgenciesTableView")
        self.AgenciesTableView.setMaximumSize(QSize(16777215, 500))

        self.gridLayout_13.addWidget(self.AgenciesTableView, 3, 0, 1, 1)

        self.label_8 = QLabel(self.gridLayoutWidget_4)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font3)
        self.label_8.setStyleSheet(u"")

        self.gridLayout_13.addWidget(self.label_8, 1, 1, 1, 1)

        self.TripsTableView = AnimatedTableView(self.gridLayoutWidget_4)
        self.TripsTableView.setObjectName(u"TripsTableView")
        self.TripsTableView.setMaximumSize(QSize(16777215, 500))

        self.gridLayout_13.addWidget(self.TripsTableView, 3, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font2)
        self.label_5.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_5.setStyleSheet(u"")

        self.gridLayout_13.addWidget(self.label_5, 1, 0, 1, 1)


        self.gridLayout_10.addLayout(self.gridLayout_13, 0, 0, 1, 1)

        self.main_view_stacked_widget.addWidget(self.create_select_page)
        self.create_create_page = QWidget()
        self.create_create_page.setObjectName(u"create_create_page")
        sizePolicy4.setHeightForWidth(self.create_create_page.sizePolicy().hasHeightForWidth())
        self.create_create_page.setSizePolicy(sizePolicy4)
        self.create_create_page.setMaximumSize(QSize(1400, 600))
        self.create_create_page.setSizeIncrement(QSize(0, 0))
        self.layoutWidget = QWidget(self.create_create_page)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 1391, 595))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_23 = QGridLayout()
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.gridLayout_23.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.comboBox_direction = QComboBox(self.layoutWidget)
        self.comboBox_direction.addItem("")
        self.comboBox_direction.addItem("")
        self.comboBox_direction.setObjectName(u"comboBox_direction")
        self.comboBox_direction.setEnabled(False)
        self.comboBox_direction.setMaximumSize(QSize(200, 16777215))
        self.comboBox_direction.setFont(font3)
        self.comboBox_direction.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.comboBox_direction, 2, 0, 1, 1)

        self.btnStart = QPushButton(self.layoutWidget)
        self.btnStart.setObjectName(u"btnStart")
        self.btnStart.setEnabled(False)
        self.btnStart.setFont(font3)
        self.btnStart.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.btnStart, 17, 0, 1, 1)

        self.label_15 = QLabel(self.layoutWidget)
        self.label_15.setObjectName(u"label_15")
        font6 = QFont()
        font6.setFamilies([u"72"])
        font6.setBold(True)
        font6.setItalic(False)
        self.label_15.setFont(font6)
        self.label_15.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.label_15, 1, 1, 1, 1)

        self.comboBox_time_format = QComboBox(self.layoutWidget)
        self.comboBox_time_format.addItem("")
        self.comboBox_time_format.addItem("")
        self.comboBox_time_format.setObjectName(u"comboBox_time_format")
        self.comboBox_time_format.setEnabled(False)
        self.comboBox_time_format.setFont(font3)
        self.comboBox_time_format.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.comboBox_time_format, 2, 1, 1, 1)

        self.line_Selection_date_range = QLineEdit(self.layoutWidget)
        self.line_Selection_date_range.setObjectName(u"line_Selection_date_range")
        self.line_Selection_date_range.setEnabled(False)
        self.line_Selection_date_range.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.line_Selection_date_range, 10, 0, 1, 1)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font6)
        self.label_6.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.label_6, 11, 0, 1, 1)

        self.label_13 = QLabel(self.layoutWidget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font6)
        self.label_13.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.label_13, 4, 0, 1, 1)

        self.btnStop = QPushButton(self.layoutWidget)
        self.btnStop.setObjectName(u"btnStop")
        self.btnStop.setEnabled(False)
        self.btnStop.setFont(font3)
        self.btnStop.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.btnStop, 17, 1, 1, 1)

        self.label_12 = QLabel(self.layoutWidget)
        self.label_12.setObjectName(u"label_12")
        sizePolicy3.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy3)
        self.label_12.setFont(font3)
        self.label_12.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.label_12, 0, 0, 1, 1)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setEnabled(False)
        self.comboBox.setMaximumSize(QSize(200, 16777215))
        self.comboBox.setFont(font3)
        self.comboBox.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.comboBox, 3, 0, 1, 1)

        self.label_17 = QLabel(self.layoutWidget)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFont(font6)
        self.label_17.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.label_17, 9, 0, 1, 1)

        self.dateEdit = QDateEdit(self.layoutWidget)
        self.dateEdit.setObjectName(u"dateEdit")

        self.gridLayout_23.addWidget(self.dateEdit, 5, 0, 1, 1)

        self.listDatesWeekday = QTableView(self.layoutWidget)
        self.listDatesWeekday.setObjectName(u"listDatesWeekday")
        self.listDatesWeekday.setEnabled(False)
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy6.setHorizontalStretch(2)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.listDatesWeekday.sizePolicy().hasHeightForWidth())
        self.listDatesWeekday.setSizePolicy(sizePolicy6)
        self.listDatesWeekday.setMaximumSize(QSize(600, 1000))
        self.listDatesWeekday.setFont(font3)
        self.listDatesWeekday.setStyleSheet(u"")
        self.listDatesWeekday.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listDatesWeekday.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listDatesWeekday.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.listDatesWeekday.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.gridLayout_23.addWidget(self.listDatesWeekday, 12, 0, 1, 1)

        self.UseIndividualSorting = QCheckBox(self.layoutWidget)
        self.UseIndividualSorting.setObjectName(u"UseIndividualSorting")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(2)
        sizePolicy7.setVerticalStretch(1)
        sizePolicy7.setHeightForWidth(self.UseIndividualSorting.sizePolicy().hasHeightForWidth())
        self.UseIndividualSorting.setSizePolicy(sizePolicy7)
        self.UseIndividualSorting.setMaximumSize(QSize(200, 30))

        self.gridLayout_23.addWidget(self.UseIndividualSorting, 1, 0, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_23)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.tableView_sorting_stops = Customtableview(self.layoutWidget)
        self.tableView_sorting_stops.setObjectName(u"tableView_sorting_stops")
        sizePolicy.setHeightForWidth(self.tableView_sorting_stops.sizePolicy().hasHeightForWidth())
        self.tableView_sorting_stops.setSizePolicy(sizePolicy)
        self.tableView_sorting_stops.setMaximumSize(QSize(600, 300))

        self.verticalLayout.addWidget(self.tableView_sorting_stops)

        self.btnContinueCreate = QPushButton(self.layoutWidget)
        self.btnContinueCreate.setObjectName(u"btnContinueCreate")
        self.btnContinueCreate.setEnabled(False)
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.btnContinueCreate.sizePolicy().hasHeightForWidth())
        self.btnContinueCreate.setSizePolicy(sizePolicy8)
        self.btnContinueCreate.setMaximumSize(QSize(200, 200))

        self.verticalLayout.addWidget(self.btnContinueCreate)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_5)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.main_view_stacked_widget.addWidget(self.create_create_page)
        self.download_page = QWidget()
        self.download_page.setObjectName(u"download_page")
        sizePolicy4.setHeightForWidth(self.download_page.sizePolicy().hasHeightForWidth())
        self.download_page.setSizePolicy(sizePolicy4)
        self.download_page.setMaximumSize(QSize(1400, 600))
        self.gridLayoutWidget_2 = QWidget(self.download_page)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(-1, -1, 1681, 591))
        self.gridLayout_8 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_16 = QGridLayout()
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.tableView_2 = AnimatedTableView(self.gridLayoutWidget_2)
        self.tableView_2.setObjectName(u"tableView_2")
        self.tableView_2.setMaximumSize(QSize(16777215, 400))

        self.gridLayout_16.addWidget(self.tableView_2, 0, 0, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_16, 1, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_5, 1, 2, 1, 1)

        self.gridLayout_20 = QGridLayout()
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_20.addItem(self.horizontalSpacer_6, 0, 2, 1, 1)

        self.comboBox_display = QComboBox(self.gridLayoutWidget_2)
        self.comboBox_display.addItem("")
        self.comboBox_display.addItem("")
        self.comboBox_display.setObjectName(u"comboBox_display")
        self.comboBox_display.setEnabled(True)
        self.comboBox_display.setFont(font3)
        self.comboBox_display.setStyleSheet(u"")

        self.gridLayout_20.addWidget(self.comboBox_display, 5, 0, 1, 1)

        self.btnLoadOnlineData = FadingButton(self.gridLayoutWidget_2)
        self.btnLoadOnlineData.setObjectName(u"btnLoadOnlineData")
        self.btnLoadOnlineData.setEnabled(False)
        self.btnLoadOnlineData.setFont(font3)
        self.btnLoadOnlineData.setStyleSheet(u"")
        icon7 = QIcon()
        icon7.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/cloud-download-fill.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnLoadOnlineData.setIcon(icon7)
        self.btnLoadOnlineData.setIconSize(QSize(24, 24))

        self.gridLayout_20.addWidget(self.btnLoadOnlineData, 5, 2, 1, 1)

        self.label_14 = QLabel(self.gridLayoutWidget_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setFont(font5)
        self.label_14.setStyleSheet(u"")

        self.gridLayout_20.addWidget(self.label_14, 0, 0, 1, 1)

        self.lineInputPath_2 = QLineEdit(self.gridLayoutWidget_2)
        self.lineInputPath_2.setObjectName(u"lineInputPath_2")
        self.lineInputPath_2.setFont(font3)
        self.lineInputPath_2.setStyleSheet(u"")

        self.gridLayout_20.addWidget(self.lineInputPath_2, 2, 0, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_20, 0, 0, 1, 1)

        self.btnDownloadSelected = FadingButton(self.gridLayoutWidget_2)
        self.btnDownloadSelected.setObjectName(u"btnDownloadSelected")
        self.btnDownloadSelected.setFont(font3)
        self.btnDownloadSelected.setIcon(icon5)
        self.btnDownloadSelected.setIconSize(QSize(24, 24))

        self.gridLayout_8.addWidget(self.btnDownloadSelected, 1, 1, 1, 1)

        self.main_view_stacked_widget.addWidget(self.download_page)

        self.gridLayout_4.addWidget(self.main_view_stacked_widget, 1, 0, 1, 1)

        self.splitter.addWidget(self.main_widget)
        self.main_view_stacked_widget.raise_()
        self.bottom_info_widget.raise_()
        self.top_widget.raise_()

        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
#if QT_CONFIG(shortcut)
        self.label_11.setBuddy(self.lineInputPath)
        self.label_10.setBuddy(self.lineOutputPath)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(MainWindow)
        self.btnExit.clicked.connect(MainWindow.close)
        self.pushButton.toggled.connect(self.menu_widget.setHidden)

        self.toolBox.setCurrentIndex(0)
        self.main_view_stacked_widget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"General Information", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("MainWindow", u"General", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Import", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Create", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QCoreApplication.translate("MainWindow", u"Create Table", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"Download GTFS Data", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), QCoreApplication.translate("MainWindow", u"Download GTFS", None))
        self.btnExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.line_Selection_format.setText(QCoreApplication.translate("MainWindow", u"Agency", None))
        self.line_Selection_agency.setText(QCoreApplication.translate("MainWindow", u"Route", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Selection</span></p></body></html>", None))
        self.pushButton.setText("")
        self.plainTextEdit.setPlainText(QCoreApplication.translate("MainWindow", u"GTFStoFahrplan is a Python script designed to convert GTFS (General Transit Feed Specification) data into Fahrplan-compatible format. Fahrplan is a widely-used transit schedule format primarily used in the German-speaking regions.\n"
"\n"
"Before using GTFStoFahrplan, make sure you have GTFS data available. GTFS data can be obtained from various public transportation agencies or repositories.\n"
"\n"
"For more information visit:\n"
"https://github.com/Themishau/GTFStoFahrplan\n"
"\n"
"Ressources:\n"
"\n"
"- VBB - Verkehrsverbund Berlin-Brandenburg GmbH https://daten.berlin.de/datensaetze/vbb-fahrplandaten-gtfs\n"
"\n"
"- Open Data Portal Metropole Ruhr https://opendata.ruhr/\n"
"\n"
"- Img by Menschen Vektor erstellt von pch.vector - de.freepik.com\n"
"\n"
"- Icons by Petras Nargela\n"
"\n"
"- PySide6 is used.", None))
        self.lineInputPath.setText("")
        self.lineInputPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"C:/Tmp/GTFS.zip", None))
        self.btnGetPickleFile.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">input data</span></p></body></html>", None))
        self.btnGetOutputDir.setText("")
        self.lineOutputPath.setText("")
        self.lineOutputPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"C:/Tmp/", None))
        self.btnGetFile.setText("")
        self.btnImport.setText(QCoreApplication.translate("MainWindow", u"Start Import", None))
        self.picklesavename.setText("")
        self.picklesavename.setPlaceholderText(QCoreApplication.translate("MainWindow", u"C:/Tmp/GTFS.zip", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">output path</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.checkBox_savepickle.setToolTip(QCoreApplication.translate("MainWindow", u"saves data to faster format", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.checkBox_savepickle.setWhatsThis(QCoreApplication.translate("MainWindow", u"saves data to faster format", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_savepickle.setText(QCoreApplication.translate("MainWindow", u"save data to pickle format", None))
        self.btnRestart.setText(QCoreApplication.translate("MainWindow", u"Restart Import", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Information Import:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Trips</span></p></body></html>", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Agencies</span></p></body></html>", None))
        self.comboBox_direction.setItemText(0, QCoreApplication.translate("MainWindow", u"direction 1", None))
        self.comboBox_direction.setItemText(1, QCoreApplication.translate("MainWindow", u"direction 2", None))

        self.btnStart.setText(QCoreApplication.translate("MainWindow", u"Create Table", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Time Format</span></p></body></html>", None))
        self.comboBox_time_format.setItemText(0, QCoreApplication.translate("MainWindow", u"1", None))
        self.comboBox_time_format.setItemText(1, QCoreApplication.translate("MainWindow", u"2", None))

        self.label_6.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Weekday</span></p></body></html>", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Date</span></p></body></html>", None))
        self.btnStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Mode Settings</span></p></body></html>", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Date", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Weekday", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Umlaufplan Date", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Umlaufplan Weekday", None))

        self.label_17.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Detected Date Range</span></p></body></html>", None))
        self.UseIndividualSorting.setText(QCoreApplication.translate("MainWindow", u"Use individual sorting", None))
        self.btnContinueCreate.setText(QCoreApplication.translate("MainWindow", u"Continue Creating Table", None))
        self.comboBox_display.setItemText(0, QCoreApplication.translate("MainWindow", u"opendata.ruhr", None))
        self.comboBox_display.setItemText(1, QCoreApplication.translate("MainWindow", u"opendata.vbb", None))

        self.btnLoadOnlineData.setText(QCoreApplication.translate("MainWindow", u"Load Online Data", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Save Location</span></p></body></html>", None))
        self.lineInputPath_2.setText("")
        self.lineInputPath_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"C:/Tmp/", None))
        self.btnDownloadSelected.setText(QCoreApplication.translate("MainWindow", u"Download Selected Data", None))
    # retranslateUi

