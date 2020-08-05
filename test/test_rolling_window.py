import numpy as np

from csv_dataset.common import rolling_window


def test_rolling_window_1d():
    expected = np.array([
        np.arange(0, 3),
        np.arange(3, 6),
        np.arange(6, 9),
    ])

    assert np.array_equal(
        rolling_window(
            np.arange(10),
            3
        ), expected
    )

    assert np.array_equal(
        rolling_window(
            np.arange(11),
            3
        ), expected
    )


def test_rolling_window_1d_with_shift():
    expected = np.array([
        [0, 1, 2],
        [1, 2, 3],
        [2, 3, 4]
    ])

    assert np.array_equal(
        rolling_window(
            np.arange(5),
            3,
            shift=1
        ), expected
    )


def test_rolling_window_1d_with_shift_and_stride():
    expected = np.array([
        [0, 2, 4],
        [1, 3, 5],
        [2, 4, 6]
    ])

    assert np.array_equal(
        rolling_window(
            np.arange(7),
            3,
            shift=1,
            stride=2
        ), expected
    )


def test_rolling_window_2d():
    def create(length):
        return rolling_window(
            rolling_window(
                np.arange(length),
                2
            ),
            2
        )

    expected = np.array([
        [
            [0, 1],
            [2, 3]
        ],
        [
            [4, 5],
            [6, 7]
        ]
    ])

    np.testing.assert_array_equal(create(8), expected)
    np.testing.assert_array_equal(create(9), expected)
    np.testing.assert_array_equal(create(10), expected)


def test_rolling_window_2d_with_shift_and_stride():
    def create(length, **kwargs):
        return rolling_window(
            # [
            #     [0, 1],
            #     [2, 3],
            #     [4, 5],
            #     [6, 7]
            # ]
            rolling_window(
                np.arange(length),
                2
            ),
            2,
            **kwargs
        )

    np.testing.assert_array_equal(create(8, shift=1), np.array([
        [
            [0, 1], [2, 3]
        ],
        [
            [2, 3], [4, 5]
        ],
        [
            [4, 5], [6, 7]
        ]
    ]))

    np.testing.assert_array_equal(create(8, shift=1, stride=2), np.array([
        [
            [0, 1], [4, 5]
        ],
        [
            [2, 3], [6, 7]
        ]
    ]))
