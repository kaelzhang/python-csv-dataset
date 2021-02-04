[![](https://travis-ci.org/kaelzhang/python-csv-dataset.svg?branch=master)](https://travis-ci.org/kaelzhang/python-csv-dataset)
[![](https://codecov.io/gh/kaelzhang/python-csv-dataset/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-csv-dataset)
[![](https://img.shields.io/pypi/v/csv-dataset.svg)](https://pypi.org/project/csv-dataset/)
[![](https://img.shields.io/pypi/l/csv-dataset.svg)](https://github.com/kaelzhang/python-csv-dataset)

# csv-dataset

`CsvDataset` helps to read a csv file and create descriptive and efficient input pipelines for deep learning.

`CsvDataset` iterates the records of the csv file in a streaming fashion, so the full dataset does not need to fit into memory.

## Install

```sh
$ pip install csv-dataset
```

## Usage

Suppose we have a csv file whose absolute path is `filepath`:

```csv
open_time,open,high,low,close,volume
1576771200000,7145.99,7150.0,7141.01,7142.33,21.094283
1576771260000,7142.89,7142.99,7120.7,7125.73,118.279931
1576771320000,7125.76,7134.46,7123.12,7123.12,41.03628
1576771380000,7123.74,7128.06,7117.12,7126.57,39.885367
1576771440000,7127.34,7137.84,7126.71,7134.99,25.138154
1576771500000,7134.99,7144.13,7132.84,7141.64,26.467308
...
```

```py
from csv_dataset import (
    Dataset,
    CsvReader
)

dataset = CsvDataset(
    CsvReader(
        filepath,
        float,
        # Abandon the first column and only pick the following
        indexes=[1, 2, 3, 4, 5],
        header=True
    )
).window(3, 1).batch(2)

for element in dataset:
    print(element)
```

The following output shows one print.

```sh
[[[7145.99,  7150.0,   7141.01,  7142.33,   21.094283]
  [7142.89,  7142.99,  7120.7,   7125.73,  118.279931]
  [7125.76,  7134.46,  7123.12,  7123.12,   41.03628 ]]

 [[7142.89,  7142.99,  7120.7,   7125.73,  118.279931]
  [7125.76,  7134.46,  7123.12,  7123.12,   41.03628 ]
  [7123.74,  7128.06,  7117.12,  7126.57,   39.885367]]]

...
```

### Dataset(reader: AbstractReader)

#### dataset.window(size: int, shift: int = None, stride: int = 1) -> self

Defines the window size, shift and stride.

The default window size is `1` which means the dataset has no window.

**Parameter explanation**

Suppose we have a raw data set

```
[ 1  2  3  4  5  6  7  8  9 ... ]
```

And the following is a window of `(size=4, shift=3, stride=2)`

```
  |-------------- size:4 --------------|
  |- stride:2 -|                       |
  |            |                       |
[ 1            3           5           7  ] --------|-----
                                               shift:3
[ 4            6           8           10 ] --------|-----

[ 7            9           11          13 ]

...
```

#### dataset.batch(batch: int) -> self

Defines batch size.

The default batch size of the dataset is `1` which means it is single-batch

#### dataset.get() -> Optional[np.ndarray]

Gets the data of the next batch

#### dataset.reset() -> self

Resets dataset

#### dataset.read(amount: int, reset_buffer: bool = False)

- **amount** the maximum length of data the dataset will read
- **reset_buffer** if `True`, the dataset will reset the data of the previous window in the buffer

Reads multiple batches at a time

If we `reset_buffer`, then the next read will not use existing data in the buffer, and the result will have no overlap with the last read.

### CsvReader(filepath, dtype, indexes, **kwargs)

- **filepath** `str` absolute path of the csv file
- **dtype** `Callable` data type. We should only use `float` or `int` for this argument.
- **indexes** `List[int]` column indexes to pick from the lines of the csv file
- **kwargs**
    - **header** `bool = False` whether we should skip reading the header line.
    - **splitter** `str = ','` the column splitter of the csv file
    - **normalizer** `List[NormalizerProtocol]` list of normalizer to normalize each column of data. A `NormalizerProtocol` should contains two methods, `normalize(float) -> float` to normalize the given datum and `restore(float) -> float` to restore the normalized datum.
    - **max_lines** `int = -1` max lines of the csv file to be read. Defaults to `-1` which means no limit.

#### csvReader.reset()

Resets reader pos

#### csvReader.max_lines(lines: int)

Changes `max_lines`

#### csvReader.readline() -> list

Returns the converted value of the next line

#### property csvReader.lines

Returns number of lines has been read

## License

[MIT](LICENSE)
