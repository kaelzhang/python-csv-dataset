from pathlib import Path
import pytest

from csv_dataset import (
    CsvReader,
    Dataset,
    RangeNormalizer
)

csv_path = Path(Path(__file__).resolve()).parent.parent / \
    'example' / 'stock.csv'


def test_reader_exception():
    with pytest.raises(
        ValueError,
        match='positive'
    ):
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            max_lines=0
        )


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

    assert dataset.lines_need(reads=3) == 19

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

    assert len(list(dataset)) == 19

    dataset.reset()
    assert len(list(dataset)) == 19


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


def test_reader_with_normalizers():
    price_normalizer = RangeNormalizer(0, 10000)
    volume_normalizer = RangeNormalizer(0, 200)

    dataset = Dataset(
        CsvReader(
            csv_path.absolute(),
            float,
            [
                2, 3, 4, 5, 6
            ],
            normalizers=[
                price_normalizer,
                price_normalizer,
                price_normalizer,
                price_normalizer,
                volume_normalizer
            ],
            header=True
        )
    ).batch(5)

    got = dataset.get()

    assert format(got[0][0], '.6f') == '0.714599'
    assert format(got[1][0], '.6f') == '0.714289'

    assert format(
        price_normalizer.restore(got[0][0]),
        '.2f'
    ) == '7145.99'


def test_reader_error():
    with pytest.raises(
        ValueError,
        match='expect 5 but got 2'
    ):
        CsvReader(
            'fake',
            float,
            indexes=[1, 2, 3, 4, 5],
            normalizers=[1, 2]
        )


def test_max_lines():
    reader = CsvReader(
        csv_path.absolute(),
        float,
        [
            2, 3, 4, 5, 6
        ],
        header=True,
        max_lines=5
    )

    data = Dataset(reader)

    assert len(list(data)) == 5

    reader.max_lines = 1
    data.reset()

    assert len(list(data)) == 1


def test_read():
    reader = CsvReader(
        csv_path.absolute(),
        float,
        [
            2, 3, 4, 5, 6
        ],
        header=True
    )

    assert reader.max_lines is None

    data = Dataset(reader).window(2, shift=1)

    assert data.get()[0][0] == 7145.99

    assert reader.lines == 2

    array = data.read(4)
    assert len(array) == 4
    assert array[0][0][0] == 7142.89

    assert reader.lines == 6

    # reset

    data.reset()

    assert data.get()[0][0] == 7145.99

    array = data.read(4, reset_buffer=True)
    assert len(array) == 4
    assert array[0][0][0] == 7125.76

    assert reader.lines == 7


def test_max_reads():
    reader = CsvReader(
        csv_path.absolute(),
        float,
        [
            2, 3, 4, 5, 6
        ],
        header=True
    )

    data = Dataset(reader).window(2, shift=1)

    assert data.max_reads() is None

    with pytest.raises(ValueError, match='positive'):
        data.max_reads(-1)

    assert data.max_reads(1) == 0
    assert data.max_reads(2) == 1
    assert data.max_reads(3) == 2
