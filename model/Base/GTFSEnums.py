from enum import Enum, auto

'''
This file contains all used types and names

For learning reasons, I implemented a Subscriber/Observer

'''

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


'''
Enums to show all available Subscriber and Observer methods
'''

class SchedulePlanerFunctionEnum(Enum):
    nothing = 'nothing'


class UpdateGuiEnum(Enum):
    update_import_path = 'update_import_path'
    update_routes_list = 'update_routes_list'
    update_stopname_create_list = 'update_stopname_create_list'
    update_date_range = 'update_date_range'
    update_weekday_list = 'update_weekday_list'
    update_agency_list = 'update_agency_list'
    update_weekdate_option = 'update_weekdate_option'
    update_progress_bar = 'update_progress_bar'
    import_finished = 'import_finished'
    show_error = 'show_error'
    message = 'message'
    data_changed = 'data_changed'
    restart = 'restart'

class ModelTriggerActionsEnum(Enum):
    planer_start_load_data = 'planer_start_load_data'
    planer_select_agency = 'planer_select_agency'
    planer_select_weekday = 'planer_select_weekday'
    planer_reset_gtfs = 'planer_reset_gtfs'
    planer_start_create_table = 'planer_start_create_table'
    planer_start_create_table_continue = 'planer_start_create_table_continue'


class SchedulePlanerTriggerActionsEnum(Enum):
    import_GTFS = 'import_GTFS'
    get_routes_list_based_on_agency = 'get_routes_list_based_on_agency'
    get_agency_list = 'get_agency_list'
    create_plan = 'create_plan'
    export_plan = 'export_plan'
    schedule_planer_load_gtfsdata_event = 'schedule_planer_load_gtfsdata_event'
    schedule_planer_select_agency = 'schedule_planer_select_agency'
    schedule_planer_select_weekday = 'schedule_planer_select_weekday'
    schedule_planer_reset_schedule_planer = 'schedule_planer_reset_gtfs'
    schedule_planer_start_create_table = 'schedule_planer_start_create_table'
    schedule_planer_start_create_table_continue = 'schedule_planer_start_create_table_continue'
    schedule_planer_update_routes_list = 'schedule_planer_update_routes_list'
    schedule_planer_create_output_fahrplan_date = 'schedule_planer_create_output_fahrplan_date'
    schedule_planer_create_output_fahrplan_date_indi = 'schedule_planer_create_output_fahrplan_date_indi'
    schedule_planer_create_output_fahrplan_date_indi_continue = 'schedule_planer_create_output_fahrplan_date_indi_continue'
    schedule_planer_create_output_fahrplan_weekday = 'schedule_planer_create_output_fahrplan_weekday'


class ControllerTriggerActionsEnum(Enum):
    restart = 'restart'


class ImportDataFuncitonEnum(Enum):
    import_GTFS = 'import_GTFS'
    update_progress_bar = 'update_progress_bar'


class ErrorMessageRessources(Enum):
    import_data_error = 'no data in imported_data.'
    no_import_object_generated = 'No import object generated.'
    no_create_object_generated = 'No create object generated.'
    error_in_SchedulePlaner_class = 'error_in_SchedulePlaner_class'
    error_load_data = 'Error. Could not load data.'


class InfoMessageRessources(Enum):
    export_complete = 'export completed.'
