from typing import (
    Optional,
    TypeVar,
    Generic
)

import numpy as np

from common_decorators import lazy

from .reader import AbstractReader
from .common import rolling_window

T = TypeVar('T')


class Dataset(Generic[T]):
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
        """The list size of the underlying datum referred to a single window
        """

        return (self._window_size - 1) * self._window_stride + 1

    @lazy
    def _single_step(self) -> int:
        """stride without considering the batch size
        """
        return self._window_shift * self._window_stride

    @lazy
    def _least(self) -> int:
        return self._single_least + (self._batch - 1) * self._single_step

    @lazy
    def _step(self) -> int:
        return self._batch * self._single_step

    def _check_start(self, method_name: str):
        if self._buffer_read:
            raise RuntimeError(f'calling {method_name}() during reading is forbidden')

    def window(
        self,
        window_size: int,
        shift: Optional[int] = None,
        stride: int = 1
    ) -> 'Dataset':
        """Combines (nests of) input elements into a dataset of (nests of) windows.
        """

        self._check_start('window')

        self._window_size = window_size
        self._window_shift = shift or window_size
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

    # def restore(
    #     self,
    #     data: np.ndarray
    # ) -> np.ndarray:
    #     ...

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
            self._buffer = self._readlines(self._step, self._buffer, True)

    def get(self) -> Optional[np.ndarray]:
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

    def read(
        self,
        amount: int,
        reset_buffer: bool = False
    ) -> list:
        if reset_buffer:
            self._buffer = None

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
