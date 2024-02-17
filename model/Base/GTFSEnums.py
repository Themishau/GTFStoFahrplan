from enum import Enum, auto


class CreatePlanMode(Enum):
    """ Types of methods """
    date = 'date'
    weekday = 'weekday'


class GtfsColumnNames(Enum):
    stopsList = 'stopsList'
    stopTimesList = 'stopTimesList'
    tripsList = 'tripsList'
    calendarList = 'calendarList'
    calendar_datesList = 'calendar_datesList'
    routesList = 'routesList'
    agencyList = 'agencyList'
    feed_info = 'feed_info'


class GtfsDfNames(Enum):
    Routes = 'Routes'
    Trips = 'Trips'
    Stoptimes = 'Stoptimes'
    Stops = 'Stops ='
    Calendarweeks = 'Calendarweeks'
    Calendardates = 'Calendardates'
    Agencies = 'Agencies'
    Feedinfos = 'Feedinfos'


class SubscriberTypes(Enum):
    update_gui = 'update_gui'
    trigger_action = 'trigger_action'


class SchedulePlanerFunctionEnum(Enum):
    nothing = 'nothing'


class UpdateGuiEnum(Enum):
    update_routes_list = 'update_routes_list'
    update_stopname_create_list = 'update_stopname_create_list'
    update_date_range = 'update_date_range'
    update_weekday_list = 'update_weekday_list'
    update_agency_list = 'update_agency_list'
    update_weekdate_option = 'update_weekdate_option'
    update_progress_bar = 'update_progress_bar'
    message = 'message'


class SchedulePlanerTriggerActionsEnum(Enum):
    import_GTFS = 'import_GTFS'
    get_routes_list_based_on_agency = 'get_routes_list_based_on_agency'
    get_agency_list = 'get_agency_list'
    create_plan = 'create_plan'
    export_plan = 'export_plan'


class ControllerTriggerActionsEnum(Enum):
    restart = 'restart'


class ImportDataFuncitonEnum(Enum):
    import_GTFS = 'import_GTFS'
    update_progress_bar = 'update_progress_bar'


class ErrorMessageRessources(Enum):
    import_data_error = 'no data in imported_data.'
    no_import_object_generated = 'No import object generated.'


class InfoMessageRessources(Enum):
    export_complete = 'export completed.'
