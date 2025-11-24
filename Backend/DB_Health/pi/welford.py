from __future__ import annotations

class Welford:
#초기화자
    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0
#데이터 추가 메서드
    def add(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2
#분산 계산
    @property
    def variance(self) -> float:
        return (self.M2 / (self.n - 1)) if self.n > 1 else 0.0
#표준편차 계산
    @property
    def stdev(self) -> float:
        v = self.variance
        return v ** 0.5 if v > 0 else 0.0