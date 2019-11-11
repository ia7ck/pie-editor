# -*- encoding: utf-8 -*-

import os
import re


# エラーがなければ -1 を返す
# エラーがあればエラーが起きた最初の行番号を返す
def find_error_line(text):
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

def find_imagefile_path(text):
    if not (".png" in text):
        return ""
    path_list = text.lstrip("[").rstrip("]").split(",")
    path = ""
    for p in path_list:
        root_ext = os.path.splitext(p)
        if root_ext[1] == ".png":
            path = p
            break
    return path
