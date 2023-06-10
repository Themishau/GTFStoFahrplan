# -*- coding: utf-8 -*-
# import sys
# import os
#
# from PySide2.QtGui import QGuiApplication
# from PySide2.QtQml import QQmlApplicationEngine

from GUI_Q5_test import main

if __name__ == '__main__':
      # app = QGuiApplication(sys.argv)
      # engine = QQmlApplicationEngine()
      # engine.load(os.path.join(os.path.dirname(__file__), "qml/splashScreen.qml"))
      main(['update_process',
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
            'get_date_range'], 'controller')
      # if not engine.rootObjects():
      #       sys.exit(-1)
      # sys.exit(app.exec_())






