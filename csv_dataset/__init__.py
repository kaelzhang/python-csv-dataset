# The first alpha version
__version__ = '0.3.0'

from .reader import (
    AbstractReader,
    CsvReader
)
from .dataset import Dataset
from .normalizer import (
    RangeNormalizer
)
