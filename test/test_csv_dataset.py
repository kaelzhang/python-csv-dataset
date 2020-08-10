from pathlib import Path
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

    assert len(data) == 5
    assert len(data[0]) == 5

    # while data is not None:
    #     print(data, len(data))
    #     data = dataset.get()
