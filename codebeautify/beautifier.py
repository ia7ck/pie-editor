# -*- coding: utf-8 -*-


from _token import Token
from _lexer import Lexer


class Beautifier:
    def __init__(self, input_text):
        self.le = Lexer(input_text)
        self.current_line = ""
        self.output_lines = []
        self.depth = 0

    def append_current_line(self):
        if len(self.current_line) == 0:
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
        if prev_token_type in {Token.SEMICOLON, Token.END}:
            self.output_lines[-1] += " " + comment
        else:
            self.append_content(comment)
            self.append_current_line()

    def append_blockcomment(self, comment):
        if len(comment.splitlines()) == 1:  # 一行コメント
            self.append_current_line()
            self.append_content(comment, " ")
            self.append_current_line()
        else:
            self.append_current_line()
            self.append_content("/*")
            self.append_current_line()
            lines = comment[2:-2].splitlines()
            for ln in lines:
                if len(ln.strip()) >= 1:
                    self.output_lines.append(ln.rstrip())
            self.append_content("*/")
            self.append_current_line()

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
                        self.append_content(t.content, " ")
                    else:
                        self.append_after_rstrip(t.content, " ")
                elif t.content == "-":
                  if prev.token_type in {"", Token.SEMICOLON, Token.OPERATOR, Token.LPAR}:
                    self.append_content("-")
                  else:
                    self.append_content("-", " ")
                else:
                    self.append_content(t.content, " ")
            elif t.token_type == Token.LPAR:
                if prev.content in {"for", "if"}:
                    self.append_content("(")
                elif prev.token_type == Token.WORD:  # 関数呼び出し
                    self.append_after_rstrip("(")
                else:
                    self.append_content("(")
            elif t.token_type == Token.RPAR:
                self.append_after_rstrip(")", " ")
            elif t.token_type == Token.LBRACE:
                self.append_content("{")
                self.append_current_line()
                self.depth += 1
            elif t.token_type == Token.RBRACE:
                self.append_current_line()
                self.depth -= 1
                self.append_content("}")
                self.append_current_line()
            elif t.token_type == Token.LBRACKET:
                if prev.token_type == Token.WORD:  # 添字アクセス
                    self.append_after_rstrip("[")
                else:
                    self.append_content("[")
            elif t.token_type == Token.RBRACKET:
                self.append_after_rstrip("]")
            elif t.token_type == Token.COMMA:
                self.append_after_rstrip(",", " ")
            elif t.token_type == Token.SEMICOLON:
                if inside_for:
                    semicolon_cnt += 1
                    if semicolon_cnt == 2:
                        inside_for = False
                    self.append_after_rstrip(";", " ")
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
                    else:
                        self.append_content("else", " ")
                else:
                    if prev.content in {"++", "--"}:
                        self.append_after_rstrip(t.content, " ")
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
                assert False, "unknown token type: {}, content: '{}'".format(
                    t.token_type, t.content
                )
            prev = t
        if len(self.current_line) >= 1:
            self.append_current_line()
        return "\n".join(self.output_lines).strip()


if __name__ == "__main__":
    import sys

    text = sys.stdin.read()
    f = Beautifier(text)
    print(f.beautify())
