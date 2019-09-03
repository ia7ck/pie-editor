import re


# return -1 if not found
def get_error_line(text):
    if not ("error" in text):
        return -1
    sp = text.split("asir_where")
    if len(sp) < 2:
        return -1
    match = re.search(r"(\d+)", sp[1])
    if match:
        return int(match.group(1))
    else:
        return -1


if __name__ == "__main__":
    assert (
        get_error_line(
            "error([1,4294967295,syntax error,[asir_where,[[toplevel,13]]]])"
        )
        == 13
    )
