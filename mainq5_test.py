# -*- coding: utf-8 -*-
import sys
from GUI_Q5_test import Gui
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
from ui_splash_screen import Ui_SplashScreen


counter = 0
class SplashScreen(QMainWindow):
      # def __init__(self, application_window):
      #     super().__init__(events=events, name=name)
      def __init__(self, application_window):
            QMainWindow.__init__(self)
            self.ui = Ui_SplashScreen()
            self.ui.setupUi(self)
            self.application_window = application_window

            ## UI ==> INTERFACE CODES
            ########################################################################

            ## REMOVE TITLE BAR
            self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)


            ## DROP SHADOW EFFECT
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(20)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 60))
            self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

            ## QTIMER ==> START
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.progress)
            # TIMER IN MILLISECONDS
            self.timer.start(35)

            # CHANGE DESCRIPTION

            # Initial Text
            self.ui.label_description.setText("<strong>WELCOME</strong> GTFS TimeTabler")

            # Change Texts
            QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>LOADING</strong> USER INTERFACE."))
            QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>LOADING</strong> USER INTERFACE..."))


            ## SHOW ==> MAIN WINDOW
            ########################################################################
            self.show()
            ## ==> END ##

      ## ==> APP FUNCTIONS
      ########################################################################
      def progress(self):

            global counter

            # SET VALUE TO PROGRESS BAR
            self.ui.progressBar.setValue(counter)

            # CLOSE SPLASH SCREE AND OPEN APP
            if counter > 100:
                  # STOP TIMER
                  self.timer.stop()

                  # SHOW MAIN WINDOW
                  self.main = self.application_window
                  self.main.show()

                  # CLOSE SPLASH SCREEN
                  self.close()

            # INCREASE COUNTER
            counter += 1


if __name__ == '__main__':
      gtfs_app = QApplication(sys.argv)
      application_window = Gui(events=['update_process',
                                       'toggle_button_direction_event',
                                       'toggle_button_date_week_event',
                                       'message_test',
                                       'load_gtfsdata_event',
                                       'select_agency',
                                       'select_route',
                                       'select_weekday',
                                       'start_create_table',
                                       'reset_gtfs',
                                       'send_message_box',
                                       'get_date_range'], name='controller')
      # application_window.show()
      window = SplashScreen(application_window)
      sys.exit(gtfs_app.exec_())







