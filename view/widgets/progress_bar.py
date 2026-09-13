# -*- coding: utf-8 -*-

class ProgressBar:
    def __init__(self):
        self.progress = 0

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
