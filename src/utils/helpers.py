import random


def shuffle_list(items: list) -> list:
    result = items[:]
    random.shuffle(result)
    return result


def normalize_answer(text: str) -> str:
    return text.strip().lower()


def answers_match(user_answer: str, correct_answer: str) -> bool:
    return normalize_answer(user_answer) == normalize_answer(correct_answer)
