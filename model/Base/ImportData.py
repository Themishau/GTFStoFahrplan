# -*- coding: utf-8 -*-
import concurrent.futures
import io
import logging
import os
import zipfile

import pandas as pd
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import Signal

from model.Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from model.Enum.GTFSEnums import *
from .Progress import ProgressSignal
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from ..Dto.ImportSettingsDto import ImportSettingsDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


def _check_paths():
    os.path.isfile()
    os.path.exists()


class ImportData(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self._pkl_loaded = False
        self.reset_import = False

        """ visual internal property """
        self.progress = ProgressSignal()

        self.current_process_string = ""
        self.missing_columns_in_gtfs_file = pd.DataFrame({
            'table': [],
            'column': []
        })

    @property
    def reset_import(self):
        return self._reset_import

    @reset_import.setter
    def reset_import(self, value):
        self._reset_import = value

    def _check_input_fields_based_on_settings(self, import_settings_dto: ImportSettingsDto) -> bool:
        if not _check_paths():
            self.error_occured.emit(f"could not read data from path: {import_settings_dto.input_path}")
            return False
        return None
    def pre_checks(self,  import_settings_dto: ImportSettingsDto):
        return import_settings_dto.input_path is not None

    def import_gtfs(self, import_settings_dto: ImportSettingsDto) -> GtfsDataFrameDto | None:
        self.progress.set_progress(0, ProcessType.import_data, "Import GTFS data started")
        self.progress_Update.emit(self.progress)
        if not self.pre_checks(import_settings_dto):
            self.progress_Update.emit(self.progress.set_progress(0, ProcessType.import_data, "pre checks"))
            self.reset_data_cause_of_error()
            return None

        imported_data = self.read_gtfs_data(import_settings_dto)
        if imported_data is None:
            self.error_occured.emit("Error while reading data!")

        if imported_data.get(GtfsDfNames.Feedinfos.name) is not None:
            gtfsDataFrameDto = GtfsDataFrameDto(imported_data[GtfsDfNames.Routes], imported_data[GtfsDfNames.Trips],
                                                imported_data[GtfsDfNames.Stoptimes], imported_data[GtfsDfNames.Stops],
                                                imported_data[GtfsDfNames.Calendarweeks],
                                                imported_data[GtfsDfNames.Calendardates],
                                                imported_data[GtfsDfNames.Agencies],
                                                imported_data[GtfsDfNames.Feedinfos])
        else:
            gtfsDataFrameDto = GtfsDataFrameDto(imported_data[GtfsDfNames.Routes], imported_data[GtfsDfNames.Trips],
                                                imported_data[GtfsDfNames.Stoptimes], imported_data[GtfsDfNames.Stops],
                                                imported_data[GtfsDfNames.Calendarweeks],
                                                imported_data[GtfsDfNames.Calendardates],
                                                imported_data[GtfsDfNames.Agencies], None)

        if imported_data is None:
            self.reset_data_cause_of_error()
            return None

        if import_settings_dto.pickle_export_checked is True and import_settings_dto.pickle_save_path_filename is not None:
            self.save_pickle(imported_data)
        self.progress_Update.emit(self.progress.set_progress(100, ProcessType.import_data, "import_gtfs done"))
        return gtfsDataFrameDto


    def read_pickle_from_zip(self, zf, file_name):
        with zf.open(file_name, mode="r") as file:
            compressed_data = file.read()
            with io.BytesIO(compressed_data) as byte_stream:
                return pd.read_pickle(byte_stream)

    def read_gtfs_data(self, import_settings_dto: ImportSettingsDto):
        df_gtfs_data = {}

        with zipfile.ZipFile(import_settings_dto.input_path) as zf:
            logging.debug(zf.namelist())
            for file in zf.namelist():
                if file.endswith('pkl'):
                    self._pkl_loaded = True
                    break

            if self._pkl_loaded is True:
                logging.debug('pickle data detected')
                for step in GtfsProcessingStep:
                    df_gtfs_data[step.df_name] = self.read_pickle_from_zip(zf, step.file_path)
                    self.progress_Update.emit(self.progress.set_progress(step.progress_value, ProcessType.import_data, step.name))

                try:
                    with zipfile.ZipFile(import_settings_dto.input_path) as zf:
                        with zf.open("Tmp/dffeed_info.pkl", mode="r") as feed_info:
                            df_gtfs_data["dffeed_info"] = pd.read_pickle(feed_info, compression='zip')
                except:
                    logging.debug('no feed info header')
                return df_gtfs_data

        if self._pkl_loaded is False:
            raw_data = {}

            try:
                with zipfile.ZipFile(import_settings_dto.input_path) as zf:
                    files_to_process = [
                        ("stops.txt", GtfsColumnNames.stopsList),
                        ("stop_times.txt", GtfsColumnNames.stopTimesList),
                        ("trips.txt", GtfsColumnNames.tripsList),
                        ("calendar.txt", GtfsColumnNames.calendarList),
                        ("calendar_dates.txt", GtfsColumnNames.calendar_datesList),
                        ("routes.txt", GtfsColumnNames.routesList),
                        ("agency.txt", GtfsColumnNames.agencyList)
                    ]

                    for filename, column_name in files_to_process:
                        header = self.read_file_from_zip(zf, filename, start_line=0)
                        if header:
                            raw_data[column_name] = [header[0].rstrip()]

                    for filename, column_name in files_to_process:
                        data = self.read_file_from_zip(zf, filename, start_line=1)
                        if data:
                            raw_data[column_name].extend(data)

            except Exception as e:
                logging.debug(f'Error processing GTFS files: {str(e)}')
                return None
            except:
                logging.debug('no feed info data')

            logging.debug(f"raw_data keys: {raw_data.keys()}")

            return self.create_dfs(raw_data)

    def read_file_from_zip(self, zip_file, filename, start_line=0):
        encodings = ["utf-8", "utf-8-sig"]
        try:
            for encoding in encodings:
                with io.TextIOWrapper(
                        zip_file.open(filename, mode="r"),
                        encoding=encoding
                ) as file:
                    lines = file.readlines()
                    if lines and not lines[0].startswith('\ufeff'):
                        return lines[start_line:] if lines else []

        except Exception as e:
            logging.debug(f'Error reading {filename}: {str(e)}')
            return []

    def print_all_headers(self, stopsHeader, stop_timesHeader, tripsHeader, calendarHeader, calendar_datesHeader,
                          routesHeader, agencyHeader, feed_infoHeader):
        logging.debug('stopsHeader          = {} \n'
                      'stop_timesHeader     = {} \n'
                      'tripsHeader          = {} \n'
                      'calendarHeader       = {} \n'
                      'calendar_datesHeader = {} \n'
                      'routesHeader         = {} \n'
                      'agencyHeader         = {} \n'
                      'feed_infoHeader      = {}'.format(stopsHeader, stop_timesHeader, tripsHeader, calendarHeader,
                                                         calendar_datesHeader, routesHeader, agencyHeader,
                                                         feed_infoHeader))

    """ reset methods """

    def create_dfs(self, raw_data):
        if raw_data is None:
            return None

        # Define processing steps
        dict_creation_steps = [
            ("routes", self.get_gtfs_routes),
            ("trips", self.get_gtfs_trips),
            ("stop_times", self.get_gtfs_stop_times),
            ("stops", self.get_gtfs_stops),
            ("week", self.get_gtfs_week),
            ("dates", self.get_gtfs_dates),
            ("agency", self.get_gtfs_agency)
        ]

        if raw_data.get(GtfsColumnNames.feed_info) is not None:
            dict_creation_steps.append(("feed_info", self.get_gtfs_feed_info))

        # Create dictionaries in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            processes = [executor.submit(func, raw_data)
                         for _, func in dict_creation_steps]

            raw_dict_data = {}
            for result in concurrent.futures.as_completed(processes):
                try:
                    name, data = result.result()
                    raw_dict_data[name] = data
                except Exception as e:
                    logging.debug(f"Error in dict creation for {name}: {str(e)}")
                    return None

        logging.debug(f"raw_dict_data creation: {raw_dict_data.keys()}")

        # Define DataFrame creation steps
        df_creation_steps = [
            ("routes", self.create_df_routes),
            ("trips", self.create_df_trips),
            ("stop_times", self.create_df_stop_times),
            ("stops", self.create_df_stops),
            ("week", self.create_df_week),
            ("dates", self.create_df_dates),
            ("agency", self.create_df_agency)
        ]

        if raw_dict_data.get(GtfsColumnNames.feed_info) is not None:
            df_creation_steps.append(("feed_info", self.create_df_feed))

        # Create DataFrames in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            processes = [executor.submit(func, raw_dict_data)
                         for _, func in df_creation_steps]

            df_collection = {}
            for result in concurrent.futures.as_completed(processes):
                try:
                    df = result.result()
                    df_collection[df.name] = df
                except Exception as e:
                    logging.debug(f"Error in DataFrame creation: {str(e)} {df.name.value if df is not None else 'unknown df'}")
                    return None

        logging.debug(f"df_collection creation: {df_collection.keys()}")
        return df_collection

    def get_gtfs_trips(self, raw_data):
        tripdict = {
        }

        headers = raw_data[GtfsColumnNames.tripsList][0].replace('"', "").split(",")
        itripDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            tripdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.tripsList].remove(raw_data[GtfsColumnNames.tripsList][0])

        for data in raw_data[GtfsColumnNames.tripsList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            tripDate = data.split(",")
            for idx in range(itripDate):
                tripdict[header_names[idx]].append(tripDate[idx])

        return GtfsDfNames.Trips, tripdict

    def get_gtfs_stops(self, raw_data):

        stopsdict = {
        }
        headers = raw_data[GtfsColumnNames.stopsList][0].replace('"', "").split(",")
        istopDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopsdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.stopsList].remove(raw_data[GtfsColumnNames.stopsList][0])

        for haltestellen in raw_data[GtfsColumnNames.stopsList]:
            haltestellen = haltestellen.replace(", ", " ")
            haltestellen = haltestellen.replace('"', "")
            haltestellen = haltestellen.replace('\n', "")
            stopData = haltestellen.split(",")

            for idx in range(istopDate):
                stopsdict[header_names[idx]].append(stopData[idx])

        return GtfsDfNames.Stops, stopsdict

    def get_gtfs_stop_times(self, raw_data):
        stopTimesdict = {
        }

        headers = raw_data[GtfsColumnNames.stopTimesList][0].replace('"', "").split(",")
        istopTimeData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopTimesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.stopTimesList].remove(raw_data[GtfsColumnNames.stopTimesList][0])

        for data in raw_data[GtfsColumnNames.stopTimesList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            stopTimeData = data.split(",")

            for idx in range(istopTimeData):
                stopTimesdict[header_names[idx]].append(stopTimeData[idx])

        return GtfsDfNames.Stoptimes, stopTimesdict

    def get_gtfs_week(self, raw_data):
        calendarWeekdict = {
        }

        headers = raw_data[GtfsColumnNames.calendarList][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarWeekdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.calendarList].remove(raw_data[GtfsColumnNames.calendarList][0])

        for data in raw_data[GtfsColumnNames.calendarList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDate = data.split(",")

            for idx in range(icalendarDate):
                calendarWeekdict[header_names[idx]].append(calendarDate[idx])

        return GtfsDfNames.Calendarweeks, calendarWeekdict

    def get_gtfs_dates(self, raw_data):
        calendarDatesdict = {
        }

        headers = raw_data[GtfsColumnNames.calendar_datesList][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarDatesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.calendar_datesList].remove(raw_data[GtfsColumnNames.calendar_datesList][0])

        for data in raw_data[GtfsColumnNames.calendar_datesList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDatesDate = data.split(",")
            for idx in range(icalendarDate):
                calendarDatesdict[header_names[idx]].append(calendarDatesDate[idx])

        return GtfsDfNames.Calendardates, calendarDatesdict

    def get_gtfs_routes(self, raw_data):
        routesFahrtdict = {
        }

        headers = raw_data[GtfsColumnNames.routesList][0].replace('"', "").split(",")
        iroutesFahrt = len(headers)
        header_names = []
        for haltestellen_header in headers:
            routesFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.routesList].remove(raw_data[GtfsColumnNames.routesList][0])

        for data in raw_data[GtfsColumnNames.routesList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            routesFahrtData = data.split(",")
            for idx in range(iroutesFahrt):
                routesFahrtdict[header_names[idx]].append(routesFahrtData[idx])

        return GtfsDfNames.Routes, routesFahrtdict

    def get_gtfs_feed_info(self, raw_data):
        feed_infodict = {
        }

        headers = raw_data[GtfsColumnNames.feed_info][0].replace('"', "").split(",")
        ifeed_infodict = len(headers)
        header_names = []
        for haltestellen_header in headers:
            feed_infodict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.feed_info].remove(raw_data[GtfsColumnNames.feed_info][0])

        for data in raw_data[GtfsColumnNames.feed_info]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            feed_infodictData = data.split(",")
            for idx in range(ifeed_infodict):
                feed_infodict[header_names[idx]].append(feed_infodictData[idx])

        return GtfsDfNames.Feedinfos, feed_infodict

    def get_gtfs_agency(self, raw_data):

        agencyFahrtdict = {
        }

        headers = raw_data[GtfsColumnNames.agencyList][0].replace('"', "").split(",")
        iagencyData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            agencyFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)
        raw_data[GtfsColumnNames.agencyList].remove(raw_data[GtfsColumnNames.agencyList][0])

        for data in raw_data[GtfsColumnNames.agencyList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            agencyData = data.split(",")
            for idx in range(iagencyData):
                agencyFahrtdict[header_names[idx]].append(agencyData[idx])

        return GtfsDfNames.Agencies, agencyFahrtdict

    # region creation dataframes

    def create_df_routes(self, raw_data):
        logging.debug("convert to df: create_df_routes")
        df_routes = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Routes])
        df_routes = self.drop_columns_by_enum(df_routes, DfRouteColumnEnum)
        df_routes.name = GtfsDfNames.Routes
        try:
            df_routes['route_long_name'] = df_routes['route_long_name'].astype('string')
            df_routes['agency_id'] = df_routes['agency_id'].astype('string')
            df_routes['route_type'] = df_routes['route_type'].astype('string')
            df_routes['route_id'] = df_routes['route_id'].astype('string')
            df_routes = df_routes.sort_values(DfRouteColumnEnum.route_short_name.value)
        except KeyError:
            logging.debug("can not convert df_routes: stop_id into int ")
        except ValueError:
            logging.debug("can not convert df_routes")
        except AttributeError:
            logging.debug("can not convert df_routes Attribute")
        self.missing_columns_in_df(df_routes, DfRouteColumnEnum)
        logging.debug("convert to df: df_routes finished")

        return df_routes

    def create_df_trips(self, raw_data):
        logging.debug("convert to df: create_df_trips")
        df_trips = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Trips])
        df_trips = self.drop_columns_by_enum(df_trips, DfTripColumnEnum)
        df_trips.name = GtfsDfNames.Trips
        """ lets try to convert every column to speed computing """
        try:
            df_trips['trip_id'] = df_trips['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert dfTrips")
        except ValueError:
            logging.debug("can not convert dfTrips")
        try:
            df_trips['service_id'] = df_trips['service_id'].astype('string')
        except KeyError:
            logging.debug("can not convert service_id")
        except ValueError:
            logging.debug("can not convert service_id")
        try:
            df_trips['route_id'] = df_trips['route_id'].astype('string')
        except KeyError:
            logging.debug("can not convert route_id")
        except ValueError:
            logging.debug("can not convert route_id")
        try:
            df_trips['direction_id'] = pd.to_numeric(df_trips['direction_id'], errors='coerce').fillna(0).astype(int)
        except KeyError:
            logging.debug("can not convert direction_id in  dfTrips")
        except ValueError:
            logging.debug("can not convert direction_id in  dfTrips")
        self.missing_columns_in_df(df_trips, DfTripColumnEnum)
        logging.debug("convert to df: create_df_trips finished")

        return df_trips

    def create_df_stop_times(self, raw_data):
        logging.debug("convert to df: create_df_stop_times")
        # DataFrame with every stop (time)
        df_stoptimes = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Stoptimes])
        df_stoptimes = self.drop_columns_by_enum(df_stoptimes, DfStopTimesColumnEnum)
        df_stoptimes.name = GtfsDfNames.Stoptimes
        try:
            df_stoptimes['stop_sequence'] = df_stoptimes['stop_sequence'].astype('int32')
            df_stoptimes['arrival_time'] = df_stoptimes['arrival_time'].astype('string')
            df_stoptimes['departure_time'] = df_stoptimes['departure_time'].astype('string')
            df_stoptimes['stop_id'] = df_stoptimes['stop_id'].astype('string')
            df_stoptimes['trip_id'] = df_stoptimes['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert df_stoptimes")
        except OverflowError:
            logging.debug("can not convert df_stoptimes")
        except ValueError:
            logging.debug("can not convert df_stoptimes")
        except AttributeError:
            logging.debug("can not convert df_stoptimes Attribute")
        self.missing_columns_in_df(df_stoptimes, DfStopTimesColumnEnum)
        logging.debug("convert to df: create_df_stop_times finished")

        return df_stoptimes

    def create_df_stops(self, raw_data):
        logging.debug("convert to df: create_df_stops")
        # DataFrame with every stop
        df_stops = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Stops])
        df_stops = self.drop_columns_by_enum(df_stops, DfStopColumnEnum)
        df_stops.name = GtfsDfNames.Stops
        try:
            df_stops['stop_id'] = df_stops['stop_id'].astype('string')
            df_stops['stop_name'] = df_stops['stop_name'].astype('string')
        except KeyError:
            logging.debug("can not convert df_Stops: stop_id into int ")
        except ValueError:
            logging.debug("can not convert df_Stops")
        except AttributeError:
            logging.debug("can not convert df_Stops Attribute")
        self.missing_columns_in_df(df_stops, DfStopColumnEnum)
        logging.debug("convert to df: create_df_stops finished")
        return df_stops

    def create_df_week(self, raw_data):
        logging.debug("convert to df: create_df_week")
        df_week = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Calendarweeks])
        df_week = self.drop_columns_by_enum(df_week, DfCalendarweekColumnEnum)
        df_week.name = GtfsDfNames.Calendarweeks
        try:
            df_week['start_date'] = df_week['start_date'].astype('string')
            df_week['end_date'] = df_week['end_date'].astype('string')
        except KeyError:
            logging.debug("can not convert df_week")

        self.missing_columns_in_df(df_week, DfCalendarweekColumnEnum)
        logging.debug("convert to df: df_week finished")

        return df_week

    def create_df_dates(self, raw_data):
        logging.debug("convert to df: create_df_dates")
        df_dates = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Calendardates])
        df_dates.name = GtfsDfNames.Calendardates
        try:
            df_dates['exception_type'] = df_dates['exception_type'].astype('int32')
            df_dates['date_day_format'] = pd.to_datetime(df_dates['date'])
            df_dates['day'] = df_dates['date_day_format'].dt.day_name()
            df_dates['date'] = pd.to_datetime(df_dates['date'], format='%Y%m%d')
        except KeyError:
            logging.debug("can not convert df_dateS")
        logging.debug("convert to df: create_df_dates finished")
        df_dates = self.drop_columns_by_enum(df_dates, DfCalendardateColumnEnum)
        self.missing_columns_in_df(df_dates, DfCalendardateColumnEnum)
        return df_dates

    def create_df_agency(self, raw_data):
        logging.debug("convert to df: create_df_agency")
        df_agencies = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Agencies])
        df_agencies = self.drop_columns_by_enum(df_agencies, DfAgencyColumnEnum)
        df_agencies = df_agencies.sort_values(DfAgencyColumnEnum.agency_name.value)
        df_agencies.name = GtfsDfNames.Agencies
        self.missing_columns_in_df(df_agencies, DfAgencyColumnEnum)

        return df_agencies

    def create_df_feed(self, raw_data):
        logging.debug("convert to df: create_df_feed")
        if raw_data["feed_info"]:
            df_feedinfo = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Feedinfos])
            df_feedinfo.name = GtfsDfNames.Feedinfos
            self.drop_columns_by_enum(df_feedinfo, DfFeedinfoColumnEnum)
            self.missing_columns_in_df(df_feedinfo, DfFeedinfoColumnEnum)
            return df_feedinfo
        return None

    def drop_columns_by_enum(self, df, enum_class):
        columns_to_keep = [col.value for col in enum_class]
        columns_to_drop = [col for col in df.columns if col not in columns_to_keep]

        if len(columns_to_drop) > 0:
            return df.drop(columns=columns_to_drop)
        return df

    def missing_columns_in_df(self, df, enum_class):
        missing_columns = [col for col in enum_class if col not in df.columns]
        # Add each missing column to the tracking DataFrame
        for column in missing_columns:
            self.missing_columns_in_gtfs_file.loc[len(self.missing_columns_in_gtfs_file)] = [
                df.name,
                column
            ]


    # region end

    def read_gtfs_data_from_path(self):
        ...

    def reset_data_cause_of_error(self):
        self.progress = 0
        """Todo: add the other values here """

    def save_pickle(self, imported_df_data, import_settings_dto : ImportSettingsDto):
        imported_df_data[GtfsDfNames.Stops].to_pickle(import_settings_dto.pickle_save_path + "dfStops.pkl")
        imported_df_data[GtfsDfNames.Stoptimes].to_pickle(import_settings_dto.pickle_save_path + "dfStopTimes.pkl")
        imported_df_data[GtfsDfNames.Trips].to_pickle(import_settings_dto.pickle_save_path + "dfTrips.pkl")
        imported_df_data[GtfsDfNames.Calendarweeks].to_pickle(import_settings_dto.pickle_save_path + "dfWeek.pkl")
        imported_df_data[GtfsDfNames.Calendardates].to_pickle(import_settings_dto.pickle_save_path + "dfDates.pkl")
        imported_df_data[GtfsDfNames.Routes].to_pickle(import_settings_dto.pickle_save_path + "dfRoutes.pkl")
        imported_df_data[GtfsDfNames.Agencies].to_pickle(import_settings_dto.pickle_save_path + "dfagency.pkl")

        if GtfsDfNames.Feedinfos in imported_df_data:
            imported_df_data[GtfsDfNames.Stops].to_pickle(import_settings_dto.pickle_save_path + "dffeed_info.pkl")

        with zipfile.ZipFile(import_settings_dto.pickle_save_path_filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(import_settings_dto.pickle_save_path + "dfStops.pkl")
            zf.write(import_settings_dto.pickle_save_path + "dfStopTimes.pkl")
            zf.write(import_settings_dto.pickle_save_path + "dfTrips.pkl")
            zf.write(import_settings_dto.pickle_save_path + "dfWeek.pkl")
            zf.write(import_settings_dto.pickle_save_path + "dfDates.pkl")
            zf.write(import_settings_dto.pickle_save_path + "dfRoutes.pkl")
            zf.write(import_settings_dto.pickle_save_path + "dfagency.pkl")

        os.remove(import_settings_dto.pickle_save_path + "dfStops.pkl")
        os.remove(import_settings_dto.pickle_save_path + "dfStopTimes.pkl")
        os.remove(import_settings_dto.pickle_save_path + "dfTrips.pkl")
        os.remove(import_settings_dto.pickle_save_path + "dfWeek.pkl")
        os.remove(import_settings_dto.pickle_save_path + "dfDates.pkl")
        os.remove(import_settings_dto.pickle_save_path + "dfRoutes.pkl")
        os.remove(import_settings_dto.pickle_save_path + "dfagency.pkl")

        if GtfsDfNames.Feedinfos in imported_df_data:
            os.remove(import_settings_dto.pickle_save_path + "dffeed_info.pkl")
