import random

JSON_MAGIC_PHRASE = "Return output in JSON format and only the JSON in the Markdown code block. JSON."


# TODO: Define the id system, so that I can trace the branch
# TODO: Add info about chapter in each prompt
# TODO: Randomize/get arguments for number of main characters and places

def plot_prompt(num_endings=3,
                themes=None,
                num_main_characters=None,
                num_main_scenes=None,
                game_genre="visual novel") -> str:
    if themes is None:
        themes = ["sci-fi", "fantasy", "middle-age", "utopia", "mythical creatures", "world scale"]

    if num_main_characters is None:
        num_main_characters = random.randint(3, 7)

    if num_main_scenes is None:
        num_main_scenes = random.randint(1, 5)

    themes_str = ", ".join(themes)
    return f"""Write a game story synopsis. Then generate 1 story beginning, {num_endings} possible endings, {num_main_characters} main characters, and {num_main_scenes} main scenes. {JSON_MAGIC_PHRASE}

# Output format
{{
"title": game title,
"genre": game genre,
"themes": [words],
"main_scenes": [{{"id": id, "title": location name, "location": where is this place, "description": describe location}}].
"main_characters": [{{"id": id, "first_name": first name, "last_name": last name, "species": species, "age": exact age or description, "role": role of the character, "background": background story, "place_of_birth": location, "physical_appearance": [details]}}]
"synopsis": synopsis,
"beginning": beginning of the story,
"endings": [{{"id": id, "ending": ending}}]
}}

# Game information
Game genre: {game_genre}
Themes: {themes_str}"""


def story_until_choices_opportunity_prompt(story_so_far: str, num_choices=3, game_genre="visual novel") -> str:
    return f"""Generate possible narratives and dialogues for a {game_genre} game, culminating in {num_choices} choices that the player can make to influence the course of the story. {JSON_MAGIC_PHRASE}

# Output format
{{
"id": id,
"story_so_far": story so far,
"story": [{{"id": id signifies the order, "speaker": speaker name or -1 for narration, "text": dialogue or narration}}],
"choices": [{{"id": id, "choice": choice, "description": description}}]
}}

# Plot information
{plot_information}

# The story so far
{story_so_far}"""


def story_based_on_selected_choice_prompt(story_so_far: str, selected_choice: str, game_genre="visual novel") -> str:
    return f"""Generate possible narratives and dialogues for a {game_genre} game, based on the selected choice. {JSON_MAGIC_PHRASE}

# Output format
{{
"id": id,
"story_so_far": story so far,
"story": [{{"id": id signifies the order, "speaker": speaker name or -1 for narration, "text": dialogue or narration}}],
"choices": [{{"id": id, "choice": choice, "description": description}}]
}}

# Plot information
{plot_information}

# The story so far
{story_so_far}

# The selected choice
{selected_choice}"""


def story_until_chapter_end_prompt(story_so_far: str, game_genre="visual novel") -> str:
    return f"""Generate possible narratives and dialogues for a {game_genre} game, culminating in the end of the chapter. {JSON_MAGIC_PHRASE}

# Output format
{{
"id": id,
"story_so_far": story so far,
"story": [{{"id": id signifies the order, "speaker": speaker name or -1 for narration, "text": dialogue or narration}}]
}}

# Plot information
{plot_information}

# The story so far
{story_so_far}"""


def story_until_game_end_prompt(story_so_far: str, selected_ending: str, game_genre="visual novel") -> str:
    return f"""Generate possible narratives and dialogues for a {game_genre} game, culminating in the end of the game. {JSON_MAGIC_PHRASE}

# Output format
{{
"id": id,
"story_so_far": story so far,
"story": [{{"id": id signifies the order, "speaker": speaker name or -1 for narration, "text": dialogue or narration}}],
}}

# Plot information
{plot_information}

# The story so far
{story_so_far}

# The selected ending
{selected_ending}"""

# def merge_story_branch_prompt(story_so_far: str, story_branches: list[str], game_genre="visual novel") -> str:
#     story_branches_str = ""
#
#     for i, story_branch in enumerate(story_branches):
#         story_branches_str += f"# Story branch {i + 1}\n{story_branch}\n\n"
#
#     return f"""Merge story branches together. {JSON_MAGIC_PHRASE}
#
# # Output format
# {{
# "id": id,
# "story_so_far": story so far,
# "story": [{{"id": id signifies the order, "speaker": speaker name or -1 for narration, "text": dialogue or narration}}],
# }}
#
# # The story so far
# {story_so_far}
#
# # The story branches
# {story_branches_str}"""
