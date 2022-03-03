from typing import List


def identifier_to_segments(text: str) -> List[str]:
    # kebab case heruestic
    if "-" in text:
        parts = text.split("-")
    # snake case heurestic
    elif "_" in text:
        parts = text.split("_")
    # camel case probably
    else:
        parts = []
        current_word = []
        for idx, letter in enumerate(text):
            if letter.isupper() and idx > 0 and text[idx - 1].islower():
                parts.append("".join(current_word))
                current_word = []
            current_word.append(letter.lower())
        if current_word:
            parts.append("".join(current_word))
    if len(parts) == 0:
        parts = [text]
    return parts


def to_snake_case(text: str):
    return "_".join(identifier_to_segments(text))


def to_upper_camel_case(text: str):
    segments = identifier_to_segments(text)
    for i in range(len(segments)):
        segments[i] = segments[i][0].upper() + segments[i][1:].lower()
    return "".join(segments)
