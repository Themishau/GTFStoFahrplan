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
import h5py
from PyQt5.QtCore import QAbstractTableModel

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


# noinspection SqlResolve
class Umlaufplaner(Publisher, Subscriber):

    def __init__(self, events, name):
        super().__init__(events=events, name=name)
        self.notify_functions = {
        }



    def createUmlaufPlanExperimential(self):

        """
        Just a prototype to create Umlaufpläne.
        I do not know the english equivalent. It describes a schedule for each bus/train.

        Algorithm:
        - get schedule for a day with both directions (use the already implemented action)
        - take the last stop and get the next starttime for opposite direction
        - do it for all start times
        ! there might be some errors if the ride ends after 12 pm or early in the morning -> but we will deal with it later

        :return: 2 schedules for each bus/train both directions. -> is currently used for creating a csv / Excel document
        """

