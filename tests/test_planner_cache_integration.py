import copy
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pandas as pd
from PySide6.QtCore import QEventLoop, QThread, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from model.planning.exporter import PlanExporter
from model.domain.planning_settings import PlanningSettings
from model.domain.in_memory_gtfs_data import InMemoryGtfsData
from model.enums import PlanMode
from model.planning.strategies.parallel_strategy import ParallelTableCreationStrategy
from model.planning.strategies.sequential_strategy import SequentialTableCreationStrategy
from model.planning.vehicle_circulation_planner import VehicleCirculationPlanner
from model.infrastructure.paths.app_paths import AppPaths
from model.application_model import ApplicationModel
from model.services.cached_gtfs_data import CachedGtfsData
from model.services.gtfs_cache_service import GtfsCacheService
from tests.gtfs_fixtures import make_feed


class PlannerCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.paths = AppPaths(self.root / "app")
        self.cache = GtfsCacheService.for_paths(self.paths)
        self.addCleanup(self.cache.close)
        self.zip_path = make_feed(self.root / "feed.zip")
        self.feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.source = CachedGtfsData(self.feed, self.cache.repository)

    def settings(self, mode):
        settings = PlanningSettings()
        settings.agency = self.source.agencies
        settings.route = self.source.routes.query("route_id == 'r1'")
        settings.date = "20260912"
        settings.output_path = str(self.root)
        settings.create_plan_mode = mode
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        settings.weekday = pd.DataFrame({"day": ["All Days"], "category": ["All Days"],
                                         **{day: [day] for day in days}})
        return settings

    def legacy_source(self):
        repo = self.cache.repository
        return InMemoryGtfsData(self.source.routes, repo.get_trips(self.feed.feed_id),
                                repo.get_stop_times_for_trips(self.feed.feed_id, ["t1", "t2", "t3"]),
                                repo.get_stops(self.feed.feed_id), self.source.calendar,
                                self.source.calendar_dates, self.source.agencies, self.source.feed_info)

    def test_date_plan_matches_legacy_source_and_exports(self):
        settings = self.settings(PlanMode.DATE)
        legacy = self.legacy_source()
        snapshot = copy.deepcopy(legacy)
        expected = SequentialTableCreationStrategy(self.app, settings, legacy)
        expected.create_table()
        cached = SequentialTableCreationStrategy(self.app, settings, self.source)
        with patch.object(self.cache.repository, "get_stop_times_for_trips",
                          wraps=self.cache.repository.get_stop_times_for_trips) as query:
            cached.create_table()
        self.assertEqual(list(query.call_args.args[1]), ["t1"])
        self.assertIs(cached.plans.gtfs_data, self.source)
        result = cached.plans.timetable_data.timetable
        pd.testing.assert_frame_equal(result, expected.plans.timetable_data.timetable)
        self.assertEqual(result.iloc[:, 0].tolist(), ["06:30", "06:40"])
        for name, frame in vars(legacy).items():
            if isinstance(frame, pd.DataFrame):
                pd.testing.assert_frame_equal(frame, getattr(snapshot, name))
        PlanExporter(self.app).export_plan(settings, cached.plans.timetable_data)
        text = Path(settings.full_output_path).read_text(encoding="utf-8")
        self.assertIn("06:30", text)
        self.assertIn("Central", text)

    def test_parallel_directions_share_source_and_export_circulation(self):
        settings = self.settings(PlanMode.CIRCULATION_DATE)
        strategy = ParallelTableCreationStrategy(self.app, settings, self.source)
        with patch.object(self.cache.repository, "get_stop_times_for_trips",
                          wraps=self.cache.repository.get_stop_times_for_trips) as query:
            strategy.create_table()
        self.assertEqual({tuple(call.args[1]) for call in query.call_args_list}, {("t1",), ("t2",)})
        self.assertTrue(all(plan.gtfs_data is self.source for plan in strategy.plans))
        self.assertIsNot(strategy.plans[0].planning_settings,
                         strategy.plans[1].planning_settings)
        circle = VehicleCirculationPlanner(strategy.plans, self.app)
        self.assertTrue(circle.create_circulation_plan())
        PlanExporter(self.app).export_circle_plan(settings, strategy.plans)
        text = Path(settings.full_output_path).read_text(encoding="utf-8")
        self.assertIn("06:30", text)
        self.assertIn("06:45", text)

    def test_weekday_plan(self):
        strategy = SequentialTableCreationStrategy(self.app, self.settings(PlanMode.WEEKDAY), self.source)
        strategy.create_table()
        self.assertFalse(strategy.plans.timetable_data.timetable.empty)

    def test_weekday_individual_sorting_continue(self):
        settings = self.settings(PlanMode.WEEKDAY)
        settings.use_individual_sorting = True
        strategy = SequentialTableCreationStrategy(self.app, settings, self.source)
        strategy.create_table()
        strategy.create_table_continue()
        self.assertFalse(strategy.plans.timetable_data.timetable.empty)

    def test_circulation_weekday_export(self):
        settings = self.settings(PlanMode.CIRCULATION_WEEKDAY)
        strategy = ParallelTableCreationStrategy(self.app, settings, self.source)
        strategy.create_table()
        VehicleCirculationPlanner(strategy.plans, self.app).create_circulation_plan()
        PlanExporter(self.app).export_circle_plan(settings, strategy.plans)
        self.assertTrue(Path(settings.full_output_path).is_file())

    def test_calendar_dates_only_plan(self):
        make_feed(self.zip_path, calendar=False)
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        source = CachedGtfsData(feed, self.cache.repository)
        strategy = SequentialTableCreationStrategy(self.app, self.settings(PlanMode.DATE), source)
        strategy.create_table()
        self.assertEqual(strategy.plans.timetable_data.timetable.iloc[:, 0].tolist(),
                         ["06:30", "06:40"])

    def test_individual_sorting_continue(self):
        settings = self.settings(PlanMode.DATE)
        settings.use_individual_sorting = True
        strategy = SequentialTableCreationStrategy(self.app, settings, self.source)
        strategy.create_table()
        strategy.create_table_continue()
        self.assertFalse(strategy.plans.timetable_data.timetable.empty)

    def wait_worker(self, model):
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        def done(busy):
            if not busy:
                loop.quit()
        model.busy_changed.connect(done)
        timer.start(10000)
        loop.exec()
        model.busy_changed.disconnect(done)
        timer.stop()
        self.assertIsNone(model.thread, "QThread did not finish")

    def test_qthread_import_and_reopen_without_zip(self):
        from viewmodel.application import ApplicationViewModel
        model = ApplicationModel(self.app, self.cache)
        vm = ApplicationViewModel(self.app, model)
        errors = []
        model.error_occurred.connect(errors.append)
        import_vm = vm.import_view_model
        import_vm.set_input_path((str(self.zip_path), "ZIP"))
        threads = []
        calculate = self.cache.fingerprint_service.calculate
        def record(*args):
            threads.append(QThread.currentThread() == self.app.thread())
            return calculate(*args)
        with patch.object(self.cache.fingerprint_service, "calculate", side_effect=record):
            import_vm.start_import()
            self.wait_worker(model)
        self.assertEqual(errors, [])
        self.assertEqual(threads, [False])
        self.assertEqual(model.planner.gtfs_data.feed.feed_id, self.feed.feed_id)
        self.zip_path.unlink()
        import_vm.open_feed(self.feed.feed_id)
        self.wait_worker(model)
        self.assertEqual(errors, [])
        self.assertEqual(import_vm.get_agencies_df().agency_id.tolist(), ["001"])
        import_vm.delete_feed(self.feed.feed_id)
        self.wait_worker(model)
        self.assertIsNone(model.planner.gtfs_data)
        self.assertEqual(import_vm.recent_feeds, [])

    def test_recent_feed_ui_after_restart(self):
        from viewmodel.application import ApplicationViewModel
        from view.main_window import MainWindow
        self.cache.close()
        self.zip_path.unlink()
        self.cache = GtfsCacheService.for_paths(self.paths)
        self.addCleanup(self.cache.close)
        model = ApplicationModel(self.app, self.cache)
        vm = ApplicationViewModel(self.app, model)
        window = MainWindow(vm)
        self.addCleanup(window.close)
        self.assertEqual(window.recent_feeds_combo.currentData(), self.feed.feed_id)
        self.assertTrue(window.open_feed_button.isEnabled())
        self.assertIn("2026-09-12", window.recent_feed_details.text())
        window.open_feed_button.click()
        self.wait_worker(model)
        self.assertEqual(vm.import_view_model.get_agencies_df().agency_id.tolist(), ["001"])
        window.delete_feed_button.click()
        self.wait_worker(model)
        self.assertEqual(window.recent_feeds_combo.count(), 0)
        self.assertFalse(window.ui.btnStart.isEnabled())

    def test_delete_all_cache_ui_and_storage_indicator(self):
        from viewmodel.application import ApplicationViewModel
        from view.main_window import MainWindow
        model = ApplicationModel(self.app, self.cache)
        vm = ApplicationViewModel(self.app, model)
        window = MainWindow(vm)
        self.addCleanup(window.close)
        size_before = self.cache.database_size_bytes()

        self.assertRegex(window.cache_size_label.text(), r'^DuckDB storage: \d+\.\d{2} (MB|GB)$')
        self.assertTrue(window.delete_all_feeds_button.isEnabled())
        with patch('view.main_window.QMessageBox.question',
                   return_value=QMessageBox.StandardButton.Yes) as confirmation:
            window.delete_all_feeds_button.click()
            self.wait_worker(model)

        confirmation.assert_called_once()
        self.assertEqual(window.recent_feeds_combo.count(), 0)
        self.assertFalse(window.delete_all_feeds_button.isEnabled())
        self.assertFalse(window.ui.btnStart.isEnabled())
        self.assertLess(self.cache.database_size_bytes(), size_before)
        self.assertEqual(
            window.cache_size_label.text(),
            f'DuckDB storage: {vm.import_view_model.get_database_size_text()}',
        )

    def test_gui_remains_responsive_during_hash_and_cancel(self):
        model = ApplicationModel(self.app, self.cache)
        model.setup_schedule_planner()
        model.planner.import_settings.input_path = str(self.zip_path)
        tick = threading.Event()
        calculate = self.cache.fingerprint_service.calculate
        def delayed_hash(*args):
            self.assertTrue(tick.wait(5), "GUI event loop stalled")
            return calculate(*args)
        errors = []
        model.error_occurred.connect(errors.append)
        def gui_tick():
            model.cancel_async_operation()
            tick.set()
        with patch.object(self.cache.fingerprint_service, "calculate", side_effect=delayed_hash):
            model.start_function_async("import_gtfs")
            QTimer.singleShot(10, gui_tick)
            self.wait_worker(model)
        self.assertTrue(tick.is_set())
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
