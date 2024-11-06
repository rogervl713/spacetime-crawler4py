"""
Assignment 1: Text Processing - Part A: Word Frequencies
"""

import sys
from typing import Dict, Iterator, Optional

def tokenize(text: str) -> Iterator[str]:
    current_token = []
    for ch in text:
        if ch.isalnum():
            current_token.append(ch)
        elif current_token:
            yield ''.join(current_token).lower()
    if current_token:
        yield ''.join(current_token).lower()

def compute_word_frequencies(tokens: Iterator[str]) -> Dict:
    frequencies = {}
    for token in tokens:
        frequencies[token] = frequencies.get(token, 0) + 1
    return dict(sorted(frequencies.items(), key=lambda item:(-item[1], item[0])))

def print_frequencies(frequencies: Dict, delimiter_key: Optional[str] = 'tab') -> None:
    format_options = {
        'tab': '\t',
        'space': ' ',
        'dash': ' - ',
        'equal': ' = ',
        'greater': ' > ',
        'arrow': ' -> ',
        'double_arrow': ' => ',
    }

    delimiter = format_options.get(delimiter_key, '\t')

    for token, freq in frequencies.items():
        print(f"{token}{delimiter}{freq}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 PartA.py <text_file>")
        sys.exit(1)

    TEXT = ""
    DELIMITER_KEY = ""

    text_tokens = tokenize(text=TEXT)
    text_freqs = compute_word_frequencies(text_tokens)
    print_frequencies(text_freqs, delimiter_key=DELIMITER_KEY)
