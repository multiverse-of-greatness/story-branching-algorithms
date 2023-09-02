from src.prompts import plot_prompt


def initiate_story() -> str:
    return ""


def generate_story_chunk() -> str:
    return ""


def generate_game_story(game_genre: str = 'JRPG', themes=None, num_chapters=3) -> str:
    history = []
    return plot_prompt(num_endings=3, themes=themes, game_genre=game_genre)


def main():
    print(generate_game_story())


if __name__ == '__main__':
    main()

# TODO: Add logging and raw output saving and printing
# TODO: Make it resumable
"""
Information needed
1. Genre
2. Theme
3. Character
4. Story
- How many chapters
- How many endings
- Number of choices at each opportunity (random) (depth)
---
- Randomly introduced branch merging
- Automatically summarize story so far in case the token limit exceed
- Randomly connect ending with branch when at the last chapter and last choice
- Randomly decide number of choice opportunities

MAX_DEPTH= 3
MAX_NUM_CHOICES = 3
MIN_NUM_CHOICES = 2
MAX_NUM_CHOICES_OPPORTUNITY = 5 // per chapter
MIN_NUM_CHOICES_OPPORTUNITY = 3 // per chapter
"""
