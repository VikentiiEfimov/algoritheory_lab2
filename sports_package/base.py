from abc import ABC, abstractmethod

class BaseEntity(ABC):
    """Абстрактный базовый класс для всех сущностей турнира."""

    @abstractmethod
    def get_info(self) -> str:
        """Возвращает текстовое описание сущности."""
        pass

    @abstractmethod
    def to_excel_row(self) -> list:
        """Возвращает список значений для экспорта в Excel."""
        pass