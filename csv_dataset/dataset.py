from typing import (
    Optional
)

SPLITTER = ','


class CsvDataset:
    def __init__(
        self,
        filepath,
        column_types,
        header: bool = False
    ):
        self._fd = open(filepath, 'r')
        self._header = header
        self._column_types = column_types
        self._counter_line = 0

        self._mapper = None
        self._batch = 1

        self._window_size = 1
        self._window_shift = None
        self._window_stride = 1
        self._window_drop_remainder = False

    def map_series(
        self,
        mapper
    ) -> 'CsvDataset':
        """Maps `mapper` across each series record of the csv
        """
        self._mapper = mapper

        return self

    def batch(
        self,
        batch: int
    ) -> 'CsvDataset':
        """Combines consecutive elements of this dataset into batches.
        """

        self._batch = batch

        return self

    def window(
        self,
        window_size: int,
        shift: Optional[int] = None,
        stride: int = 1,
        drop_remainder: bool = False
    ) -> 'CsvDataset':
        """Combines (nests of) input elements into a dataset of (nests of) windows.
        """

        self._window_size = window_size
        self._window_shift = shift
        self._window_stride = stride
        self._drop_remainder = drop_remainder

        return self

    def get(self):
        if self._header and self._counter_line == 0:
            line = self._fd.readline()

        self._counter_line += 1

        line = self._fd.readline()

        return [
            self._column_types[i](cell)
            for i, cell in enumerate(line.split(SPLITTER))
        ]


from pathlib import Path

csv_path = Path(Path(__file__).resolve()).parent.parent.parent / \
    'ostai-compton' / 'ostai' / 'data' / 'binance_1m_2019-12-20 00:00:00.csv'


dataset = CsvDataset(
    csv_path.absolute(),
    [
        int,
        int,
        float, float, float, float, float,
        int,
        float, float, float, float
    ],
    header=True
)

print(dataset.get())
print(dataset.get())

# f = open(csv_path.absolute(), 'r')

# lines = f.readlines()

# print(lines)

# for line in lines:
#     print(line)
