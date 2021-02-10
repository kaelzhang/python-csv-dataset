from typing import (
    Optional,
    TypeVar,
    Generic
)

import numpy as np

from common_decorators import lazy

from .reader import AbstractReader
from .common import (
    rolling_window,
    max_lines_error
)

T = TypeVar('T')


class Dataset(Generic[T]):
    _reader: AbstractReader[T]

    def __init__(
        self,
        reader: AbstractReader[T]
    ):
        self._reader = reader
        self._buffer_read = False

        self._batch = 1

        self._window_size = 1
        self._window_shift = 1
        self._window_stride = 1
        self._window_drop_remainder = False

        self.reset()

    def reset(self) -> None:
        self._reader.reset()
        self._buffer = None

        return self

    # |-------- size:3 --------|
    # |- stride:1 -|           |
    # |            |           |
    # 1            2           3 --------|---
    #                                 shift:2
    # 3            4           5 --------|---
    #
    # 5            6           7
    #
    # least: (size - 1) * stride + 1
    # step : shift * stride
    @lazy
    def _single_least(self) -> int:
        """The least size (lines) of the underlying datum referred to the first single window
        """

        return (self._window_size - 1) * self._window_stride + 1

    @lazy
    def _single_stride(self) -> int:
        """stride without considering the batch size
        """
        return self._window_shift * self._window_stride

    @lazy
    def _least(self) -> int:
        """The least size (lines) of the underlying datum referered to the first batch read
        """

        return self._single_least + (self._batch - 1) * self._single_stride

    @lazy
    def _stride(self) -> int:
        """stride that considering window stride and batch size
        """

        return self._batch * self._single_stride

    def lines_need(self, reads: int) -> int:
        """Calculate how many lines of datum needed for reading `reads` times
        """

        return self._least + (reads - 1) * self._stride

    def max_reads(self, max_lines: Optional[int] = None) -> Optional[int]:
        """How many reads does the current dataset afford

        Args:
            max_lines (:obj:`int`, optional)

        Returns:
            - None which indicates the dataset could not know about it. If max_lines is not provided, and the reader has no max_lines
            - int otherwise
        """

        if max_lines is None:
            max_lines = self._reader.max_lines

        if max_lines is None:
            return None

        if max_lines <= 0:
            raise max_lines_error(max_lines)

        rest = max_lines - self._least

        return 0 if rest < 0 else 1 + rest // self._stride

    def _check_start(self, method_name: str):
        if self._buffer_read:
            raise RuntimeError(f'calling {method_name}() during reading is forbidden')

    def window(
        self,
        size: int,
        shift: Optional[int] = None,
        stride: int = 1
    ) -> 'Dataset':
        """Combines (nests of) input elements into a dataset of (nests of) windows.
        """

        self._check_start('window')

        self._window_size = size
        self._window_shift = shift or size
        self._window_stride = stride

        return self

    def batch(
        self,
        batch: int
    ) -> 'Dataset':
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
            line = self._reader.readline()

            if line is None:
                # Reaches EOF
                return []

            dest_buffer.append(line)
            read += 1

        if slice_size:
            dest_buffer = dest_buffer[lines:]

        return dest_buffer

    def _read_buffer(self):
        if self._buffer is None:
            # Initialize buffer
            self._buffer_read = True
            self._buffer = self._readlines(self._least, [])
        else:
            # Extend buffer
            self._buffer = self._readlines(self._stride, self._buffer, True)

    def get(self) -> Optional[np.ndarray]:
        """Gets the data of the next batch
        """

        self._read_buffer()

        if not self._buffer:
            # There is no data,
            # which indicates that the data has been exhausted
            return

        array = np.array(self._buffer)

        windowed = array if self._window_size == 1 else rolling_window(
            array,
            self._window_size,
            shift=self._window_shift,
            stride=self._window_stride
        )

        batched = windowed if self._batch == 1 else rolling_window(
            windowed,
            self._batch
        )

        return batched[0]

    def reset_buffer(self) -> None:
        self._buffer = None

    def read(
        self,
        amount: int,
        reset_buffer: bool = False
    ) -> list:
        """Reads multiple batches of data

        Args:
            amount (int): number of batches to be read
            reset_buffer (:obj:`bool`, optional): if `True`, the dataset will reset the data of the previous window in the buffer
        """

        if reset_buffer:
            self.reset_buffer()

        array = []

        while amount > 0:
            amount -= 1
            array.append(self.get())

        return array

    def __iter__(self) -> 'Dataset':
        return self

    def __next__(self) -> np.ndarray:
        got = self.get()

        if got is None:
            raise StopIteration

        return got
