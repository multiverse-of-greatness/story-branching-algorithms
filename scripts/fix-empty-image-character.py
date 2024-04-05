import json

from dotenv import load_dotenv

from neo4j import Session
from src.bg_remover.bria import Bria
from src.database import Neo4J
from src.utils.general import get_base64_from_image, get_image_from_base64

bria = Bria()


def fix_empty_image_character(session: Session):
    results = session.run("MATCH (n: StoryData) RETURN n").data()
    for result in results:
        main_characters = json.loads(result.get('n').get('main_characters'))
        for character in main_characters:
            if character.get('original_image') is not None and character.get('image') is None:
                original_image = get_image_from_base64(character.get('original_image'))
                character['image'] = get_base64_from_image(bria.remove_background(original_image))

        session.run("MATCH (n: StoryData {id: $id}) SET n.main_characters = $main_characters",
                    id=result.get('n').get('id'),
                    main_characters=json.dumps(main_characters))


def main():
    neo4j_connector = Neo4J()
    neo4j_connector.with_session(fix_empty_image_character)


if __name__ == '__main__':
    load_dotenv()
    main()
