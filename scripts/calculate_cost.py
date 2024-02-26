import json
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

app = typer.Typer()


@app.command()
def calculate_cost_per_story(story_id: str):
    input_path = Path("outputs") / story_id / f"{os.getenv('GENERATION_MODEL')}.json"
    with open(input_path, "r") as f:
        responses = json.load(f)
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


@app.command()
def calculate_time_to_completion(story_id: str):
    input_path = Path("outputs") / story_id / "context.json"
    with open(input_path, "r") as f:
        context = json.load(f)
    created_at = context["created_at"]
    updated_at = context["updated_at"]
    completed_at = context["completed_at"]

    print(f"Created at: {created_at}")
    print(f"Updated at: {updated_at}")
    print(f"Completed at: {completed_at}")

    if completed_at is not None:
        time_to_completion = completed_at - created_at
        print(f"Time to completion: {time_to_completion}")
    else:
        time_to_last_update = updated_at - created_at
        print(f"Time to last update: {time_to_last_update}")


if __name__ == "__main__":
    load_dotenv()
    app()
