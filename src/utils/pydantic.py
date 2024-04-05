from pydantic import ValidationError


def map_validation_errors_to_string(e: ValidationError) -> str:
    map_input_to_str = lambda x: str(x) if not isinstance(x, str) else f"\"{x}\""
    _str: list[str] = map(lambda error: 
                            (f"{'.'.join(map(str, error['loc']))}\n"
                             f"  {error['msg']} [type={error['type']}, input_value={map_input_to_str(error['input'])}, "
                             f"input_type={type(error['input']).__name__}]"), e.errors())
    return f"{e.error_count()} validation errors found\n{'\n'.join(_str)}"
