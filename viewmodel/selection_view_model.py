from PySide6.QtCore import QObject, Signal


class SelectionViewModel(QObject):
    routes_changed = Signal()
    error_message = Signal(str)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

    def notify_routes_changed(self):
        self.routes_changed.emit()

    def get_selected_agency_text(self):
        return self.model.planner.planning_settings.selected_agency_text

    def get_selected_route_text(self):
        return self.model.planner.planning_settings.selected_route_text

    def get_routes_df(self):
        return self.model.planner.planning_settings.selected_routes

    def get_selected_route_date_range_text(self):
        date_range_df = self.model.planner.planning_settings.selected_route_date_range
        if (date_range_df is None
                or date_range_df.get('start_date') is None
                or date_range_df.get('end_date') is None):
            return None

        start_date = date_range_df['start_date']
        end_date = date_range_df['end_date']
        return f"{start_date.iloc[0].strftime('%Y-%m-%d')} - {end_date.iloc[0].strftime('%Y-%m-%d')}"

    def get_selected_route_sample_date(self):
        date_range_df = self.model.planner.planning_settings.selected_route_date_range
        if date_range_df is None or date_range_df.get('start_date') is None:
            return None
        return date_range_df['start_date'].iloc[0].strftime('%Y-%m-%d')

    def select_agency(self, index):
        self.model.planner.planning_settings.agency = index
        self.model.planner.planning_settings.selected_routes = self.model.planner.data_analyzer.get_routes_for_agency(
            self.model.planner.gtfs_data,
            self.model.planner.planning_settings.agency,
        )
        self.notify_routes_changed()

    def select_route(self, route):
        self.model.planner.planning_settings.route = route
        if self.model.planner.planning_settings.route is not None:
            self.model.planner.data_analyzer.update_selected_route_date_range(
                self.model.planner.gtfs_data,
                self.model.planner.planning_settings,
            )

    def send_error_message(self, message):
        self.error_message.emit(message)
