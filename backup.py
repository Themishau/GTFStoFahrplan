weekDayOption_1 = {'Monday': [1],
                   'Tuesday': [1],
                   'Wednesday': [1],
                   'Thursday': [1],
                   'Friday': [1],
                   'Saturday': [1],
                   'Sunday': [1]
                   }

weekDayOption_2 = {'Monday': [1],
                   'Tuesday': [1],
                   'Wednesday': [1],
                   'Thursday': [1],
                   'Friday': [1],
                   'Saturday': [0],
                   'Sunday': [0]
                   }

weekDayOption_monday = {'Monday': [1],
                        'Tuesday': [0],
                        'Wednesday': [0],
                        'Thursday': [0],
                        'Friday': [0],
                        'Saturday': [0],
                        'Sunday': [0]
                        }

weekDayOption_tuesday = {'Monday': [0],
                         'Tuesday': [1],
                         'Wednesday': [0],
                         'Thursday': [0],
                         'Friday': [0],
                         'Saturday': [0],
                         'Sunday': [0]
                         }

weekDayOption_wednesday = {'Monday': [0],
                           'Tuesday': [0],
                           'Wednesday': [1],
                           'Thursday': [0],
                           'Friday': [0],
                           'Saturday': [0],
                           'Sunday': [0]
                           }

weekDayOption_thursday = {'Monday': [0],
                          'Tuesday': [0],
                          'Wednesday': [0],
                          'Thursday': [1],
                          'Friday': [0],
                          'Saturday': [0],
                          'Sunday': [0]
                          }

weekDayOption_friday = {'Monday': [0],
                        'Tuesday': [0],
                        'Wednesday': [0],
                        'Thursday': [0],
                        'Friday': [1],
                        'Saturday': [0],
                        'Sunday': [0]
                        }

weekDayOption_saturday = {'Monday': [0],
                          'Tuesday': [0],
                          'Wednesday': [0],
                          'Thursday': [0],
                          'Friday': [0],
                          'Saturday': [1],
                          'Sunday': [0]
                          }

weekDayOption_sunday = {'Monday': [0],
                        'Tuesday': [0],
                        'Wednesday': [0],
                        'Thursday': [0],
                        'Friday': [0],
                        'Saturday': [0],
                        'Sunday': [1]
                        }

csiti = 23454
units = [11,22,33,44,55,66,77]
begin_date = '2019-10-16'

df = pd.DataFrame({'csiti':csiti,
                   'units':units,
                   'forecast_date':pd.date_range(begin_date, periods=len(units))})

fahrplan_dates_all_dates = pd.concat([pd.DataFrame([{'date': pd.date_range(row.start_date, row.end_date, freq='D'),
                                                     'trip_id': row.trip_id,
                                                     'service_id': row.service_id,
                                                     'start_date': row.start_date,
                                                     'end_date': row.end_date,
                                                     'monday': row.monday,
                                                     'tuesday': row.tuesday,
                                                     'wednesday': row.wednesday,
                                                     'thursday': row.thursday,
                                                     'friday': row.friday,
                                                     'saturday': row.saturday,
                                                     'sunday': row.sunday}],
                                                   columns=['date', 'trip_id', 'service_id', 'start_date', 'end_date',
                                                            'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                                                            'saturday', 'sunday'])
                                      for row in fahrplan_dates.iterrows()], ignore_index=True)

print(fahrplan_dates['trip_id'])
fahrplan_dates_all_dates = pd.Dataframe({
    'trip_id': [fahrplan_dates['trip_id']],
    'service_id': [fahrplan_dates['service_id']],
    'start_date': [fahrplan_dates['start_date']],
    'end_date': [fahrplan_dates['end_date']],
    'monday': [fahrplan_dates['monday']],
    'tuesday': [fahrplan_dates['tuesday']],
    'wednesday': [fahrplan_dates['wednesday']],
    'thursday': [fahrplan_dates['thursday']],
    'friday': [fahrplan_dates['friday']],
    'saturday  ': [fahrplan_dates['saturday']],
    'sunday': [fahrplan_dates['sunday']]
    # 'date'      : pd.date_range(start=fahrplan_dates['start_date'], end=fahrplan_dates['end_date'], freq='D').strftime('%Y%m%d')
})

cond_Fahrplan_calendar_weekdays = '''
            select  fahrplan_dates_all_dates.date,
                    dfDates.date as exception_date,
                    dfDates.exception_type,
                    (select st_dfStopTimes.arrival_time 
                            from dfStopTimes st_dfStopTimes
                            where st_dfStopTimes.stop_sequence = 0
                              and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time, 
                    fahrplan_dates_all_dates.trip_id,
                    dfStops.stop_name,
                    dfStopTimes.stop_sequence, 
                    dfStopTimes.arrival_time, 
                    fahrplan_dates_all_dates.service_id, 
                    dfStops.stop_id                        
            from dfStopTimes 
            left join fahrplan_dates_all_dates on dfStopTimes.trip_id = fahrplan_dates_all_dates.trip_id
            left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
            left join dfDates on dfDates.service_id = fahrplan_dates_all_dates.service_id
            left join varTestAgency 
            order by dfStopTimes.stop_sequence, dfStopTimes.arrival_time;
           '''

cond_Fahrplan_calendar_weekdays = '''
            select  
                    dfDates.date as exception_date,
                    dfDates.exception_type,
                    (select st_dfStopTimes.arrival_time 
                            from dfStopTimes st_dfStopTimes
                            where st_dfStopTimes.stop_sequence = 0
                              and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time, 
                    dfTrips.trip_id,
                    dfStops.stop_name,
                    dfStopTimes.stop_sequence, 
                    dfStopTimes.arrival_time, 
                    dfTrips.service_id, 
                    dfStops.stop_id                        
            from dfStopTimes 
            left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
            left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
            left join dfDates on dfDates.service_id = dfTrips.service_id
            left join varTestAgency 
            left join route_short_namedf
            where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
              and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
            order by dfStopTimes.stop_sequence, dfStopTimes.arrival_time;
           '''

cond_Fahrplan_calendar_weekdays = '''
            select  fahrplan_dates_all_dates.date,
                    dfDates.date as exception_date,
                    dfDates.exception_type,
                    (select st_dfStopTimes.arrival_time 
                            from dfStopTimes st_dfStopTimes
                            where st_dfStopTimes.stop_sequence = 0
                              and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time, 
                    fahrplan_dates_all_dates.trip_id,
                    dfStops.stop_name,
                    dfStopTimes.stop_sequence, 
                    dfStopTimes.arrival_time, 
                    fahrplan_dates_all_dates.service_id, 
                    dfStops.stop_id                        
            from dfStopTimes 
            left join fahrplan_dates_all_dates on dfStopTimes.trip_id = fahrplan_dates_all_dates.trip_id
            left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
            left join dfDates on dfDates.service_id = fahrplan_dates_all_dates.service_id
            left join dfRoutes on dfRoutes.route_id  = fahrplan_dates_all_dates.route_id
            left join varTestAgency
            left join route_short_namedf
            where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
              and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number 
            order by dfStopTimes.stop_sequence, dfStopTimes.arrival_time;
           '''

cond_Fahrplan_calendar_weekdays = '''
            select  
                    dfDates.date as exception_date,
                    dfDates.exception_type,
                    (select st_dfStopTimes.arrival_time 
                            from dfStopTimes st_dfStopTimes
                            where st_dfStopTimes.stop_sequence = 0
                              and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time, 
                    dfTrips.trip_id,
                    dfStops.stop_name,
                    dfStopTimes.stop_sequence, 
                    dfStopTimes.arrival_time, 
                    dfTrips.service_id, 
                    dfStops.stop_id                        
            from dfStopTimes 
            left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
            left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
            left join dfDates on dfDates.service_id = dfTrips.service_id
            left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
            left join varTestAgency 
            left join route_short_namedf
            where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
              and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
            order by dfStopTimes.stop_sequence, dfStopTimes.arrival_time;
           '''