import json
from pathlib import Path
from time import sleep

from openai import OpenAI, APITimeoutError, APIConnectionError, APIError, RateLimitError

from .utils import parse_json_string, ConversationHistory


def chatgpt(messages: ConversationHistory) -> tuple[str, dict]:
    client = OpenAI(timeout=15)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            seed=42
        )

        chatgpt_path = Path("outputs/chatgpt.json")
        responses = {"responses": []}

        if chatgpt_path.exists():
            with open(chatgpt_path, 'r') as f:
                responses = json.load(f)

        responses['responses'].append(response.choices[0].message.content)

        with open(chatgpt_path, 'w') as f:
            f.write(json.dumps(responses, indent=2))

        content = response.choices[0].message.content
        return content, parse_json_string(response.choices[0].message.content)
    except (ValueError, json.decoder.JSONDecodeError) as e:
        print(f"OpenAI API response could not be decoded as JSON: {e}")
        sleep(3)
        return chatgpt(messages)
    except APITimeoutError as e:
        print(f"OpenAI API request timed out: {e}")
        sleep(3)
        return chatgpt(messages)
    except APIConnectionError as e:
        print(f"OpenAI API request failed to connect: {e}")
        sleep(3)
        return chatgpt(messages)
    except RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        sleep(3)
        return chatgpt(messages)
    except APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        sleep(3)
        return chatgpt(messages)
    except Exception as e:
        print(f"Unexpected error: {e}")
