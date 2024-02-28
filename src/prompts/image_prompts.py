from src.models.story.character_data import CharacterData
from src.models.story.scene_data import SceneData


def get_character_image_prompt(character: CharacterData) -> str:
    prompt_template = ("A portrait image of a 2D character artwork in classic RPG game in full-body pose on a "
                       "plain white background. {name} is {species} {gender} who is {age} years old. They are a "
                       "{role} and their background is {background}. They were born in {place_of_birth}. They have "
                       "{physical_appearance}. No text. One image only. Front-facing full body pose. Centered. "
                       "No drawings. Anime-style asset.")

    prompt = prompt_template.format(
        name=character.first_name + " " + character.last_name,
        species=character.species,
        gender=character.gender,
        age=character.age,
        role=character.role,
        background=character.background,
        place_of_birth=character.place_of_birth,
        physical_appearance=" and ".join(character.physical_appearance)
    )

    return prompt


def get_scene_image_prompt(scene: SceneData) -> str:
    prompt_template = ("An image of a 2D scene artwork in classic RPG game in full-body landscape scene background. "
                       "This is a scene of {title} located in {location}. The scene is {description}. No text. "
                       "ne image only. Centered. No drawings. Anime-style asset.")

    prompt = prompt_template.format(
        title=scene.title,
        location=scene.location,
        description=scene.description
    )

    return prompt
