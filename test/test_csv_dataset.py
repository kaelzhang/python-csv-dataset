from pathlib import Path
import pytest

from csv_dataset import (
    CsvReader,
    Dataset
)

csv_path = Path(Path(__file__).resolve()).parent.parent / \
    'example' / 'stock.csv'


def test_window_and_batch():
    dataset = Dataset(
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            header=True
        )
    ).window(5, 1).batch(5)

    data = dataset.get()

    with pytest.raises(
        RuntimeError,
        match='forbidden'
    ):
        dataset.window(5, 2)

    assert len(data) == 5
    assert len(data[0]) == 5
    assert data[0][0][0] == 7145.99
    assert data[0][1][0] == 7142.89
    assert data[1][0][0] == 7142.89

    data = dataset.get()
    assert data[0][0][0] == 7134.99


def test_iterator():
    dataset = Dataset(
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            header=True
        )
    ).window(5, 1).batch(5)

    all_data = list(dataset)

    assert len(all_data) == 19


def test_direct_get():
    dataset = Dataset(
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            header=True
        )
    )

    got = dataset.get()

    assert got.shape == (5,)

    assert list(got) == [
        7145.99, 7150.0, 7141.01, 7142.33, 21.094283
    ]


def test_window_only():
    dataset = Dataset(
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            header=True
        )
    ).window(5, 1)

    assert dataset.get().shape == (5, 5)


def test_batch_only():
    dataset = Dataset(
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            header=True
        )
    ).batch(5)

    got = dataset.get()

    assert got[0][0] == 7145.99
    assert got[1][0] == 7142.89
