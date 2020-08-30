from typing import (
    List,
    Generic,
    TypeVar,
    Type,
    Optional
)
from abc import (
    ABC,
    abstractmethod
)

from common_decorators import lazy

from .normalizer import NormalizerProtocol


SPLITTER = ','
T = TypeVar('T', float, int)


class AbstractReader(ABC, Generic[T]):
    dtype: Type[T]

    @abstractmethod
    def readline(self) -> List[T]:
        """Reads a single line and returns the content
        """
        ...  # pragma: no cover

    def reset(self) -> None:
        """Reset the read position
        """
        ...  # pragma: no cover


class CsvReader(AbstractReader[T]):
    def __init__(
        self,
        filepath: str,
        dtype: Type[T],
        indexes: List[int],
        header: bool = False,
        splitter: str = SPLITTER,
        normalizers: List[NormalizerProtocol] = [],
        max_lines: int = -1
    ):
        self.dtype = dtype
        self._splitter = splitter
        self._indexes = indexes
        self._filepath = filepath
        self._normalizers = normalizers
        self._max_lines = max_lines
        self._header = header

        if normalizers and len(normalizers) != len(indexes):
            raise ValueError(
                f'normalizers has different length with indexes, expect {len(indexes)} but got {len(normalizers)}'
            )

        self.seek(0)

    @lazy
    def _fd(self):
        return open(self._filepath, 'r')

    @property
    def lines(self) -> int:
        return self._lines

    def max_lines(self, max_lines: int) -> None:
        """Set the max_lines of the reader
        """

        self._max_lines = max_lines

    def seek(self, pos: int) -> None:
        self._lines = pos
        self._fd.seek(pos)

        if pos == 0 and self._header:
            self._readline()

    def _readline(self) -> str:
        return self._fd.readline().strip()

    def _normalize(
        self,
        data: list
    ) -> list:
        if not self._normalizers:
            return data

        return [
            self._normalizers[i].normalize(datum)
            for i, datum in enumerate(data)
        ]

    def readline(self) -> Optional[List[T]]:
        if self._lines == self._max_lines:
            return

        line = self._readline()
        self._lines += 1

        if not line:
            return

        splitted = line.split(self._splitter)

        try:
            line = [
                self.dtype(cell)
                for i, cell in enumerate(splitted)
                if i in self._indexes
            ]
        except ValueError:
            return self.readline()

        return self._normalize(line)
