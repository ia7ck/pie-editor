# -*- encoding: utf-8 -*-

import re


# return -1 if not found
# return first line number (>=1) error occurred
def get_error_line(text):
    if not ("error" in text):
        return -1
    m = re.search(r"asir_where,(.*)\]\]\)", text)
    if m == None:  # match しなかった
        return -1
    errors = m.group(1)
    error_line_numbers = [
        n for n in list(map(int, re.findall(r"\d+", errors))) if n >= 1
    ]
    if len(error_line_numbers) == 0:
        return -1
    return min(error_line_numbers)


"""
def g() {
    h();
}
def f() { 
    g();
} 
f();
"""

if __name__ == "__main__":
    assert (
        get_error_line(
            "error([7,4294967295,evalf : h undefined,[asir_where,[[toplevel,7],[string,f,5],[string,g,2],[,end,0]]]])"
        )
        == 2
    )
