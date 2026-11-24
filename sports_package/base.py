from abc import ABC, abstractmethod
from datetime import datetime

class BaseEntity(ABC):
    """Абстрактный базовый класс для всех сущностей турнира."""
    def __init__(self, created_at: str | None = None):
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def touch(self) -> None:
        """Обновляет временную метку до текущего момента."""
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def get_info(self) -> str:
        """Возвращает текстовое описание сущности."""
        pass

    @abstractmethod
    def to_excel_row(self) -> list:
        """Возвращает список значений для экспорта в Excel."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(created_at={self.created_at!r})"