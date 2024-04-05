from enum import Enum


class BranchingType(str, Enum):
    BRANCHING = "branching"
    CHAPTER_END = "chapter_end"
    GAME_END = "game_end"
