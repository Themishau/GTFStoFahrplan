# -*- coding: utf-8 -*-
import logging
import sys
from logging.handlers import RotatingFileHandler
from model import Model
from viewmodel import ViewModel
from view import SplashScreen
from view import View
from PySide6.QtWidgets import *
from model.infrastructure.paths.app_paths import AppPaths
from model.services.gtfs_cache_service import GtfsCacheService

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


if __name__ == '__main__':
    gtfs_app = QApplication(sys.argv)
    gtfs_app.setOrganizationName('GTFStoFahrplan')
    gtfs_app.setApplicationName('GTFStoFahrplan')
    paths = AppPaths.for_user()
    log_handler = RotatingFileHandler(paths.logs / 'application.log', maxBytes=2_000_000,
                                     backupCount=3, encoding='utf-8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    logging.getLogger().addHandler(log_handler)
    model = Model(gtfs_app, GtfsCacheService.for_paths(paths))
    viewModel = ViewModel(app=gtfs_app, model=model)
    view = View(viewModel=viewModel)
    # show a nice loading window first
    window = SplashScreen(view)
    gtfs_app.aboutToQuit.connect(model.close)

    sys.exit(gtfs_app.exec())
