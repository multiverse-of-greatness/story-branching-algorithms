from datetime import datetime
import json
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

app = typer.Typer()


@app.command()
def cost_per_story(story_id: str):
    responses_path = Path("outputs") / story_id / f"{os.getenv('GENERATION_MODEL')}.json"
    plot_path = Path("outputs") / story_id / "plot.json"
    with open(responses_path, "r") as f:
        responses = json.load(f)
    with open(plot_path, "r") as f:
        plot = json.load(f)
    prompt_tokens = responses["prompt_tokens"]
    completion_tokens = responses["completion_tokens"]

    prompt_token_price = 0.0005 / 1000
    completion_token_price = 0.0015 / 1000

    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Completion tokens: {completion_tokens}")
    print(f"Total tokens: {prompt_tokens + completion_tokens}")

    prompt_cost = prompt_tokens * prompt_token_price
    completion_cost = completion_tokens * completion_token_price
    total_cost = prompt_cost + completion_cost

    print(f"Prompt cost: ${prompt_cost:.2f}")
    print(f"Completion cost: ${completion_cost:.2f}")
    print(f"Total cost: ${total_cost:.2f}")

    price_per_character_image = 0.080
    price_per_scene_image = 0.120

    num_characters = len(plot["parsed"]["main_characters"])
    num_scenes = len(plot["parsed"]["main_scenes"])

    character_images_cost = num_characters * price_per_character_image
    scene_images_cost = num_scenes * price_per_scene_image

    print(f"Character images cost: ${character_images_cost:.2f}")
    print(f"Scene images cost: ${scene_images_cost:.2f}")

    total_cost += character_images_cost + scene_images_cost
    print(f"Total cost (including images): ${total_cost:.2f}")


@app.command()
def time_to_completion(story_id: str):
    input_path = Path("outputs") / story_id / "context.json"
    with open(input_path, "r") as f:
        context = json.load(f)
    created_at = datetime.fromisoformat(context["created_at"])
    updated_at = datetime.fromisoformat(context["updated_at"])
    completed_at = datetime.fromisoformat(context["completed_at"])

    print(f"Created at: {created_at}")
    print(f"Updated at: {updated_at}")
    print(f"Completed at: {completed_at}")

    if completed_at is not None:
        time_to_completion = completed_at - created_at
        hour, remainder = divmod(time_to_completion.seconds, 3600)
        minute, second = divmod(remainder, 60)
        print(f"Time to completion: {hour} hours, {minute} minutes, {second} seconds")
    else:
        time_to_last_update = updated_at - created_at
        hour, remainder = divmod(time_to_last_update.seconds, 3600)
        minute, second = divmod(remainder, 60)
        print(f"Time to last update: {hour} hours, {minute} minutes, {second} seconds")

if __name__ == "__main__":
    load_dotenv()
    app()
