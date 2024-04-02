from enum import Enum


class GenerationApproach(str, Enum):
    BASELINE = "baseline"
    PROPOSED = "proposed"
