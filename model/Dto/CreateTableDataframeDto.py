class CreateTableDataframeDto:
    def __init__(self):
        self.Header = None
        self.Direction = None
        self.RequestedDates = None
        self.RequestedWeekdays = None
        self.SelectedRoute = None
        self.SelectedAgency = None
        self.FahrplanDates = None
        self.FahrplanStops = None
        self.SortedDataframe = None
        self.FilteredStopNamesDataframe = None
        self.GftsTableData = None
        self.FahrplanCalendarFilterDaysPivot = None