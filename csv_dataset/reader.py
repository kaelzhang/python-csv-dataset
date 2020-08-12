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
        normalizers: List[NormalizerProtocol] = []
    ):
        self.dtype = dtype
        self._splitter = splitter
        self._indexes = indexes
        self._filepath = filepath
        self._normalizers = normalizers

        if normalizers and len(normalizers) != len(indexes):
            raise ValueError(
                f'normalizers has different length with indexes, expect {len(indexes)} but got {len(normalizers)}'
            )

        if header:
            self._readline()

    @lazy
    def _fd(self):
        return open(self._filepath, 'r')

    def reset(self) -> None:
        self._fd.seek(0)

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

        return self._normalize(line)
