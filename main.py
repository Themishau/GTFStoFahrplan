# -*- coding: utf-8 -*-

from gui import Controller


if __name__ == '__main__':
    print("start")
    gtfsMenu = Controller(['update_process', 'toggle_button_direction_event', 'toggle_button_date_week_event'], 'controller')
    gtfsMenu.run()
