from abc import ABC, abstractmethod

class TableCreationStrategy(ABC):
    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def update_progress(self, value):
        pass
