from typing import (
    List,
    Generic,
    TypeVar,
    Type
)
from abc import (
    ABC,
    abstractmethod
)

from common_decorators import lazy


SPLITTER = ','
T = TypeVar('T', float, int)


class AbstractReader(ABC, Generic[T]):
    dtype: Type[T]

    @abstractmethod
    def readline(self) -> List[T]:
        """Reads a single line and returns the content
        """
        ...


class CsvReader(AbstractReader[T]):
    def __init__(
        self,
        filepath: str,
        dtype: Type[T],
        indexes: List[int],
        header: bool = False,
        splitter: str = SPLITTER
    ):
        self.dtype = dtype
        self._splitter = splitter
        self._indexes = indexes
        self._filepath = filepath

        if header:
            self._readline()

    @lazy
    def _fd(self):
        return open(self._filepath, 'r')

    def _readline(self) -> str:
        return self._fd.readline()

    def readline(self) -> List[T]:
        line = self._readline()

        return [
            self.dtype(cell)
            for i, cell in enumerate(line.split(self._splitter))
            if i in self._indexes
        ]
