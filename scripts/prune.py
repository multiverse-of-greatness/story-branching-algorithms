from typing import Annotated

import typer
from dotenv import load_dotenv
from neo4j import Session

from src.databases.neo4j import Neo4JConnector


def prune_story(session: Session, story_id: str):
    session.run('MATCH (sd:StoryData {id: $story_id}) DETACH DELETE sd', story_id=story_id)
    session.run('MATCH (sc:StoryChunk {story_id: $story_id}) DETACH DELETE sc', story_id=story_id)


def main(
        story_id: Annotated[
            str, typer.Option(help="Story ID to prune")
        ]
):
    db = Neo4JConnector()
    db.with_session(prune_story, story_id)
    print(f"Story {story_id} pruned")


if __name__ == '__main__':
    load_dotenv()
    typer.run(main)
