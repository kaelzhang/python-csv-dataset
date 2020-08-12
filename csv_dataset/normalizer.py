from typing import (
    Protocol
)


class NormalizerProtocol(Protocol):
    def normalize(self, value: float) -> float:
        ...  # pragma: no cover

    def restore(self, value: float) -> float:
        ...  # pragma: no cover


class RangeNormalizer:
    def __init__(
        self,
        min_value: float,
        max_value: float
    ):
        self._min = min_value
        self._scale = max_value - min_value

    def normalize(self, value: float) -> float:
        return (value - self._min) / self._scale

    def restore(self, value: float) -> float:
        return value * self._scale + self._min
