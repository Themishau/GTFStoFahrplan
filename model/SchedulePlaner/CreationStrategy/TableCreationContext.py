from model.Base.Progress import ProgressSignal
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy


class TableCreationContext:
    def __init__(self, strategy: TableCreationStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> TableCreationStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: TableCreationStrategy) -> None:
        self._strategy = strategy

    def create_table(self) -> None:
        self._strategy.create_table()

    def update_progress(self, progress: ProgressSignal) -> None:
        self._strategy.update_progress(progress)

