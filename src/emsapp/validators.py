from collections import defaultdict
from emsapp.const import ALL_COLUMNS, DISTRICTS
from emsapp.i18n import _

valid_values: dict[str, dict[str]] = defaultdict(dict)


def district_validator(s: str) -> str:
    if s.title() in DISTRICTS:
        return s.title()
    raise ValueError(
        _("{s} does not appear in {district_list!r}").format(s=s, district_list=DISTRICTS)
    )


def column_validator(s: str):
    if s not in ALL_COLUMNS:
        raise ValueError(f"{s} is not a valid column. Possible values : {ALL_COLUMNS!r}")
    return s


def register_valid(key: str, value: str, *other_valid: str):
    """register a valid value for a corresponding key

    Parameters
    ----------
    key : str
        to what the value corresponds
    value : str
        the new correct value to consider
    *other_valid : str
        any other str that corresponds to the same value.

    Example
    -------
    ```
    register_valid("district", "Glâne", "glane", "Glane")
    print(validate("district", "glane"))
    # prints Glâne
    ```
    """
    for val in (value, *other_valid):
        valid_values[key][val] = value


def validate(key: str, value: str) -> str:
    if value not in valid_values[key]:
        raise ValueError(
            f"{value} is not valid. Possible values : {list(valid_values[key].keys())!r}"
        )
    return valid_values[key][value]
