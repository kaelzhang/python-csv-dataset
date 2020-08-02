import numpy as np

from csv_dataset.common import rolling_window


def test_rolling_window():
    result = rolling_window(
        np.arange(10),
        3
    )

    print(result)
