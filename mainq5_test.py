# -*- coding: utf-8 -*-
import sys
from GUI_Q5_test import Gui
from SplashScreen import SplashScreen

from PyQt5.QtWidgets import *

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







