import numpy as np

from csv_dataset.common import rolling_window


def test_rolling_window():
    result = rolling_window(
        np.arange(10),
        3
    )

    comparison = result == np.array([
        np.array([0, 1, 2]),
        np.array([3, 4, 5]),
        np.array([6, 7, 8])
    ])

    assert comparison.all()
