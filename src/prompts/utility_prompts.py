from src.prompts.story_prompts import JSON_MAGIC_PHRASE


def get_fix_invalid_json_prompt(old_response: str, error_msg: str) -> str:
    return f"""Fix the following incorrect JSON data. Correct the syntax and provide new values if needed. Continue the generation if you found that the original is incomplete. The original message is provided between === and ===. {JSON_MAGIC_PHRASE}

# Error message
{error_msg}

# Original (Invalid JSON)
===
{old_response}
===

# Fixed (Corrected JSON)
"""
