from typing import (
    List,
    Generic,
    TypeVar,
    Type,
    Optional,
    TextIO
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

    @abstractmethod
    def reset(self) -> None:
        """Reset the reader pos
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
        self._header = header

        self.max_lines(max_lines)

        if normalizers and len(normalizers) != len(indexes):
            raise ValueError(
                f'normalizers has different length with indexes, expect {len(indexes)} but got {len(normalizers)}'
            )

        self.reset()

    @lazy
    def _fd(self) -> TextIO:
        return open(self._filepath, 'r')

    def reset(self) -> None:
        self._lines = 0
        self._fd.seek(0)

        if self._header:
            self._readline()

    def max_lines(self, max_lines: int) -> None:
        """Set the max_lines of the reader
        """

        if max_lines < -1 or max_lines == 0:
            raise ValueError(
                f'max_lines must be -1 or postivie, but got `{max_lines}`')

        self._max_lines = max_lines

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

        self._lines += 1

        return self._normalize(line)
