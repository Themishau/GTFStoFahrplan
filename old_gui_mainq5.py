# -*- coding: utf-8 -*-
from old_controller import main

if __name__ == '__main__':
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

