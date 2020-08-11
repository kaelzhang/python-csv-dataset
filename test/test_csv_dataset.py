from pathlib import Path
import pytest

from csv_dataset import (
    CsvReader,
    Dataset
)

csv_path = Path(Path(__file__).resolve()).parent.parent / \
    'example' / 'stock.csv'


def test_main():
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
