"""
Assignment 1: Text Processing - Part B: Intersection of Two Files
"""

import sys

import PartA as A

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 PartB <text_file_1> <text_file_2>")
        sys.exit(1)

    text_file_1 = sys.argv[1]
    text_file_2 = sys.argv[2]

    """
    Runtime Complexity: O(n + m)
    - n: number of tokens in file1
    - tokenize file1: O(n)
    - m: number of tokens in file2
    - tokenize file2: O(m)
    - set conversion: O(1)
    - set intersection: O(min(len(file1_tokens), len(file2_tokens)))
    """

    file1_tokens = A.tokenize(text_file_1)
    file2_tokens = A.tokenize(text_file_2)
    common_tokens = set(file1_tokens) & set(file2_tokens)
    print(len(common_tokens))
