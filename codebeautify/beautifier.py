#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from _exception import AsirSyntaxError
from _lexer import Lexer
from _token import Token


class Beautifier:
    def __init__(self, input_text):
        self.le = Lexer(input_text)
        self.current_line = ""
        self.output_lines = []
        self.depth = 0

    def append_current_line(self):
        if len(self.current_line) == 0:  # 空行は無視する
            return
        self.output_lines.append(
            ((" " * (self.depth * 4)) + self.current_line).rstrip()
        )
        self.current_line = ""

    def append_content(self, content, trailing=""):
        self.current_line += content + trailing

    def append_after_rstrip(self, content, trailing=""):
        self.current_line = self.current_line.rstrip(" ") + content + trailing

    def append_linecomment(self, comment, prev_token_type):
        self.append_content(comment)
        self.append_current_line()

    def append_blockcomment(self, comment):
        self.append_current_line()  # 念のため
        if len(comment.splitlines()) == 1:  # /* comment */
            self.append_content(comment)
            self.append_current_line()
        else:
            self.append_content("/*")
            self.append_current_line()
            lines = comment[2:-2].splitlines()
            # /*  com
            #       ment */
            # --> [com, ment]
            for ln in lines:
                if len(ln.strip()) >= 1:
                    self.output_lines.append(ln.rstrip())
            self.append_content("*/")
            self.append_current_line()
            # /*
            #   com
            #       ment
            # */

    def beautify(self):
        prev = Token("", "")
        semicolon_cnt, inside_for = 0, False
        while not self.le.is_end():
            t = self.le.read_token()
            if t.token_type == Token.LINECOMMENT:
                self.append_linecomment(t.content, prev.token_type)
            elif t.token_type == Token.BLOCKCOMMENT:
                self.append_blockcomment(t.content)
            elif t.token_type == Token.OPERATOR:
                if t.content == "!":
                    self.append_content("!")  # 前置
                elif t.content in {"++", "--"}:
                    if prev.token_type == Token.OPERATOR:
                        self.append_content(t.content, " ")  # ... * ++
                    else:
                        self.append_after_rstrip(t.content, " ")  # A++ など
                elif t.content == "-":
                    if prev.token_type in {
                        "",
                        Token.COMMA,
                        Token.SEMICOLON,
                        Token.LPAR,
                    }:
                        self.append_content("-")  # ... (-
                    elif prev.content in {"=", "==", "<", "<=", ">", ">="}:
                        self.append_content("-")  # ... == -
                    else:
                        self.append_content("-", " ")
                else:
                    self.append_content(t.content, " ")
            elif t.token_type == Token.LPAR:
                if prev.content in {"for", "if"}:
                    self.append_content("(")  # ... for (
                elif prev.token_type == Token.WORD:  # 関数呼び出し
                    self.append_after_rstrip("(")  # ... func(
                else:
                    self.append_content("(")  # ... + (
            elif t.token_type == Token.RPAR:
                self.append_after_rstrip(")", " ")
            elif t.token_type == Token.LBRACE:
                self.append_content("{")
                self.append_current_line()
                self.depth += 1
            elif t.token_type == Token.RBRACE:
                self.append_current_line()
                self.depth -= 1
                if self.depth < 0:
                    raise AsirSyntaxError("Too many right brace '}'")
                self.append_content("}")
                self.append_current_line()
            elif t.token_type == Token.LBRACKET:
                if prev.token_type == Token.WORD:  # 添字アクセス
                    self.append_after_rstrip("[")  # ... arr[
                else:
                    self.append_content("[")  # ... = [
            elif t.token_type == Token.RBRACKET:
                self.append_after_rstrip("]", " ")
            elif t.token_type == Token.COMMA:
                self.append_after_rstrip(",", " ")
            elif t.token_type == Token.SEMICOLON:
                if inside_for:
                    semicolon_cnt += 1
                    if semicolon_cnt == 2:
                        inside_for = False
                    self.append_after_rstrip(";", " ")  # for(a; b;
                else:
                    self.append_after_rstrip(";")
                    self.append_current_line()
            elif t.token_type == Token.END:
                self.append_after_rstrip("$")
                self.append_current_line()
            elif t.token_type == Token.STRING:
                self.append_content(t.content)
            elif t.token_type == Token.WORD:
                if t.content == "else":
                    if self.output_lines[-1].lstrip(" ") == "}":
                        self.output_lines.pop()
                        self.append_content("}" + " " + "else", " ")
                        # if (cond) {
                        #
                        # } else
                    else:
                        self.append_content("else", " ")
                        # if (cond) return 1;
                        # else
                else:
                    if prev.content in {"++", "--"}:
                        self.append_after_rstrip(t.content, " ")  # ... ++a
                    else:
                        self.append_content(t.content, " ")
                        if t.content == "for":
                            inside_for = True
                            semicolon_cnt = 0
            elif t.token_type == Token.DIRECTIVE:
                if len(self.current_line) >= 1:
                    self.append_current_line()
                self.output_lines.append(t.content)  # インデント無し
            else:
                raise AsirSyntaxError(  # ?
                    "Unknown token. type: {}, content: '{}'".format(
                        t.token_type, t.content
                    )
                )
            prev = t
        if self.depth > 0:
            raise AsirSyntaxError("Missing right brace '}'")
        if len(self.current_line) >= 1:
            self.append_current_line()
        return "\n".join(self.output_lines).strip()


if __name__ == "__main__":
    from sys import stdin, stderr

    text = stdin.read()
    try:
        f = Beautifier(text)
        result = f.beautify()
        print(result)
    except AsirSyntaxError as err:
        print(err, file=stderr)
