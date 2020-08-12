from typing import (
    Optional,
    # Callable,
    List,
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
        # self._header = header
        # self._column_types = column_types
        self._line_pointer = 0

        # self._mapper = default_mapper
        self._batch = 1

        self._window_size = 1
        self._window_shift = 1
        self._window_stride = 1
        self._window_drop_remainder = False

    def reset(self) -> None:
        self._line_pointer = 0
        self._reader.reset()
        self._buffer = self._init_buffer()

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

    @lazy
    def _buffer(self):
        return self._init_buffer()

    def _init_buffer(self) -> List[List[T]]:
        return self._readlines(self._least, [])

    def _check_start(self, method_name: str):
        if self._line_pointer != 0:
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
            self._line_pointer += 1
            read += 1

        if slice_size:
            dest_buffer = dest_buffer[lines:]

        return dest_buffer

    def get(self) -> Optional[np.ndarray]:
        buffer = self._buffer

        if not buffer:
            # There is no data
            return

        array = np.array(buffer)

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

        self._buffer = self._readlines(self._step, buffer, True)

        return batched[0]

    def __iter__(self) -> 'Dataset':
        return self

    def __next__(self) -> np.ndarray:
        got = self.get()

        if got is None:
            raise StopIteration

        return got
