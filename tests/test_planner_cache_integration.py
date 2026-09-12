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
from PySide6.QtWidgets import QApplication

from model.Base.ExportPlan import ExportPlan
from model.Dto.CreateSettingsForTableDto import CreateSettingsForTableDto
from model.Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from model.Enum.GTFSEnums import CreatePlanMode
from model.SchedulePlaner.CreationStrategy.ParallelTableCreationStrategy import ParallelTableCreationStrategy
from model.SchedulePlaner.CreationStrategy.SequentialTableCreationStrategy import SequentialTableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.CirclePlaner import CirclePlaner
from model.infrastructure.paths.app_paths import AppPaths
from model.model import Model
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
        settings = CreateSettingsForTableDto()
        settings.agency = self.source.Agencies
        settings.route = self.source.Routes.query("route_id == 'r1'")
        settings.date = "20260912"
        settings.output_path = str(self.root)
        settings.create_plan_mode = mode
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        settings.weekday = pd.DataFrame({"day": ["All Days"], "category": ["All Days"],
                                         **{day: [day] for day in days}})
        return settings

    def legacy_source(self):
        repo = self.cache.repository
        return GtfsDataFrameDto(self.source.Routes, repo.get_trips(self.feed.feed_id),
                                repo.get_stop_times_for_trips(self.feed.feed_id, ["t1", "t2", "t3"]),
                                repo.get_stops(self.feed.feed_id), self.source.Calendarweeks,
                                self.source.Calendardates, self.source.Agencies, self.source.Feedinfos)

    def test_date_plan_matches_legacy_source_and_exports(self):
        settings = self.settings(CreatePlanMode.date)
        legacy = self.legacy_source()
        snapshot = copy.deepcopy(legacy)
        expected = SequentialTableCreationStrategy(self.app, settings, legacy)
        expected.create_table()
        cached = SequentialTableCreationStrategy(self.app, settings, self.source)
        with patch.object(self.cache.repository, "get_stop_times_for_trips",
                          wraps=self.cache.repository.get_stop_times_for_trips) as query:
            cached.create_table()
        self.assertEqual(list(query.call_args.args[1]), ["t1"])
        self.assertIs(cached.plans.gtfs_data_frame_dto, self.source)
        result = cached.plans.create_dataframe.FahrplanCalendarFilterDaysPivot
        pd.testing.assert_frame_equal(result, expected.plans.create_dataframe.FahrplanCalendarFilterDaysPivot)
        self.assertEqual(result.iloc[:, 0].tolist(), ["06:30", "06:40"])
        for name, frame in vars(legacy).items():
            if isinstance(frame, pd.DataFrame):
                pd.testing.assert_frame_equal(frame, getattr(snapshot, name))
        ExportPlan(self.app).export_plan(settings, cached.plans.create_dataframe)
        text = Path(settings.full_output_path).read_text(encoding="utf-8")
        self.assertIn("06:30", text)
        self.assertIn("Central", text)

    def test_parallel_directions_share_source_and_export_umlauf(self):
        settings = self.settings(CreatePlanMode.umlauf_date)
        strategy = ParallelTableCreationStrategy(self.app, settings, self.source)
        with patch.object(self.cache.repository, "get_stop_times_for_trips",
                          wraps=self.cache.repository.get_stop_times_for_trips) as query:
            strategy.create_table()
        self.assertEqual({tuple(call.args[1]) for call in query.call_args_list}, {("t1",), ("t2",)})
        self.assertTrue(all(plan.gtfs_data_frame_dto is self.source for plan in strategy.plans))
        self.assertIsNot(strategy.plans[0].create_settings_for_table_dto,
                         strategy.plans[1].create_settings_for_table_dto)
        circle = CirclePlaner(strategy.plans, self.app)
        self.assertTrue(circle.CreateCirclePlan())
        ExportPlan(self.app).export_circle_plan(settings, strategy.plans)
        text = Path(settings.full_output_path).read_text(encoding="utf-8")
        self.assertIn("06:30", text)
        self.assertIn("06:45", text)

    def test_weekday_plan(self):
        strategy = SequentialTableCreationStrategy(self.app, self.settings(CreatePlanMode.weekday), self.source)
        strategy.create_table()
        self.assertFalse(strategy.plans.create_dataframe.FahrplanCalendarFilterDaysPivot.empty)

    def test_weekday_individual_sorting_continue(self):
        settings = self.settings(CreatePlanMode.weekday)
        settings.use_individual_sorting = True
        strategy = SequentialTableCreationStrategy(self.app, settings, self.source)
        strategy.create_table()
        strategy.create_table_continue()
        self.assertFalse(strategy.plans.create_dataframe.FahrplanCalendarFilterDaysPivot.empty)

    def test_umlauf_weekday_export(self):
        settings = self.settings(CreatePlanMode.umlauf_weekday)
        strategy = ParallelTableCreationStrategy(self.app, settings, self.source)
        strategy.create_table()
        CirclePlaner(strategy.plans, self.app).CreateCirclePlan()
        ExportPlan(self.app).export_circle_plan(settings, strategy.plans)
        self.assertTrue(Path(settings.full_output_path).is_file())

    def test_calendar_dates_only_plan(self):
        make_feed(self.zip_path, calendar=False)
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        source = CachedGtfsData(feed, self.cache.repository)
        strategy = SequentialTableCreationStrategy(self.app, self.settings(CreatePlanMode.date), source)
        strategy.create_table()
        self.assertEqual(strategy.plans.create_dataframe.FahrplanCalendarFilterDaysPivot.iloc[:, 0].tolist(),
                         ["06:30", "06:40"])

    def test_individual_sorting_continue(self):
        settings = self.settings(CreatePlanMode.date)
        settings.use_individual_sorting = True
        strategy = SequentialTableCreationStrategy(self.app, settings, self.source)
        strategy.create_table()
        strategy.create_table_continue()
        self.assertFalse(strategy.plans.create_dataframe.FahrplanCalendarFilterDaysPivot.empty)

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
        from viewmodel.view_model import ViewModel
        model = Model(self.app, self.cache)
        vm = ViewModel(self.app, model)
        errors = []
        model.error_occurred.connect(errors.append)
        import_vm = vm.view_model_import_data
        import_vm.on_change_input_file_path((str(self.zip_path), "ZIP"))
        threads = []
        calculate = self.cache.fingerprint_service.calculate
        def record(*args):
            threads.append(QThread.currentThread() == self.app.thread())
            return calculate(*args)
        with patch.object(self.cache.fingerprint_service, "calculate", side_effect=record):
            import_vm.start_import_gtfs_data()
            self.wait_worker(model)
        self.assertEqual(errors, [])
        self.assertEqual(threads, [False])
        self.assertEqual(model.planer.gtfs_data_frame_dto.feed.feed_id, self.feed.feed_id)
        self.zip_path.unlink()
        import_vm.open_feed(self.feed.feed_id)
        self.wait_worker(model)
        self.assertEqual(errors, [])
        self.assertEqual(import_vm.get_agencies_df().agency_id.tolist(), ["001"])
        import_vm.delete_feed(self.feed.feed_id)
        self.wait_worker(model)
        self.assertIsNone(model.planer.gtfs_data_frame_dto)
        self.assertEqual(import_vm.recent_feeds, [])

    def test_recent_feed_ui_after_restart(self):
        from viewmodel.view_model import ViewModel
        from view.view import View
        self.cache.close()
        self.zip_path.unlink()
        self.cache = GtfsCacheService.for_paths(self.paths)
        self.addCleanup(self.cache.close)
        model = Model(self.app, self.cache)
        vm = ViewModel(self.app, model)
        window = View(vm)
        self.addCleanup(window.close)
        self.assertEqual(window.recent_feeds_combo.currentData(), self.feed.feed_id)
        self.assertTrue(window.open_feed_button.isEnabled())
        self.assertIn("2026-09-12", window.recent_feed_details.text())
        window.open_feed_button.click()
        self.wait_worker(model)
        self.assertEqual(vm.view_model_import_data.get_agencies_df().agency_id.tolist(), ["001"])
        window.delete_feed_button.click()
        self.wait_worker(model)
        self.assertEqual(window.recent_feeds_combo.count(), 0)
        self.assertFalse(window.ui.btnStart.isEnabled())

    def test_gui_remains_responsive_during_hash_and_cancel(self):
        model = Model(self.app, self.cache)
        model.set_up_schedule_planer()
        model.planer.import_settings_dto.input_path = str(self.zip_path)
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
            model.start_function_async("planer_start_load_data")
            QTimer.singleShot(10, gui_tick)
            self.wait_worker(model)
        self.assertTrue(tick.is_set())
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
