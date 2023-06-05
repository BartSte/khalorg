import re
from dataclasses import dataclass


def remove_timestamps(text: str) -> str:
    """
    Removes active range timestamps from `text` that are not inline with the
    text. If a timestamp is the only entity on a line, it will be removed.

    If a line only contains a time stamp and spaces, the whole line is
    deleted. If it is surrounded by characters, it is only removed.

    Args:
    ----
        text: str containing time stamps

    Returns:
    -------
        text without active ranr timestamps

    """
    '^(?:\\s*<foo>\\s*)+$'
    result: str = text
    head: str = r'(^|\n)\s*'
    tail: str = r'\s*(\n|$)'
    timestamps: str = (
        f'(?:{OrgRegex.timestamp_long})|'
        f'(?:{OrgRegex.timestamp_short})|'
        f'(?:{OrgRegex.timestamp_short_alt})|'
        f'(?:{OrgRegex.timestamp})'
    )
    regex: str = f'({head}{timestamps}{tail})+'
    result: str = re.sub(regex, '', result)

    # Remove indent first line.
    result = re.sub(r'^\s+', '', result)

    return result


def get_indent(text: str, piece: str) -> list:
    """
    Returns the indent for a `piece` of `text`. If `piece` is found multiple
    times, the returned list has a length that is larger than one.

    Args:
    ----
        text: the text
        piece: the str that needs to be found.

    Returns:
    -------
        the indents that belong to the matches.

    """
    return re.findall(rf'^(\s+){piece}', text, re.MULTILINE)


@dataclass
class OrgRegex:
    """ Regex used for org timestamps. """

    day: str = '[A-Z]{1}[a-z]{2}'
    time: str = '[0-9]{2}:[0-9]{2}'
    date: str = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    repeater: str = '[-+]{1,2}[0-9]+[a-z]+'
    timestamp: str = f'<{date}( {day})?( {time})?( {repeater})?>'
    timestamp_short: str = f'<{date}( {day})? {time}--{time}( {repeater})?>'
    timestamp_short_alt: str = f'<{date}( {day})? {time}-{time}( {repeater})?>'
    timestamp_long: str = f'{timestamp}--{timestamp}'
