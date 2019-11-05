# -*- encoding: utf-8 -*-

import re


# return -1 if not found
# return first line number (>=1) error occurred
def get_error_line(text):
    if not ("error" in text):
        return -1
    m = re.search(r"asir_where,(.*)\]\]\)", text)
    if m is None:  # match しなかった
        return -1
    errors = m.group(1)
    error_line_numbers = [
        n for n in list(map(int, re.findall(r"\d+", errors))) if n >= 1
    ]
    if len(error_line_numbers) == 0:
        return -1
    return min(error_line_numbers)
