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

    cond_select_dates_for_date_range = '''
                select  
                        dfTrips.trip_id,
                        dfTrips.service_id,
                        dfTrips.route_id, 
                        dfWeek.start_date,
                        dfWeek.end_date,
                        dfWeek.monday,
                        dfWeek.tuesday,
                        dfWeek.wednesday,
                        dfWeek.thursday,
                        dfWeek.friday,
                        dfWeek.saturday,
                        dfWeek.sunday
                from dfWeek 
                left join dfTrips on dfWeek.service_id = dfTrips.service_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join route_short_namedf
                left join varTestAgency
                where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
                order by dfTrips.service_id;
               '''


    cond_select_dates_delete_exception_2 = '''
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
                                                                  and fahrplan_dates_all_dates.date = dfDates.date
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

    cond_select_dates_delete_exception_2 = '''
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
                                                                  and fahrplan_dates_all_dates.date = dfDates.date
                                                                  and dfDates.exception_type = 2
                                                            )
                  and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                         from weekcond_df                                                            
                                                        where fahrplan_dates_all_dates.day = weekcond_df.day
                                                      )                   
                order by fahrplan_dates_all_dates.service_id;
               '''

    cond_select_dates_delete_exception_2 = '''
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
                                                                  and fahrplan_dates_all_dates.date = dfDates.date
                                                                  and dfDates.exception_type = 2
                                                            )                
                and ( (  fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                      ) 
                      or 
                      (   fahrplan_dates_all_dates.monday    = '-'
                      and fahrplan_dates_all_dates.tuesday   = '-'
                      and fahrplan_dates_all_dates.wednesday = '-'
                      and fahrplan_dates_all_dates.thursday  = '-'
                      and fahrplan_dates_all_dates.friday    = '-'
                      and fahrplan_dates_all_dates.saturday  = '-'
                      and fahrplan_dates_all_dates.sunday    = '-'
                      )
                    )
                 and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_dates_all_dates.day = weekcond_df.day
                                                     )  
                order by fahrplan_dates_all_dates.service_id;
               '''


    cond_filter_days_not_requested = '''
                select  fahrplan_calendar_weeks.day,
                        fahrplan_calendar_weeks.date,
                        fahrplan_calendar_weeks.start_time, 
                        fahrplan_calendar_weeks.trip_id,
                        fahrplan_calendar_weeks.stop_name,
                        fahrplan_calendar_weeks.stop_sequence, 
                        fahrplan_calendar_weeks.arrival_time, 
                        fahrplan_calendar_weeks.service_id, 
                        fahrplan_calendar_weeks.stop_id         
                from fahrplan_calendar_weeks
                where fahrplan_calendar_weeks.day  in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_calendar_weeks.day = weekcond_df.day
                                                     );
               '''


    # fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_1, locals())
    # fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates.to_csv( 'C:/Temp/fahrplan_dates_all_datesDelete1.csv', header=True, quotechar=' ',
    #                       index=True, sep=';', mode='w', encoding='utf8')
    # fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
    # fahrplan_dates_all_datesTEST.to_csv( 'C:/Temp/fahrplan_dates_all_datesTESTDELETEEXCEPTION_1.csv', header=True, quotechar=' ',
    #                       index=True, sep=';', mode='w', encoding='utf8')

    async def create_fahrplan_weekday(routeName,
                                      agencyName,
                                      selected_weekdayOption,
                                      stopsdict,
                                      stopTimesdict,
                                      tripdict,
                                      calendarWeekdict,
                                      calendarDatesdict,
                                      routesFahrtdict,
                                      agencyFahrtdict,
                                      output_path):
        print(routeName)
        print(agencyName)
        print(selected_weekdayOption)
        last_time = time.time()

        header_for_export_data = {'Agency': [agencyName],
                                  'Route': [routeName],
                                  'WeekdayOption': [selected_weekdayOption]
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
        dfDates['exception_type'] = dfDates['exception_type'].astype(int)
        dfDates['date'] = pd.to_datetime(dfDates['date'], format='%Y%m%d')
        # DataFrame with every agency
        df_agency = pd.DataFrame.from_dict(agencyFahrtdict).set_index('agency_id')

        weekDayOption_1 = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        weekDayOption_2 = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        weekDayOption_monday = {'day': ['Monday']}
        weekDayOption_tuesday = {'day': ['Tuesday']}
        weekDayOption_wednesday = {'day': ['Wednesday']}
        weekDayOption_thursday = {'day': ['Thursday']}
        weekDayOption_friday = {'day': ['Friday']}
        weekDayOption_saturday = {'day': ['Saturday']}
        weekDayOption_sunday = {'day': ['Sunday']}

        weekDay_1_df = pd.DataFrame.from_dict(weekDayOption_1).set_index('day')
        weekDay_2_df = pd.DataFrame.from_dict(weekDayOption_2).set_index('day')
        weekDayOption_monday_df = pd.DataFrame.from_dict(weekDayOption_monday).set_index('day')
        weekDayOption_tuesday_df = pd.DataFrame.from_dict(weekDayOption_tuesday).set_index('day')
        weekDayOption_wednesday_df = pd.DataFrame.from_dict(weekDayOption_wednesday).set_index('day')
        weekDayOption_thursday_df = pd.DataFrame.from_dict(weekDayOption_thursday).set_index('day')
        weekDayOption_friday_df = pd.DataFrame.from_dict(weekDayOption_friday).set_index('day')
        weekDayOption_saturday_df = pd.DataFrame.from_dict(weekDayOption_saturday).set_index('day')
        weekDayOption_sunday_df = pd.DataFrame.from_dict(weekDayOption_sunday).set_index('day')

        weekDayOptionList = [weekDay_1_df,
                             weekDay_2_df,
                             weekDayOption_monday_df,
                             weekDayOption_tuesday_df,
                             weekDayOption_wednesday_df,
                             weekDayOption_thursday_df,
                             weekDayOption_friday_df,
                             weekDayOption_saturday_df,
                             weekDayOption_sunday_df]

        weekcond_df = weekDayOptionList[selected_weekdayOption]
        dummy_direction = 0
        direction = [{'direction_id': dummy_direction}
                     ]
        dfdirection = pd.DataFrame(direction)

        # dataframe with the (bus) lines
        inputVar = [{'route_short_name': routeName}]
        route_short_namedf = pd.DataFrame(inputVar).set_index('route_short_name')

        inputVarAgency = [{'agency_id': agencyName}]
        varTestAgency = pd.DataFrame(inputVarAgency).set_index('agency_id')

        inputVarService = [{'weekdayOption': selected_weekdayOption}]
        varTestService = pd.DataFrame(inputVarService).set_index('weekdayOption')

        # conditions for searching in dfs
        cond_select_dates_for_date_range = '''
                    select  
                            dfTrips.trip_id,
                            dfTrips.service_id,
                            dfTrips.route_id, 
                            dfWeek.start_date,
                            dfWeek.end_date,
                            dfWeek.monday,
                            dfWeek.tuesday,
                            dfWeek.wednesday,
                            dfWeek.thursday,
                            dfWeek.friday,
                            dfWeek.saturday,
                            dfWeek.sunday
                    from dfWeek 
                    inner join dfTrips on dfWeek.service_id = dfTrips.service_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = 0 -- shows the direction of the line 
                    order by dfTrips.service_id;
                   '''

        cond_select_dates_delete_exception_1 = '''
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
                    where 
                         (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
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

        cond_select_dates_delete_exception_2 = '''
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
                          -- not has exception_type = 2
                    where fahrplan_dates_all_dates.date not in (select dfDates.date
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 2
                                                                )
                      -- and is marked as the day of the week or is has exception_type = 1                          
                      and (  (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                             )
                             or 
                             (   fahrplan_dates_all_dates.date in (select dfDates.date
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 1
                                                                 )    
                             )
                          )
                      -- and the day is requested   
                      and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                                  from weekcond_df                                                            
                                                                    where fahrplan_dates_all_dates.day = weekcond_df.day
                                                         )  
                    order by fahrplan_dates_all_dates.date;
                   '''
        cond_select_dates_delete_TEST = '''
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
                            fahrplan_dates_all_dates.sunday,
                            dfDates.exception_type
                    from fahrplan_dates_all_dates 
                    left join dfDates on dfDates.date = fahrplan_dates_all_dates.date
                    where dfDates.service_id = fahrplan_dates_all_dates.service_id
                    order by fahrplan_dates_all_dates.date;
                   '''

        cond_select_dates_delete_TESTWEEK = '''
                    select  
                            fahrplan_calendar_weeks.date,
                            fahrplan_calendar_weeks.day,
                            fahrplan_calendar_weeks.trip_id,
                            fahrplan_calendar_weeks.service_id,
                            fahrplan_calendar_weeks.stop_name,
                            fahrplan_calendar_weeks.stop_id,
                            dfDates.exception_type
                    from fahrplan_calendar_weeks 
                    left join dfDates on dfDates.date = fahrplan_calendar_weeks.date
                    where dfDates.service_id = fahrplan_calendar_weeks.service_id                
                    order by fahrplan_calendar_weeks.date;
                   '''

        cond_select_stops_for_trips = '''
                    select  
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
                    inner join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                    inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = 0 -- shows the direction of the line 
                    order by dfStopTimes.stop_sequence, start_time;
                   '''

        cond_select_for_every_date_trips_stops = '''
                    select  fahrplan_dates_all_dates.date,
                            fahrplan_dates_all_dates.day,
                            fahrplan_calendar_weeks.start_time, 
                            fahrplan_dates_all_dates.trip_id,
                            fahrplan_calendar_weeks.stop_name,
                            fahrplan_calendar_weeks.stop_sequence, 
                            fahrplan_calendar_weeks.arrival_time, 
                            fahrplan_dates_all_dates.service_id, 
                            fahrplan_calendar_weeks.stop_id                        
                    from fahrplan_dates_all_dates 
                    inner join fahrplan_calendar_weeks on fahrplan_calendar_weeks.trip_id = fahrplan_dates_all_dates.trip_id                         
                    order by fahrplan_dates_all_dates.date, fahrplan_calendar_weeks.stop_sequence, fahrplan_calendar_weeks.start_time;
                   '''

        # get dates for start and end dates for date range function
        fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
        # add date column for every date in date range
        fahrplan_dates_all_dates = pd.concat(
            [pd.DataFrame({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
                           'trip_id': row.trip_id,
                           'service_id': row.service_id,
                           'route_id': row.route_id,
                           'start_date': row.start_date,
                           'end_date': row.end_date,
                           'monday': row.monday,
                           'tuesday': row.tuesday,
                           'wednesday': row.wednesday,
                           'thursday': row.thursday,
                           'friday': row.friday,
                           'saturday': row.saturday,
                           'sunday': row.sunday
                           }
                          )
             for i, row in fahrplan_dates.iterrows()], ignore_index=True)
        # I need to convert the date after every sqldf for some reason
        fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()
        # set value in column to day if 1 and and compare with day
        fahrplan_dates_all_dates['monday'] = fahrplan_dates_all_dates['monday'].apply(
            lambda x: 'Monday' if x == '1' else '-')
        fahrplan_dates_all_dates['tuesday'] = fahrplan_dates_all_dates['tuesday'].apply(
            lambda x: 'Tuesday' if x == '1' else '-')
        fahrplan_dates_all_dates['wednesday'] = fahrplan_dates_all_dates['wednesday'].apply(
            lambda x: 'Wednesday' if x == '1' else '-')
        fahrplan_dates_all_dates['thursday'] = fahrplan_dates_all_dates['thursday'].apply(
            lambda x: 'Thursday' if x == '1' else '-')
        fahrplan_dates_all_dates['friday'] = fahrplan_dates_all_dates['friday'].apply(
            lambda x: 'Friday' if x == '1' else '-')
        fahrplan_dates_all_dates['saturday'] = fahrplan_dates_all_dates['saturday'].apply(
            lambda x: 'Saturday' if x == '1' else '-')
        fahrplan_dates_all_dates['sunday'] = fahrplan_dates_all_dates['sunday'].apply(
            lambda x: 'Sunday' if x == '1' else '-')

        fahrplan_dates_all_dates.to_csv('C:/Temp/fahrplan_dates_all_dates_alleTage.csv', header=True, quotechar=' ',
                                        index=True, sep=';', mode='w', encoding='utf8')

        fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
        fahrplan_dates_all_datesTEST.to_csv('C:/Temp/fahrplan_dates_all_datesTESTNODELETEEXCEPTION.csv', header=True,
                                            quotechar=' ',
                                            index=True, sep=';', mode='w', encoding='utf8')

        # fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_1, locals())
        # fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates.to_csv( 'C:/Temp/fahrplan_dates_all_datesDelete1.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='w', encoding='utf8')
        # fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
        # fahrplan_dates_all_datesTEST.to_csv( 'C:/Temp/fahrplan_dates_all_datesTESTDELETEEXCEPTION_1.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='w', encoding='utf8')

        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('trip_id')
        fahrplan_dates_all_dates.to_csv('C:/Temp/fahrplan_dates_all_datesDelete2.csv', header=True, quotechar=' ',
                                        index=True, sep=';', mode='w', encoding='utf8')
        fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
        fahrplan_dates_all_datesTEST.to_csv('C:/Temp/fahrplan_dates_all_datesTESTDELETEEXCEPTION_2.csv', header=True,
                                            quotechar=' ',
                                            index=True, sep=';', mode='w', encoding='utf8')

        # get all stop_times and stops for every stop of one route
        fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())
        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.set_index('trip_id')

        fahrplan_calendar_weeks.to_csv('C:/Temp/fahrplan_calendar_weeksWEEKS.csv', header=True, quotechar=' ',
                                       index=True, sep=';', mode='w', encoding='utf8')

        # combine dates and trips to get a df with trips for every date
        fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())
        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype(int)
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(str)
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].apply(str)

        fahrplan_calendar_weeks.to_csv('C:/Temp/fahrplan_calendar_weeksCOMBINE.csv', header=True, quotechar=' ',
                                       index=True, sep=';', mode='w', encoding='utf8')
        fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TESTWEEK, locals())
        fahrplan_dates_all_datesTEST.to_csv('C:/Temp/fahrplan_dates_all_datesTESTEXCEPTIONCOMBINE.csv', header=True,
                                            quotechar=' ',
                                            index=True, sep=';', mode='w', encoding='utf8')

        # filter days
        # fahrplan_calendar_filter_days  = sqldf(cond_filter_days_not_requested, locals())
        # fahrplan_calendar_filter_days['date'] = pd.to_datetime(fahrplan_calendar_filter_days['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_calendar_filter_days['trip_id'] = fahrplan_calendar_filter_days['trip_id'].astype(int)
        # fahrplan_calendar_filter_days['arrival_time'] = fahrplan_calendar_filter_days['arrival_time'].apply(str)

        # creating a pivot table
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence', 'stop_name'], columns=['start_time', 'trip_id'],
            values='arrival_time')
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        # releae some memory
        dfTrips = None
        dfStopTimes = None
        dfStops = None
        dfRoutes = None
        dfWeek = None
        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
        return zeit, dfheader_for_export_data, fahrplan_calendar_filter_days_pivot

    cond_select_dates_for_date_range = '''
                select  
                        dfTrips.trip_id,
                        dfTrips.service_id,
                        dfTrips.route_id, 
                        dfWeek.start_date,
                        dfWeek.end_date,
                        dfWeek.monday,
                        dfWeek.tuesday,
                        dfWeek.wednesday,
                        dfWeek.thursday,
                        dfWeek.friday,
                        dfWeek.saturday,
                        dfWeek.sunday
                from dfWeek 
                left join dfTrips on dfWeek.service_id = dfTrips.service_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join route_short_namedf
                left join varTestAgency
                where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
                order by dfTrips.service_id;
               '''


    cond_select_dates_delete_exception_2 = '''
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
                                                                  and fahrplan_dates_all_dates.date = dfDates.date
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

    cond_select_dates_delete_exception_2 = '''
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
                                                                  and fahrplan_dates_all_dates.date = dfDates.date
                                                                  and dfDates.exception_type = 2
                                                            )
                  and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                         from weekcond_df                                                            
                                                        where fahrplan_dates_all_dates.day = weekcond_df.day
                                                      )                   
                order by fahrplan_dates_all_dates.service_id;
               '''

    cond_select_dates_delete_exception_2 = '''
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
                                                                  and fahrplan_dates_all_dates.date = dfDates.date
                                                                  and dfDates.exception_type = 2
                                                            )                
                and ( (  fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                      ) 
                      or 
                      (   fahrplan_dates_all_dates.monday    = '-'
                      and fahrplan_dates_all_dates.tuesday   = '-'
                      and fahrplan_dates_all_dates.wednesday = '-'
                      and fahrplan_dates_all_dates.thursday  = '-'
                      and fahrplan_dates_all_dates.friday    = '-'
                      and fahrplan_dates_all_dates.saturday  = '-'
                      and fahrplan_dates_all_dates.sunday    = '-'
                      )
                    )
                 and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_dates_all_dates.day = weekcond_df.day
                                                     )  
                order by fahrplan_dates_all_dates.service_id;
               '''


    cond_filter_days_not_requested = '''
                select  fahrplan_calendar_weeks.day,
                        fahrplan_calendar_weeks.date,
                        fahrplan_calendar_weeks.start_time, 
                        fahrplan_calendar_weeks.trip_id,
                        fahrplan_calendar_weeks.stop_name,
                        fahrplan_calendar_weeks.stop_sequence, 
                        fahrplan_calendar_weeks.arrival_time, 
                        fahrplan_calendar_weeks.service_id, 
                        fahrplan_calendar_weeks.stop_id         
                from fahrplan_calendar_weeks
                where fahrplan_calendar_weeks.day  in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_calendar_weeks.day = weekcond_df.day
                                                     );
               '''


    # fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_1, locals())
    # fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates.to_csv( 'C:/Temp/fahrplan_dates_all_datesDelete1.csv', header=True, quotechar=' ',
    #                       index=True, sep=';', mode='w', encoding='utf8')
    # fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
    # fahrplan_dates_all_datesTEST.to_csv( 'C:/Temp/fahrplan_dates_all_datesTESTDELETEEXCEPTION_1.csv', header=True, quotechar=' ',
    #                       index=True, sep=';', mode='w', encoding='utf8')

    async def create_fahrplan_weekday(routeName,
                                      agencyName,
                                      selected_weekdayOption,
                                      stopsdict,
                                      stopTimesdict,
                                      tripdict,
                                      calendarWeekdict,
                                      calendarDatesdict,
                                      routesFahrtdict,
                                      agencyFahrtdict,
                                      output_path):
        print(routeName)
        print(agencyName)
        print(selected_weekdayOption)
        last_time = time.time()

        header_for_export_data = {'Agency': [agencyName],
                                  'Route': [routeName],
                                  'WeekdayOption': [selected_weekdayOption]
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
        dfDates['exception_type'] = dfDates['exception_type'].astype(int)
        dfDates['date'] = pd.to_datetime(dfDates['date'], format='%Y%m%d')
        # DataFrame with every agency
        df_agency = pd.DataFrame.from_dict(agencyFahrtdict).set_index('agency_id')

        weekDayOption_1 = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        weekDayOption_2 = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        weekDayOption_monday = {'day': ['Monday']}
        weekDayOption_tuesday = {'day': ['Tuesday']}
        weekDayOption_wednesday = {'day': ['Wednesday']}
        weekDayOption_thursday = {'day': ['Thursday']}
        weekDayOption_friday = {'day': ['Friday']}
        weekDayOption_saturday = {'day': ['Saturday']}
        weekDayOption_sunday = {'day': ['Sunday']}

        weekDay_1_df = pd.DataFrame.from_dict(weekDayOption_1).set_index('day')
        weekDay_2_df = pd.DataFrame.from_dict(weekDayOption_2).set_index('day')
        weekDayOption_monday_df = pd.DataFrame.from_dict(weekDayOption_monday).set_index('day')
        weekDayOption_tuesday_df = pd.DataFrame.from_dict(weekDayOption_tuesday).set_index('day')
        weekDayOption_wednesday_df = pd.DataFrame.from_dict(weekDayOption_wednesday).set_index('day')
        weekDayOption_thursday_df = pd.DataFrame.from_dict(weekDayOption_thursday).set_index('day')
        weekDayOption_friday_df = pd.DataFrame.from_dict(weekDayOption_friday).set_index('day')
        weekDayOption_saturday_df = pd.DataFrame.from_dict(weekDayOption_saturday).set_index('day')
        weekDayOption_sunday_df = pd.DataFrame.from_dict(weekDayOption_sunday).set_index('day')

        weekDayOptionList = [weekDay_1_df,
                             weekDay_2_df,
                             weekDayOption_monday_df,
                             weekDayOption_tuesday_df,
                             weekDayOption_wednesday_df,
                             weekDayOption_thursday_df,
                             weekDayOption_friday_df,
                             weekDayOption_saturday_df,
                             weekDayOption_sunday_df]

        weekcond_df = weekDayOptionList[selected_weekdayOption]
        dummy_direction = 0
        direction = [{'direction_id': dummy_direction}
                     ]
        dfdirection = pd.DataFrame(direction)

        # dataframe with the (bus) lines
        inputVar = [{'route_short_name': routeName}]
        route_short_namedf = pd.DataFrame(inputVar).set_index('route_short_name')

        inputVarAgency = [{'agency_id': agencyName}]
        varTestAgency = pd.DataFrame(inputVarAgency).set_index('agency_id')

        inputVarService = [{'weekdayOption': selected_weekdayOption}]
        varTestService = pd.DataFrame(inputVarService).set_index('weekdayOption')

        # conditions for searching in dfs
        cond_select_dates_for_date_range = '''
                    select  
                            dfTrips.trip_id,
                            dfTrips.service_id,
                            dfTrips.route_id, 
                            dfWeek.start_date,
                            dfWeek.end_date,
                            dfWeek.monday,
                            dfWeek.tuesday,
                            dfWeek.wednesday,
                            dfWeek.thursday,
                            dfWeek.friday,
                            dfWeek.saturday,
                            dfWeek.sunday
                    from dfWeek 
                    inner join dfTrips on dfWeek.service_id = dfTrips.service_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = 0 -- shows the direction of the line 
                    order by dfTrips.service_id;
                   '''

        cond_select_dates_delete_exception_1 = '''
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
                    where 
                         (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
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

        cond_select_dates_delete_exception_2 = '''
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
                          -- not has exception_type = 2
                    where fahrplan_dates_all_dates.date not in (select dfDates.date
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 2
                                                                )
                      -- and is marked as the day of the week or is has exception_type = 1                          
                      and (  (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                             )
                             or 
                             (   fahrplan_dates_all_dates.date in (select dfDates.date
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 1
                                                                 )    
                             )
                          )
                      -- and the day is requested   
                      and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                                  from weekcond_df                                                            
                                                                    where fahrplan_dates_all_dates.day = weekcond_df.day
                                                         )  
                    order by fahrplan_dates_all_dates.date;
                   '''
        cond_select_dates_delete_TEST = '''
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
                            fahrplan_dates_all_dates.sunday,
                            dfDates.exception_type
                    from fahrplan_dates_all_dates 
                    left join dfDates on dfDates.date = fahrplan_dates_all_dates.date
                    where dfDates.service_id = fahrplan_dates_all_dates.service_id
                    order by fahrplan_dates_all_dates.date;
                   '''

        cond_select_dates_delete_TESTWEEK = '''
                    select  
                            fahrplan_calendar_weeks.date,
                            fahrplan_calendar_weeks.day,
                            fahrplan_calendar_weeks.trip_id,
                            fahrplan_calendar_weeks.service_id,
                            fahrplan_calendar_weeks.stop_name,
                            fahrplan_calendar_weeks.stop_id,
                            dfDates.exception_type
                    from fahrplan_calendar_weeks 
                    left join dfDates on dfDates.date = fahrplan_calendar_weeks.date
                    where dfDates.service_id = fahrplan_calendar_weeks.service_id                
                    order by fahrplan_calendar_weeks.date;
                   '''

        cond_select_stops_for_trips = '''
                    select  
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
                    inner join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                    inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = 0 -- shows the direction of the line 
                    order by dfStopTimes.stop_sequence, start_time;
                   '''

        cond_select_for_every_date_trips_stops = '''
                    select  fahrplan_dates_all_dates.date,
                            fahrplan_dates_all_dates.day,
                            fahrplan_calendar_weeks.start_time, 
                            fahrplan_dates_all_dates.trip_id,
                            fahrplan_calendar_weeks.stop_name,
                            fahrplan_calendar_weeks.stop_sequence, 
                            fahrplan_calendar_weeks.arrival_time, 
                            fahrplan_dates_all_dates.service_id, 
                            fahrplan_calendar_weeks.stop_id                        
                    from fahrplan_dates_all_dates 
                    inner join fahrplan_calendar_weeks on fahrplan_calendar_weeks.trip_id = fahrplan_dates_all_dates.trip_id                         
                    order by fahrplan_dates_all_dates.date, fahrplan_calendar_weeks.stop_sequence, fahrplan_calendar_weeks.start_time;
                   '''

        # get dates for start and end dates for date range function
        fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
        # add date column for every date in date range
        fahrplan_dates_all_dates = pd.concat(
            [pd.DataFrame({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
                           'trip_id': row.trip_id,
                           'service_id': row.service_id,
                           'route_id': row.route_id,
                           'start_date': row.start_date,
                           'end_date': row.end_date,
                           'monday': row.monday,
                           'tuesday': row.tuesday,
                           'wednesday': row.wednesday,
                           'thursday': row.thursday,
                           'friday': row.friday,
                           'saturday': row.saturday,
                           'sunday': row.sunday
                           }
                          )
             for i, row in fahrplan_dates.iterrows()], ignore_index=True)
        # I need to convert the date after every sqldf for some reason
        fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()
        # set value in column to day if 1 and and compare with day
        fahrplan_dates_all_dates['monday'] = fahrplan_dates_all_dates['monday'].apply(
            lambda x: 'Monday' if x == '1' else '-')
        fahrplan_dates_all_dates['tuesday'] = fahrplan_dates_all_dates['tuesday'].apply(
            lambda x: 'Tuesday' if x == '1' else '-')
        fahrplan_dates_all_dates['wednesday'] = fahrplan_dates_all_dates['wednesday'].apply(
            lambda x: 'Wednesday' if x == '1' else '-')
        fahrplan_dates_all_dates['thursday'] = fahrplan_dates_all_dates['thursday'].apply(
            lambda x: 'Thursday' if x == '1' else '-')
        fahrplan_dates_all_dates['friday'] = fahrplan_dates_all_dates['friday'].apply(
            lambda x: 'Friday' if x == '1' else '-')
        fahrplan_dates_all_dates['saturday'] = fahrplan_dates_all_dates['saturday'].apply(
            lambda x: 'Saturday' if x == '1' else '-')
        fahrplan_dates_all_dates['sunday'] = fahrplan_dates_all_dates['sunday'].apply(
            lambda x: 'Sunday' if x == '1' else '-')

        fahrplan_dates_all_dates.to_csv('C:/Temp/fahrplan_dates_all_dates_alleTage.csv', header=True, quotechar=' ',
                                        index=True, sep=';', mode='w', encoding='utf8')

        fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
        fahrplan_dates_all_datesTEST.to_csv('C:/Temp/fahrplan_dates_all_datesTESTNODELETEEXCEPTION.csv', header=True,
                                            quotechar=' ',
                                            index=True, sep=';', mode='w', encoding='utf8')

        # fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_1, locals())
        # fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates.to_csv( 'C:/Temp/fahrplan_dates_all_datesDelete1.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='w', encoding='utf8')
        # fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
        # fahrplan_dates_all_datesTEST.to_csv( 'C:/Temp/fahrplan_dates_all_datesTESTDELETEEXCEPTION_1.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='w', encoding='utf8')

        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('trip_id')
        fahrplan_dates_all_dates.to_csv('C:/Temp/fahrplan_dates_all_datesDelete2.csv', header=True, quotechar=' ',
                                        index=True, sep=';', mode='w', encoding='utf8')
        fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TEST, locals())
        fahrplan_dates_all_datesTEST.to_csv('C:/Temp/fahrplan_dates_all_datesTESTDELETEEXCEPTION_2.csv', header=True,
                                            quotechar=' ',
                                            index=True, sep=';', mode='w', encoding='utf8')

        # get all stop_times and stops for every stop of one route
        fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())
        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.set_index('trip_id')

        fahrplan_calendar_weeks.to_csv('C:/Temp/fahrplan_calendar_weeksWEEKS.csv', header=True, quotechar=' ',
                                       index=True, sep=';', mode='w', encoding='utf8')

        # combine dates and trips to get a df with trips for every date
        fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())
        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype(int)
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(str)
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].apply(str)

        fahrplan_calendar_weeks.to_csv('C:/Temp/fahrplan_calendar_weeksCOMBINE.csv', header=True, quotechar=' ',
                                       index=True, sep=';', mode='w', encoding='utf8')
        fahrplan_dates_all_datesTEST = sqldf(cond_select_dates_delete_TESTWEEK, locals())
        fahrplan_dates_all_datesTEST.to_csv('C:/Temp/fahrplan_dates_all_datesTESTEXCEPTIONCOMBINE.csv', header=True,
                                            quotechar=' ',
                                            index=True, sep=';', mode='w', encoding='utf8')

        # filter days
        # fahrplan_calendar_filter_days  = sqldf(cond_filter_days_not_requested, locals())
        # fahrplan_calendar_filter_days['date'] = pd.to_datetime(fahrplan_calendar_filter_days['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_calendar_filter_days['trip_id'] = fahrplan_calendar_filter_days['trip_id'].astype(int)
        # fahrplan_calendar_filter_days['arrival_time'] = fahrplan_calendar_filter_days['arrival_time'].apply(str)

        # creating a pivot table
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence', 'stop_name'], columns=['start_time', 'trip_id'],
            values='arrival_time')
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        # releae some memory
        dfTrips = None
        dfStopTimes = None
        dfStops = None
        dfRoutes = None
        dfWeek = None
        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
        return zeit, dfheader_for_export_data, fahrplan_calendar_filter_days_pivot

    self.view.main.weekday_list.delete(0, 'end')
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[0][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[1][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[2][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[3][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[4][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[5][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[6][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[7][1]))
    self.view.main.weekday_list.insert("end", str(self.model.weekDayOptions[8][1]))