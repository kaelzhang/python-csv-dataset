from typing import (
    Optional
)

import numpy as np


def rolling_window(
    array: np.ndarray,
    size: int,
    shift: Optional[int] = None,
    stride: int = 1
) -> np.ndarray:
    """Gets an `size`-period rolling window for `array` as an 1d array

    |-------- size:3 --------|
    |- stride:1 -|           |
    |            |           |
    1            2           3 --------|---
                                    shift:2
    3            4           5 --------|---

    5            6           7
    """

    shift = shift or size

    window_step = shift * stride

    step_length = len(array) - size
    steps = step_length // window_step
    rest = step_length - window_step * steps

    steps += 1

    if rest:
        # drop the last window
        # if its size is smaller than `size`.
        array = array[:-rest]

    item_stride = array.strides[0]

    ret = np.lib.stride_tricks.as_strided(
        array,
        # rolling_window "destroy" the first dimension of input `array`,
        shape=(steps, size) + array.shape[1:],
        strides=(item_stride * shift, item_stride * stride) + array.strides[1:]
    )

    return ret


def max_lines_error(max_lines):
    return ValueError(
        f'max_lines must be positive, but got `{max_lines}`'
    )
