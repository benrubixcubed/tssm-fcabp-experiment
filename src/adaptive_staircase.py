from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class AdaptiveStaircase:
    initial_ambiguity: float = 0.45
    min_ambiguity: float = 0.05
    max_ambiguity: float = 0.95
    initial_step: float = 0.08
    min_step: float = 0.01
    target_accuracy: float = 0.75

    current_ambiguity: float = field(init=False)
    consecutive_correct: int = field(default=0, init=False)
    reversals: int = field(default=0, init=False)
    last_direction: int = field(default=0, init=False)
    history: List[dict] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.current_ambiguity = float(np.clip(self.initial_ambiguity, self.min_ambiguity, self.max_ambiguity))

    def step_size(self) -> float:
        return max(self.min_step, self.initial_step / (1.0 + 0.5 * self.reversals))

    def update(self, is_correct: bool) -> float:
        direction = 0
        s = self.step_size()

        if is_correct:
            self.consecutive_correct += 1
            if self.consecutive_correct >= 2:
                direction = 1
                self.current_ambiguity += s
                self.consecutive_correct = 0
        else:
            self.consecutive_correct = 0
            direction = -1
            self.current_ambiguity -= s * (self.target_accuracy / (1.0 - self.target_accuracy)) * 0.5

        if direction != 0:
            if self.last_direction != 0 and direction != self.last_direction:
                self.reversals += 1
            self.last_direction = direction

        self.current_ambiguity = float(np.clip(self.current_ambiguity, self.min_ambiguity, self.max_ambiguity))
        self.history.append({
            "is_correct": bool(is_correct),
            "ambiguity": self.current_ambiguity,
            "reversals": self.reversals,
            "step_size": s,
        })
        return self.current_ambiguity
      
