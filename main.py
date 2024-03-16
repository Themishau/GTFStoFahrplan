# -*- coding: utf-8 -*-
import sys
from controller import Controller
from model.Base.GTFSEnums import ModelTriggerActionsEnum
from view.splash_screen import SplashScreen

from PyQt5.QtWidgets import *

if __name__ == '__main__':
    gtfs_app = QApplication(sys.argv)

    # I can trigger events in this event list
    application_window = Controller(events=[ModelTriggerActionsEnum.planer_start_load_data,
                                            ModelTriggerActionsEnum.planer_select_agency,
                                            ModelTriggerActionsEnum.planer_select_weekday,
                                            ModelTriggerActionsEnum.planer_reset_gtfs,
                                            ModelTriggerActionsEnum.planer_start_create_table,
                                            ModelTriggerActionsEnum.planer_start_create_table_continue
                                            ], name='controller')
    # show a nice loading window first
    window = SplashScreen(application_window)

    sys.exit(gtfs_app.exec_())
