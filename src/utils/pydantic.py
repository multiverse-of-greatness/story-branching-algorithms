from pydantic import ValidationError


def map_validation_errors_to_string(e: ValidationError) -> str:
    _str: list[str] = map(lambda error: 
                            (f"{'.'.join(map(str, error['loc']))}\n"
                             f"  {error['msg']} [type={error['type']}, input_value={error['input']}, "
                             f"input_type={type(error['input']).__name__}]"), e.errors())
    return f"{e.error_count()} validation errors found\n{'\n'.join(_str)}"
