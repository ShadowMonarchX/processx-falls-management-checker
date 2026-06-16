import re


# This file defines helper functions for text normalization and phrase matching, which are used throughout the application to process and analyze resident notes and policy rules.
# The normalize_text function standardizes the input text by removing extra whitespace and converting it to lowercase, while the contains_any function checks if any of the specified phrases are present in the normalized text.
# These helpers help ensure consistent text processing and improve the accuracy of phrase matching in the application.
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def contains_any(text: str, phrases: list[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(phrase) in normalized for phrase in phrases)
