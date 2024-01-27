import json
from pathlib import Path
from time import sleep

from openai import OpenAI, Timeout, APIConnectionError, APIError, RateLimitError
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam

type ConversationHistory = list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                                ChatCompletionAssistantMessageParam]


def chatgpt(messages: ConversationHistory) -> str:
    client = OpenAI(timeout=60)
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

        return response.choices[0].message.content
    except Timeout as e:
        print(f"OpenAI API request timed out: {e}")
        sleep(3)
        return chatgpt(messages)
    except APIConnectionError as e:
        print(f"OpenAI API request failed to connect: {e}")
        sleep(3)
        return chatgpt(messages)
    except APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        sleep(3)
        return chatgpt(messages)
    except RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        sleep(3)
        return chatgpt(messages)
    except Exception as e:
        print(f"Unexpected error: {e}")
