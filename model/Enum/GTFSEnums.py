from enum import Enum

'''
This file contains all used types and names
'''


class ProcessType(Enum):
    """ Types of process """
    import_data = "import_data"
    create_table = "create_table"
    create_plan = "create_plan"
    export_plan = "export_plan"


class ProcessTypeImport(Enum):
    """ Types of import process """
    import_gtfs = "import_gtfs"
    import_gtfs_continue = "import_gtfs_continue"
    import_gtfs_finished = "import_gtfs_finished"
    import_gtfs_error = "import_gtfs_error"


class ProcessTypeCreateTable(Enum):
    """ Types of create table process """
    create_table = "create_table"
    create_table_continue = "create_table_continue"
    create_table_finished = "create_table_finished"
    create_table_error = "create_table_error"


class ProceessTypeExport(Enum):
    """ Types of export process """
    export_plan = "export_plan"
    export_plan_continue = "export_plan_continue"
    export_plan_finished = "export_plan_finished"
    export_plan_error = "export_plan_error"


class CreatePlanMode(Enum):
    """ Types of methods """
    date = 0
    weekday = 1
    umlauf_date = 2
    umlauf_weekday = 3


class Direction(Enum):
    """ Types of direction """
    direction_1 = 0
    direction_2 = 1


class GtfsColumnNames(Enum):
    stopsList = 'stopsList'
    stopTimesList = 'stopTimesList'
    tripsList = 'tripsList'
    calendarList = 'calendarList'
    calendar_datesList = 'calendar_datesList'
    routesList = 'routesList'
    agencyList = 'agencyList'
    feed_info = 'feedList'


class GtfsDfNames(Enum):
    Routes = 'Routes'
    Trips = 'Trips'
    Stoptimes = 'Stoptimes'
    Stops = 'Stops'
    Calendarweeks = 'Calendarweeks'
    Calendardates = 'Calendardates'
    Agencies = 'Agencies'
    Feedinfos = 'Feedinfos'


class GtfsProcessingStep(Enum):
    Stops = (20, "Tmp/dfStops.pkl")
    Stoptimes = (30, "Tmp/dfStopTimes.pkl")
    Trips = (40, "Tmp/dfTrips.pkl")
    Calendarweeks = (50, "Tmp/dfWeek.pkl")
    Calendardates = (60, "Tmp/dfDates.pkl")
    Routes = (70, "Tmp/dfRoutes.pkl")
    Agencies = (80, "Tmp/dfagency.pkl")

    def __init__(self, progress_value, file_path):
        self.progress_value = progress_value
        self.file_path = file_path

    @property
    def df_name(self):
        return GtfsDfNames[self.name]


class DateProcessingStep(Enum):
    INIT = (10, "Initialize date processing")
    PREPARE_DATA = (20, "Prepare data")
    SELECT_DATES = (30, "Select dates for date range")
    HANDLE_EXCEPTIONS = (40, "Handle date exceptions")
    SELECT_STOPS = (50, "Select stops for trips")
    PROCESS_DATES = (70, "Process dates and trips")
    CREATE_SORT = (80, "Create and sort stop names")
    CREATE_PLAN = (90, "Create final plan")


class DfStopColumnEnum(Enum):
    stop_id = 'stop_id'
    stop_name = 'stop_name'


class DfTripColumnEnum(Enum):
    trip_id = 'trip_id'
    route_id = 'route_id'
    service_id = 'service_id'
    direction_id = 'direction_id'


class DfRouteColumnEnum(Enum):
    route_id = 'route_id'
    route_short_name = 'route_short_name'
    route_long_name = 'route_long_name'
    agency_id = 'agency_id'


class DfAgencyColumnEnum(Enum):
    agency_id = 'agency_id'
    agency_name = 'agency_name'


class DfFeedinfoColumnEnum(Enum):
    feed_publisher_name = 'feed_publisher_name'
    feed_publisher_url = 'feed_publisher_url'
    feed_start_date = 'feed_start_date'
    feed_end_date = 'feed_end_date'


class DfCalendarweekColumnEnum(Enum):
    service_id = 'service_id'
    start_date = 'start_date'
    end_date = 'end_date'
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'


class DfCalendardateColumnEnum(Enum):
    date_day_format = 'date_day_format'
    service_id = 'service_id'
    date = 'date'
    day = 'day'
    exception_type = 'exception_type'


class DfStopTimesColumnEnum(Enum):
    trip_id = 'trip_id'
    arrival_time = 'arrival_time'
    departure_time = 'departure_time'
    stop_id = 'stop_id'
    stop_sequence = 'stop_sequence'
    stop_headsign = 'stop_headsign'


class SubscriberTypes(Enum):
    update_gui = 'update_gui'
    trigger_action = 'trigger_action'


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
    no_import_object_generated = 'There has been an error while importing GTFS data.'
    missing_import_object_generated = 'There are missing columns in imported data.'
    no_create_object_generated = 'There has been an error while creating file.'
    no_export_object_generated = 'There has been an error while exporting data to file.'
    error_in_SchedulePlaner_class = 'error_in_SchedulePlaner_class'
    error_load_data = 'Error. Could not load data.'
    no_trips_found = 'No trips found for the selected date range.'
    no_trips_found_in_date_range = 'No trips found in the selected date range.'


class InfoMessageRessources(Enum):
    export_complete = 'export completed.'


class Weekday(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    # WEEKEND category
    WEEKEND = SATURDAY or SUNDAY

    @classmethod
    def is_weekday(cls, day):
        return isinstance(day, Weekday) and day not in cls.WEEKEND

    @classmethod
    def is_weekend(cls, day):
        return isinstance(day, Weekday) and day in cls.WEEKEND
