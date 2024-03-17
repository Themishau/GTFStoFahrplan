from PyQt5.QtCore import QEvent
from model.Base.GTFSEnums import *

costum_event_incrementer = 1


class ProgressUpdateEvent(QEvent):
    def __init__(self, progress):
        global costum_event_incrementer
        super().__init__(QEvent.Type(QEvent.User + costum_event_incrementer))
        costum_event_incrementer += 1
        self.progress = progress
        self.event_type = UpdateGuiEnum.update_progress_bar


class ShowErrorMessageEvent(QEvent):
    def __init__(self, message):
        global costum_event_incrementer
        super().__init__(QEvent.Type(QEvent.User + costum_event_incrementer))
        costum_event_incrementer += 1
        self.message = message
        self.event_type = UpdateGuiEnum.show_error


class UpdateAgencyListEvent(QEvent):
    def __init__(self, message):
        global costum_event_incrementer
        super().__init__(QEvent.Type(QEvent.User + costum_event_incrementer))
        costum_event_incrementer += 1
        self.message = message
        self.event_type = UpdateGuiEnum.update_agency_list
