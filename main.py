import logging
import sys
from logging.handlers import RotatingFileHandler

from PySide6.QtWidgets import QApplication

from model import ApplicationModel
from model.infrastructure.paths.app_paths import AppPaths
from model.services.gtfs_cache_service import GtfsCacheService
from view import MainWindow, SplashScreen
from viewmodel import ApplicationViewModel


def configure_logging(paths: AppPaths) -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_handler = RotatingFileHandler(
        paths.logs / "application.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    log_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logging.getLogger().addHandler(log_handler)


def main() -> int:
    application = QApplication(sys.argv)
    application.setOrganizationName("GTFStoFahrplan")
    application.setApplicationName("GTFStoFahrplan")

    paths = AppPaths.for_user()
    configure_logging(paths)
    model = ApplicationModel(application, GtfsCacheService.for_paths(paths))
    view_model = ApplicationViewModel(model=model, parent=application)
    main_window = MainWindow(view_model=view_model)
    _splash_screen = SplashScreen(main_window)
    application.aboutToQuit.connect(model.close)

    # The local reference keeps the splash screen alive while the event loop starts.
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
