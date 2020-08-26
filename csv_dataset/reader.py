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

        self.reset()

    @lazy
    def _fd(self):
        return open(self._filepath, 'r')

    @property
    def line(self) -> int:
        return self._line

    def max_lines(self, max_lines: int) -> None:
        """Set the max_lines of the reader
        """

        self._max_lines = max_lines

    def reset(self) -> None:
        self._line = 0
        self._fd.seek(0)

        if self._header:
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
        if self._line == self._max_lines:
            return

        line = self._readline()
        self._line += 1

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
