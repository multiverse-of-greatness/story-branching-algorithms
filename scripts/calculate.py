import json
from datetime import datetime
from pathlib import Path

import typer
from dotenv import load_dotenv

app = typer.Typer()


@app.command()
def cost_per_story(story_id: str):
    files = list((Path("outputs") / story_id).glob("*.json"))
    model_name = None
    responses_path = None
    for file in files:
        if file.stem not in ["context", "histories", "plot"]:
            responses_path = file
            model_name = file.stem
            break

    plot_path = Path("outputs") / story_id / "plot.json"
    context_path = Path("outputs") / story_id / "context.json"
    with open(responses_path, "r") as f:
        responses = json.load(f)
    with open(plot_path, "r") as f:
        plot = json.load(f)
    with open(context_path, "r") as f:
        context = json.load(f)

    prompt_tokens = responses["prompt_tokens"]
    completion_tokens = responses["completion_tokens"]

    LLM_PRICES = {
        'claude-3-opus-20240229': {
            "prompt": 15 / 10e5,
            "completion": 75 / 10e5
        },
        "claude-3-sonnet-20240229": {
            "prompt": 3 / 10e5,
            "completion": 15 / 10e5
        },
        "claude-2.1": {
            "prompt": 8 / 10e5,
            "completion": 24 / 10e5
        },
        'gemini-1.0-pro': {
            "prompt": 0 / 10e5,
            "completion": 0 / 10e5
        },
        'gpt-3.5-turbo-0125': {
            "prompt": 0.5 / 10e5,
            "completion": 1.5 / 10e5
        },
        'gpt-4-0125-preview': {
            "prompt": 10 / 10e5,
            "completion": 30 / 10e5
        }
    }

    print(f"LLM: {model_name}")

    prompt_token_price = LLM_PRICES[model_name]["prompt"]
    completion_token_price = LLM_PRICES[model_name]["completion"]

    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Completion tokens: {completion_tokens}")
    print(f"Total tokens: {prompt_tokens + completion_tokens}")

    prompt_cost = prompt_tokens * prompt_token_price
    completion_cost = completion_tokens * completion_token_price
    total_cost = prompt_cost + completion_cost

    print(f"Prompt cost: ${prompt_cost:.2f}")
    print(f"Completion cost: ${completion_cost:.2f}")
    print(f"Total cost: ${total_cost:.2f}")

    if context['image_generation_model'] == "DALL·E 3":
        price_per_character_image = 0.080
        price_per_scene_image = 0.120
    else:
        price_per_character_image = 0
        price_per_scene_image = 0

    print(f"Image generation model: {context['image_generation_model']}")

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
