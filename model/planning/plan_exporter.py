"""CSV export for timetables and vehicle circulation plans."""

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from model.domain.planning_settings import PlanningSettings
from model.domain.timetable_data import TimetableData
from model.enums import ProcessKind
from model.planning.progress import ProgressUpdate


class PlanExporter(QObject):
    progress_updated = Signal(ProgressUpdate)

    def __init__(self):
        super().__init__()
        self.progress = ProgressUpdate()

    def export_timetable(self, settings: PlanningSettings, timetable: TimetableData) -> None:
        self._write_timetable(settings, timetable)
        self._emit_complete()

    def export_circulation_plan(self, settings: PlanningSettings, plans: list) -> None:
        self._write_circulation_plan(settings, plans)
        self._emit_complete()

    def _write_timetable(self, settings: PlanningSettings, timetable: TimetableData) -> None:
        if settings.route is None or settings.route.empty:
            raise ValueError("Select a route before exporting a timetable")
        output = self._output_file(settings, settings.route, "dates")
        timetable.header.to_csv(output, header=True, quotechar=" ", sep=";", mode="w", encoding="utf8")
        timetable.timetable.to_csv(
            output, header=True, quotechar=" ", index=True, sep=";", mode="a", encoding="utf8"
        )

    def _write_circulation_plan(self, settings: PlanningSettings, plans: list) -> None:
        if not plans:
            raise ValueError("No circulation plans are available to export")
        if (
            plans[0].planning_settings.route is None
            or plans[0].planning_settings.route.empty
        ):
            raise ValueError("Select a route before exporting a circulation plan")
        output = self._output_file(
            settings,
            plans[0].planning_settings.route,
            "circulation_plan_dates",
        )
        for index, plan in enumerate(plans):
            mode = "w" if index == 0 else "a"
            plan.timetable_data.header.to_csv(
                output, header=True, quotechar=" ", sep=";", mode=mode, encoding="utf8"
            )
            plan.timetable_data.timetable.to_csv(
                output, header=True, quotechar=" ", index=True, sep=";", mode="a", encoding="utf8"
            )

    @staticmethod
    def _output_file(settings: PlanningSettings, route, label: str) -> Path:
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        route_name = str(route["route_short_name"].iloc[0])
        output = Path(settings.output_path) / f"{route_name}_{label}_{timestamp}_pivot_table.csv"
        output.parent.mkdir(parents=True, exist_ok=True)
        settings.full_output_path = str(output)
        return output

    def _emit_complete(self) -> None:
        self.progress_updated.emit(
            self.progress.set_progress(100, ProcessKind.EXPORT_PLAN, "Export complete")
        )
