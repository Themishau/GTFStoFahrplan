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


async def create_fahrplan_dates(routeName,
                                agencyName,
                                dates,
                                stopsdict,
                                stopTimesdict,
                                tripdict,
                                calendarWeekdict,
                                calendarDatesdict,
                                routesFahrtdict,
                                agencyFahrtdict,
                                output_path):
    print("get_fahrt_ofroute_fahrplan start")
    print(routeName)
    print(agencyName)
    print(dates)
    last_time = time.time()

    if not check_dates_input(dates):
        return

    # DataFrame for header information
    header_for_export_data = {'Agency': [agencyName],
                              'Route': [routeName],
                              'Dates': [dates],
                              'Start': [''],
                              'Stop': ['']
                              }
    dfheader_for_export_data = pd.DataFrame.from_dict(header_for_export_data)

    # DataFrame for every route
    dfRoutes = pd.DataFrame.from_dict(routesFahrtdict).set_index('route_id')

    # DataFrame with every trip
    dfTrips = pd.DataFrame.from_dict(tripdict)

    try:
        # dfTrips['trip_id'] = pd.to_numeric(dfTrips['trip_id'])
        dfTrips['trip_id'] = dfTrips['trip_id'].astype(int)
    except:
        print("can not convert dfTrips: trip_id into int")

    # DataFrame with every stop (time)
    dfStopTimes = pd.DataFrame.from_dict(stopTimesdict)
    try:
        dfStopTimes['arrival_time'] = dfStopTimes['arrival_time'].apply(lambda x: time_in_string(x))
        dfStopTimes['arrival_time'] = dfStopTimes['arrival_time'].apply(str)
    except:
        print("can not convert dfStopTimes: arrival_time into string and change time")

    try:
        dfStopTimes['stop_sequence'] = dfStopTimes['stop_sequence'].astype(int)
    except:
        print("can not convert dfStopTimes: stop_sequence into int")
    try:
        dfStopTimes['stop_id'] = dfStopTimes['stop_id'].astype(int)
    except:
        print("can not convert dfStopTimes: stop_id into int")
    try:
        dfStopTimes['trip_id'] = dfStopTimes['trip_id'].astype(int)

    except:
        print("can not convert dfStopTimes: trip_id into int")

    # DataFrame with every stop
    dfStops = pd.DataFrame.from_dict(stopsdict).set_index('stop_id')
    try:
        dfStops['stop_id'] = dfStops['stop_id'].astype(int)
    except:
        print("can not convert dfStops: stop_id into int ")

    # try to set some more indeces
    try:
        dfTrips = dfTrips.set_index('trip_id')
        dfStopTimes = dfStopTimes.set_index(['trip_id', 'stop_id'])
        dfStops = dfStops.set_index('stop_id')
    except:
        print("can not set index: stop_id into int ")

    # DataFrame with every service weekly
    dfWeek = pd.DataFrame.from_dict(calendarWeekdict).set_index('service_id')

    # DataFrame with every service dates
    dfDates = pd.DataFrame.from_dict(calendarDatesdict).set_index('service_id')

    # DataFrame with every agency
    df_agency = pd.DataFrame.from_dict(agencyFahrtdict).set_index('agency_id')

    weekDay = [{'Monday': 'Monday'},
               {'Tuesday': 'Tuesday'},
               {'Wednesday': 'Wednesday'},
               {'Thursday': 'Thursday'},
               {'Friday': 'Friday'},
               {'Saturday': 'Saturday'},
               {'Sunday': 'Sunday'}]
    weekDaydf = pd.DataFrame(weekDay)

    dummy_direction = 0
    direction = [{'direction_id': dummy_direction}
                 ]
    dfdirection = pd.DataFrame(direction)

    requested_dates = {'date': [dates]}
    requested_datesdf = pd.DataFrame.from_dict(requested_dates).set_index('date')
    print(requested_datesdf)

    # dataframe with the (bus) lines
    inputVar = [{'route_short_name': routeName}]
    requested_route_short_namedf = pd.DataFrame(inputVar).set_index('route_short_name')

    inputVarAgency = [{'agency_id': agencyName}]
    requested_agencydf = pd.DataFrame(inputVarAgency).set_index('agency_id')


    # conditions for searching in dfs

    cond_Fahrplan_calendar_dates = '''
                select  dfDates.date,
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
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join dfDates on dfDates.service_id = dfTrips.service_id
                left join requested_route_short_namedf
                left join requested_agencydf
                inner join requested_datesdf
                where dfRoutes.route_short_name = requested_route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = requested_agencydf.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
                  and dfDates.date = requested_datesdf.date
                order by dfStopTimes.stop_sequence, dfStopTimes.arrival_time;
               '''

    fahrplan_calendar_dates = sqldf(cond_Fahrplan_calendar_dates, locals())

    # creating a pivot table
    fahrplan_calendar_dates_pivot = fahrplan_calendar_dates.pivot(index  =['date', 'stop_sequence', 'stop_name'],
                                                                  columns=['start_time', 'trip_id'],
                                                                  values ='arrival_time')
    fahrplan_calendar_dates_pivot = fahrplan_calendar_dates_pivot.sort_index(axis=0)

    # releae some memory
    dfTrips = None
    dfStopTimes = None
    dfStops = None
    dfRoutes = None
    dfWeek = None

    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
    return zeit, dfheader_for_export_data, fahrplan_calendar_dates_pivot


    cond_select_dates_delete_exception_2ohneleft join  = '''
                select  
                        fahrplan_dates_all_dates.date,
                        fahrplan_dates_all_dates.day,
                        fahrplan_dates_all_dates.trip_id,
                        fahrplan_dates_all_dates.service_id,
                        fahrplan_dates_all_dates.route_id, 
                        fahrplan_dates_all_dates.start_date,
                        fahrplan_dates_all_dates.end_date,
                        fahrplan_dates_all_dates.monday,
                        fahrplan_dates_all_dates.tuesday,
                        fahrplan_dates_all_dates.wednesday,
                        fahrplan_dates_all_dates.thursday,
                        fahrplan_dates_all_dates.friday,
                        fahrplan_dates_all_dates.saturday,
                        fahrplan_dates_all_dates.sunday
                from fahrplan_dates_all_dates 
                where fahrplan_dates_all_dates.date not in (select dfDates.date 
                                                              from dfDates                                                            
                                                                where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                  and dfDates.exception_type = 2
                                                            )
                 and (fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                     )
                 and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_dates_all_dates.day = weekcond_df.day
                                                     )  
                order by fahrplan_dates_all_dates.service_id;
               '''