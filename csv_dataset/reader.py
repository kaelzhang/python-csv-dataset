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
from .common import max_lines_error


SPLITTER = ','
T = TypeVar('T', float, int)


class AbstractReader(ABC, Generic[T]):
    dtype: Type[T]

    _max_lines: Optional[int]
    _max_lines = None

    @property
    def max_lines(self) -> Optional[int]:
        return self._max_lines

    @max_lines.setter
    def max_lines(self, max_lines: Optional[int]) -> None:
        self._set_max_lines(max_lines)

    def _set_max_lines(self, max_lines: Optional[int]) -> None:
        """Set the max_lines of the reader

        Args:
            max_lines (int | None): if None, it indicates where is no limit
        """

        if max_lines is None:
            self._max_lines = None
            return

        if max_lines <= 0:
            raise max_lines_error(max_lines)

        self._max_lines = max_lines

    @abstractmethod
    def readline(_) -> List[T]:
        """Reads a single line and returns the content
        """
        ...  # pragma: no cover

    @abstractmethod
    def reset(_) -> None:
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
        max_lines: Optional[int] = None
    ):
        self.dtype = dtype
        self._splitter = splitter
        self._indexes = indexes
        self._filepath = filepath
        self._normalizers = normalizers
        self._header = header

        self.max_lines = max_lines

        if normalizers and len(normalizers) != len(indexes):
            raise ValueError(
                f'normalizers has different length with indexes, expect {len(indexes)} but got {len(normalizers)}'
            )

        self.reset()

    @property
    def lines(self) -> int:
        """How many lines the reader has read
        """

        return self._lines

    # @property
    # def pos(self) -> int:
    #     """The stream position of the reader
    #     """

    #     return self._pos

    @lazy
    def _fd(self) -> TextIO:
        # Ref
        # https://docs.python.org/3/library/io.html
        return open(self._filepath, 'r')

    def reset(self) -> None:
        self._lines = 0
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
        if self._lines == self._max_lines:
            return

        line = self._readline()
        # self._pos = self._fd.tell()

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
