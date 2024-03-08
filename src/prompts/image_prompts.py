from src.models.story.character_data import CharacterData
from src.models.story.scene_data import SceneData


def get_negative_image_prompt() -> str:
    return ("multiple people, poorly Rendered face, poorly drawn face, poor facial details, poorly drawn hands, "
            "poorly rendered hands, low resolution, blurry image, oversaturated, bad anatomy, signature, watermark, "
            "username, error, out of frame, extra fingers, mutated hands, poorly drawn hands, malformed limbs, "
            "missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, "
            "long neck, bad face, text, realistic")


def get_character_image_prompt(character: CharacterData) -> str:
    prompt_template = (
        "A close-up face portrait image game asset of a 2D character artwork in a classic RPG game on "
        "a plain white background. {name} is a {gender} {species} who is {age} years old. "
        "They have {physical_appearance}. No text. One image only. Front face only. Centered. No drawings. "
        "Anime-style asset. Detailed face.")

    prompt = prompt_template.format(
        name=character.first_name + " " + character.last_name,
        species=character.species,
        gender=character.gender,
        age=character.age,
        physical_appearance=" and ".join(character.physical_appearance)
    )

    return prompt


def get_scene_image_prompt(scene: SceneData) -> str:
    prompt_template = (
        "An image of a 2D scene artwork in a classic RPG game with a landscape scene background. "
        "This is a scene of {title} located in {location}. The scene is {description}. No text. "
        "One image only. Centered. No drawings. Anime-style asset.")

    prompt = prompt_template.format(
        title=scene.title,
        location=scene.location,
        description=scene.description
    )

    return prompt
