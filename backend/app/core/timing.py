import time
from dataclasses import dataclass, field

def now_ms() -> float:
    return time.perf_counter() * 1000.0

@dataclass
class Timings:
    t0: float = field(default_factory=now_ms)
    marks: dict[str, float] = field(default_factory=dict)

    def mark(self, name: str) -> None:
        self.marks[name] = now_ms()

    def elapsed_ms(self, name: str) -> float:
        t = self.marks.get(name)
        if t is None:
            return -1.0
        return t - self.t0

    def span_ms(self, start: str, end: str) -> float:
        a = self.marks.get(start)
        b = self.marks.get(end)
        if a is None or b is None:
            return -1.0
        return b - a

    def to_dict_ms(self) -> dict:
        return {k: round(v - self.t0, 1) for k, v in self.marks.items()}