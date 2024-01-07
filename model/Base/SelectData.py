# -*- coding: utf-8 -*-
from model.observer import Publisher, Subscriber
import time
import pandas as pd
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re
import logging
import sys
import os
from enum import Enum, auto
from model.Base.ProgressBar import ProgressBar
from model.Base.ImportData import ImportData

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SelectData(Publisher, Subscriber):
    def __init__(self, events, name, progress: int):
        super().__init__(events=events, name=name)
        self.imported_data = None
        self.agencies_list = None
        self.df_selected_routes = None

        self.selected_agency = None
        self.selected_route = None
        self.selected_weekday = None
        self.selected_dates = None

        self.header_for_export_data = None
        self.df_header_for_export_data = None
        self.last_time = time.time()
        self.df_direction = None

        self.reset_select_data = False
        self.create_plan_mode = None
        self.progress = progress

        self.notify_functions = {
            'fill_agency_list': [self.get_routes_of_agency, False],
        }

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    @property
    def agencies_list(self):
        return self._agencies_list

    @agencies_list.setter
    def agencies_list(self, value):
        self._agencies_list = value
        self.dispatch("update_agency_list",
                      "update_agency_list routine started! Notify subscriber!")

    @property
    def imported_data(self):
        return self._imported_data

    @imported_data.setter
    def imported_data(self, value):
        self._imported_data = value

    def get_routes_of_agency(self) -> None:
        if self.selected_agency is not None:
            self.select_gtfs_routes_from_agency()

    def select_gtfs_routes_from_agency(self):
        df_routes = self.imported_data["df_routes"]
        input_var = [{'agency_id': self.selected_agency}]
        var_test = pd.DataFrame(input_var).set_index('agency_id')
        cond_routes_of_agency = '''
                    select *
                    from df_routes 
                    left join var_test
                    where var_test.agency_id = df_routes.agency_id
                    order by df_routes.route_short_name;
                   '''
        routes_list = sqldf(cond_routes_of_agency, locals())
        """
        todo
        """
        self.df_selected_routes = routes_list
        return True

    def read_gtfs_agencies(self):
        df_agency = self.imported_data["df_agency"]
        cond_agencies = '''
                    select *
                    from df_agency 
                    order by df_agency.agency_id;
                   '''
        agency_list = sqldf(cond_agencies, locals())
        agency_list = agency_list.values.tolist()
        agency_str_list = []
        for lists in agency_list:
            agency_str_list.append('{},{}'.format(lists[0], lists[1]))
        self.agencies_list = agency_str_list
        # print (agency_list.values.tolist())
        return True