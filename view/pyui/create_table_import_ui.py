# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_table_import.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGridLayout,
                               QLabel, QLayout, QLineEdit,
                               QPushButton, QSizePolicy, QSpacerItem, QTableWidget)

from view.Custom.FadingButton import FadingButton
from view.ui.res import resource_boot
from view.ui.res import resource_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1100, 500)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(0, 0))
        Form.setMaximumSize(QSize(1100, 900))
        Form.setLayoutDirection(Qt.LeftToRight)
        Form.setStyleSheet(u"#Form {\n"
"border-style: solid;\n"
"border-color:  #f2f7f5;\n"
"background: #cfe2da; \n"
"\n"
"}\n"
"\n"
"#Form QPushButton {\n"
"	background-color: #587b6d;\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#f2b198;\n"
"}\n"
"\n"
"#Form QLineEdit {\n"
"	background-color: #F0FCF7;\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"#Form QLabel {\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 5px;\n"
"	text-align: center;\n"
"    color:#41312b;\n"
"}\n"
"\n"
"#Form QComboBox {\n"
"	background-color: #587b6d;\n"
"   border-radius: 10px;\n"
"	padding: 5px 5px 5px 100px;\n"
"	text-align: center;\n"
"    color:#f2b198;\n"
"    \n"
"}\n"
"\n"
"#Form QPushButton:hover {\n"
"	background-color: #408d49;\n"
"   border-radius: 10px;\n"
"       color:#fde1d6;\n"
"}\n"
"")
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")
        font = QFont()
        font.setFamilies([u"MS Reference Sans Serif"])
        self.label_11.setFont(font)
        self.label_11.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.label_11, 1, 0, 1, 1)

        self.btnImport = QPushButton(Form)
        self.btnImport.setObjectName(u"btnImport")
        self.btnImport.setEnabled(True)
        font1 = QFont()
        font1.setPointSize(12)
        self.btnImport.setFont(font1)
        self.btnImport.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.btnImport, 4, 1, 1, 1)

        self.btnGetPickleFile = QPushButton(Form)
        self.btnGetPickleFile.setObjectName(u"btnGetPickleFile")
        self.btnGetPickleFile.setEnabled(True)
        self.btnGetPickleFile.setFont(font1)
        self.btnGetPickleFile.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u":/newPrefix/icons/bootstrap-icons-1.10.3/file-earmark-arrow-up.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnGetPickleFile.setIcon(icon)
        self.TestButtoon = FadingButton("Click me")
        self.TestButtoon.setEnabled(True)
        self.gridLayout_3.addWidget(self.TestButtoon, 4, 2, 1, 1)

        self.gridLayout_3.addWidget(self.btnGetPickleFile, 3, 2, 1, 1)

        self.checkBox_savepickle = QCheckBox(Form)
        self.checkBox_savepickle.setObjectName(u"checkBox_savepickle")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.checkBox_savepickle.sizePolicy().hasHeightForWidth())
        self.checkBox_savepickle.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.checkBox_savepickle, 3, 0, 1, 1)

        self.btnGetOutputDir = QPushButton(Form)
        self.btnGetOutputDir.setObjectName(u"btnGetOutputDir")
        self.btnGetOutputDir.setEnabled(True)
        self.btnGetOutputDir.setFont(font1)
        self.btnGetOutputDir.setStyleSheet(u"")
        self.btnGetOutputDir.setIcon(icon)

        self.gridLayout_3.addWidget(self.btnGetOutputDir, 2, 2, 1, 1)

        self.picklesavename = QLineEdit(Form)
        self.picklesavename.setObjectName(u"picklesavename")
        self.picklesavename.setFont(font1)
        self.picklesavename.setStyleSheet(u"")
        self.picklesavename.setReadOnly(True)

        self.gridLayout_3.addWidget(self.picklesavename, 3, 1, 1, 1)

        self.btnGetFile = QPushButton(Form)
        self.btnGetFile.setObjectName(u"btnGetFile")
        self.btnGetFile.setEnabled(True)
        self.btnGetFile.setFont(font1)
        self.btnGetFile.setStyleSheet(u"")
        self.btnGetFile.setIcon(icon)

        self.gridLayout_3.addWidget(self.btnGetFile, 1, 2, 1, 1)

        self.lineOutputPath = QLineEdit(Form)
        self.lineOutputPath.setObjectName(u"lineOutputPath")
        self.lineOutputPath.setFont(font1)
        self.lineOutputPath.setStyleSheet(u"")
        self.lineOutputPath.setReadOnly(True)

        self.gridLayout_3.addWidget(self.lineOutputPath, 2, 1, 1, 1)

        self.label_10 = QLabel(Form)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font)
        self.label_10.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.label_10, 2, 0, 1, 1)

        self.lineInputPath = QLineEdit(Form)
        self.lineInputPath.setObjectName(u"lineInputPath")
        self.lineInputPath.setFont(font1)
        self.lineInputPath.setStyleSheet(u"")
        self.lineInputPath.setReadOnly(True)

        self.gridLayout_3.addWidget(self.lineInputPath, 1, 1, 1, 1)

        self.btnRestart = QPushButton(Form)
        self.btnRestart.setObjectName(u"btnRestart")
        self.btnRestart.setEnabled(False)
        self.btnRestart.setFont(font1)
        self.btnRestart.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.btnRestart, 5, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_3, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 18, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 18, 5, 1, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.tableWidget = QTableWidget(Form)
        self.tableWidget.setObjectName(u"tableWidget")

        self.gridLayout_5.addWidget(self.tableWidget, 1, 0, 1, 1)

        self.import_file_table_label = QLabel(Form)
        self.import_file_table_label.setObjectName(u"import_file_table_label")
        font2 = QFont()
        font2.setFamilies([u"MS Reference Sans Serif"])
        font2.setBold(False)
        self.import_file_table_label.setFont(font2)

        self.gridLayout_5.addWidget(self.import_file_table_label, 0, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_5, 0, 1, 1, 1)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.comboBox_display = QComboBox(Form)
        self.comboBox_display.addItem("")
        self.comboBox_display.addItem("")
        self.comboBox_display.setObjectName(u"comboBox_display")
        self.comboBox_display.setEnabled(True)
        self.comboBox_display.setFont(font1)
        self.comboBox_display.setStyleSheet(u"")

        self.gridLayout_4.addWidget(self.comboBox_display, 1, 0, 1, 1)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_4, 0, 5, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 1, 1, 2)

#if QT_CONFIG(shortcut)
        self.label_11.setBuddy(self.lineInputPath)
        self.label_10.setBuddy(self.lineOutputPath)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Form)
        self.checkBox_savepickle.toggled.connect(self.picklesavename.setEnabled)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">input data</span></p></body></html>", None))
        self.btnImport.setText(QCoreApplication.translate("Form", u"Start Import", None))
        self.btnGetPickleFile.setText("")
#if QT_CONFIG(tooltip)
        self.checkBox_savepickle.setToolTip(QCoreApplication.translate("Form", u"saves data to faster format", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.checkBox_savepickle.setWhatsThis(QCoreApplication.translate("Form", u"saves data to faster format", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_savepickle.setText(QCoreApplication.translate("Form", u"save data to pickle format", None))
        self.btnGetOutputDir.setText("")
        self.picklesavename.setText("")
        self.picklesavename.setPlaceholderText(QCoreApplication.translate("Form", u"C:/Tmp/GTFS.zip", None))
        self.btnGetFile.setText("")
        self.lineOutputPath.setText("")
        self.lineOutputPath.setPlaceholderText(QCoreApplication.translate("Form", u"C:/Tmp/", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">output path</span></p></body></html>", None))
        self.lineInputPath.setText("")
        self.lineInputPath.setPlaceholderText(QCoreApplication.translate("Form", u"C:/Tmp/GTFS.zip", None))
        self.btnRestart.setText(QCoreApplication.translate("Form", u"Restart Import", None))
        self.import_file_table_label.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.comboBox_display.setItemText(0, QCoreApplication.translate("Form", u"time format 1", None))
        self.comboBox_display.setItemText(1, QCoreApplication.translate("Form", u"time format 2", None))

        self.label.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

