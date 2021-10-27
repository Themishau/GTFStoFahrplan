# -*- coding: utf-8 -*-

from gui import Controller
from GUI_Q5 import main

if __name__ == '__main__':
    print("start")
    main(['update_process', 'toggle_button_direction_event', 'toggle_button_date_week_event'], 'controller')
    # gtfsMenu = Controller(['update_process', 'toggle_button_direction_event', 'toggle_button_date_week_event'], 'controller')
    # gtfsMenu.run()
