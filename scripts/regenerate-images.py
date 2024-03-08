import json
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

from src.bg_remover.bria import Bria
from src.databases.neo4j import Neo4JConnector
from src.models.story.character_data import CharacterData
from src.models.story.scene_data import SceneData
from src.prompts.image_prompts import get_character_image_prompt, get_scene_image_prompt
from src.utils.general import get_image_from_base64, get_base64_from_image
from src.utils.generative_models import get_image_generation_model

bria = Bria()

app = typer.Typer()


def _run_regenerate_images(session, story_id: str, for_characters: bool, for_scenes: bool):
    img_gen = get_image_generation_model(os.getenv('IMAGE_GENERATION_MODEL'))
    result = session.run("MATCH (n: StoryData {id: $story_id}) RETURN n LIMIT 1", story_id=story_id).data()[0]
    if for_characters:
        main_characters = json.loads(result.get('n').get('main_characters'))
        for character in main_characters:
            character_data = CharacterData.from_json(character)
            prompt = get_character_image_prompt(character_data)
            image = img_gen.generate_image_from_text_prompt(prompt)
            character['original_image'] = image
            image_b64 = get_image_from_base64(image)
            character['image'] = get_base64_from_image(bria.remove_background(image_b64))

        session.run("MATCH (n: StoryData {id: $id}) SET n.main_characters = $main_characters",
                    id=result.get('n').get('id'),
                    main_characters=json.dumps(main_characters))

    if for_scenes:
        main_scenes = json.loads(result.get('n').get('main_scenes'))
        for scene in main_scenes:
            scene_data = SceneData.from_json(scene)
            prompt = get_scene_image_prompt(scene_data)
            image = img_gen.generate_image_from_text_prompt(prompt)
            scene['image'] = image

        session.run("MATCH (n: StoryData {id: $id}) SET n.main_scenes = $main_scenes",
                    id=result.get('n').get('id'),
                    main_scenes=json.dumps(main_scenes))

    context_file = Path("../outputs") / result.get('n').get('approach') / result.get('n').get('id') / "context.json"
    with open(context_file, 'r') as file:
        context = json.load(file)
        context['image_generation_model'] = str(img_gen)
    with open(context_file, 'w') as file:
        json.dump(context, file, indent=2)


@app.command()
def regenerate_images(story_id: str, for_characters: bool = False, for_scenes: bool = False):
    neo4j_connector = Neo4JConnector()
    neo4j_connector.with_session(lambda session: _run_regenerate_images(session, story_id, for_characters, for_scenes))


if __name__ == '__main__':
    load_dotenv()
    app()
