from typing import (
    Optional,
    Callable
)

import numpy as np

from common_decorators import lazy

from .reader import ReaderProtocol


Mapper = Callable[[list], list]

# numpy stride for float is 8
BYTE_STRIDE = 8


def default_mapper(lst: list):
    return np.array(lst)


class CsvDataset:
    def __init__(
        self,
        reader: ReaderProtocol,
        column_types: list[Callable],
        header: bool = False
    ):
        self._reader = reader
        self._header = header
        self._column_types = column_types
        self._line_pointer = 0

        self._mapper = default_mapper
        self._batch = 1

        self._reshapes = []

        self._window_size = 1
        self._window_shift = None
        self._window_stride = 1
        self._window_drop_remainder = False

        if header:
            self._fd.readline()

    @lazy
    def _single_size(self) -> int:
        """Size of the underlying datum referred to a single window
        """

        return (self._window_size - 1) * self._window_stride + 1

    @lazy
    def _single_step(self) -> int:
        """stride without considering the batch size
        """
        return self._window_shift * self._window_stride

    @lazy
    def _size(self) -> int:
        return self._single_size + (self._batch - 1) * self._single_stride

    @lazy
    def _step(self) -> int:
        return self._batch * self._single_stride

    @lazy
    def _buffer(self):
        return self._readlines(self._size, [])

    def map_series(
        self,
        mapper: Mapper
    ) -> 'CsvDataset':
        """Maps `mapper` across each series record of the csv
        """

        self._mapper = mapper

        return self

    def _check_start(self, method_name: str):
        if self._line_pointer != 0:
            raise RuntimeError(f'calling {method_name}() during reading is forbidden')

    def window(
        self,
        window_size: int,
        shift: Optional[int] = None,
        stride: int = 1,
        drop_remainder: bool = False
    ) -> 'CsvDataset':
        """Combines (nests of) input elements into a dataset of (nests of) windows.

        |-------- size:3 --------|
        |- stride:1 -|           |
        |            |           |
        1            2           3 --------|---
                                        shift:2
        3            4           5 --------|---

        5            6           7

        least: (size - 1) * stride + 1
        step : shift * stride
        """

        self._check_start('window')

        self._window_size = window_size
        self._window_shift = shift or window_size
        self._window_stride = stride
        self._drop_remainder = drop_remainder

        return self

    def batch(
        self,
        batch: int
    ) -> 'CsvDataset':
        """Combines consecutive elements of this dataset into batches.
        """

        self._check_start('batch')

        self._batch = batch

        return self

    def _readlines(
        self,
        lines: int,
        dest_buffer: list,
        slice_size: bool = False
    ) -> list:
        read = 0

        while read < lines:
            dest_buffer.append(self._readline())
            read += 1

        if slice_size:
            dest_buffer = dest_buffer.slice(read)

        return dest_buffer

    def get(self) -> Optional[np.ndarray]:
        buffer = self._buffer

        if not buffer:
            # There is no data
            return

        array = np.array(buffer)

        windowed = np.lib.stride_tricks.as_strided(
            array,
            shape=(
                len(array) - self._window_size + 1,
                period
            ),
            strides=(BYTE_STRIDE, BYTE_STRIDE)
        )


        self._buffer = self._readlines(buffer, self._stride, True)


from pathlib import Path

csv_path = Path(Path(__file__).resolve()).parent.parent.parent / \
    'ostai-compton' / 'ostai' / 'data' / 'binance_1m_2019-12-20 00:00:00.csv'


dataset = CsvDataset(
    csv_path.absolute(),
    [
        int,
        int,
        float, float, float, float, float,
        int,
        float, float, float, float
    ],
    header=True
)

print(dataset.get())
print(dataset.get())

# f = open(csv_path.absolute(), 'r')

# lines = f.readlines()

# print(lines)

# for line in lines:
#     print(line)
