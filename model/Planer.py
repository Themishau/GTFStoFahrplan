# -*- coding: utf-8 -*-
from model.observer import Publisher, Subscriber
import time
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re
import logging
import sys
import os
from gtfs import gtfs
from umlaufplaner import Umlaufplaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


# noinspection SqlResolve
class Planer(Publisher, Subscriber):

    def __init__(self, events, name):
        super().__init__(events=events, name=name)
        self.notify_functions = {
        }

