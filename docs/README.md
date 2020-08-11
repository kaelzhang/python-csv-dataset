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

## License

[MIT](LICENSE)
