import pandas as pd
from PySide6.QtCore import QObject, Signal

from model.application_model import ApplicationModel


class SelectionViewModel(QObject):
    routes_changed = Signal()
    error_message = Signal(str)

    def __init__(
            self,
            model: ApplicationModel,
            parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.model = model

    def notify_routes_changed(self) -> None:
        self.routes_changed.emit()

    def get_selected_agency_text(self) -> str:
        return self.model.planner.planning_settings.selected_agency_text

    def get_selected_route_text(self) -> str:
        return self.model.planner.planning_settings.selected_route_text

    def get_routes_df(self) -> pd.DataFrame | None:
        return self.model.planner.planning_settings.selected_routes

    def get_selected_route_date_range_text(self) -> str | None:
        date_range_df = self.model.planner.planning_settings.selected_route_date_range
        if (date_range_df is None
                or date_range_df.get('start_date') is None
                or date_range_df.get('end_date') is None):
            return None

        start_date = date_range_df['start_date']
        end_date = date_range_df['end_date']
        return f"{start_date.iloc[0].strftime('%Y-%m-%d')} - {end_date.iloc[0].strftime('%Y-%m-%d')}"

    def get_selected_route_sample_date(self) -> str | None:
        date_range_df = self.model.planner.planning_settings.selected_route_date_range
        if date_range_df is None or date_range_df.get('start_date') is None:
            return None
        return date_range_df['start_date'].iloc[0].strftime('%Y-%m-%d')

    def select_agency(self, agency: pd.DataFrame) -> None:
        gtfs_data = self.model.planner.gtfs_data
        if gtfs_data is None:
            self.send_error_message("Open a GTFS feed before selecting an agency.")
            return
        self.model.planner.planning_settings.agency = agency
        self.model.planner.planning_settings.selected_routes = self.model.planner.data_analyzer.get_routes_for_agency(
            gtfs_data,
            self.model.planner.planning_settings.agency,
        )
        self.notify_routes_changed()

    def select_route(self, route: pd.DataFrame) -> None:
        gtfs_data = self.model.planner.gtfs_data
        if gtfs_data is None:
            self.send_error_message("Open a GTFS feed before selecting a route.")
            return
        self.model.planner.planning_settings.route = route
        if self.model.planner.planning_settings.route is not None:
            self.model.planner.data_analyzer.update_selected_route_date_range(
                gtfs_data,
                self.model.planner.planning_settings,
            )

    def send_error_message(self, message: str) -> None:
        self.error_message.emit(message)
