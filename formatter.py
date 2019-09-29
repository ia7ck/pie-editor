# -*- coding: utf-8 -*-


class Token:
    LINECOMMENT = "LINE COMMENT"  # //
    BLOCKCOMMENT = "BLOCK COMMENT"  # /* */

    OPERATOR = "OPERATOR"  # +, -, ++, --, +=, -=, <, <=, ?, :, &&, |, ||, ...

    LPAR = "("
    RPAR = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    COMMA = ","
    SEMICOLON = ";"
    END = "$"

    STRING = "STRING"
    WORD = "WORD"  # 123, Abc, @pi, ...
    DIRECTIVE = "DIRECTIVE"  # #define abc 123, #if 0, ...

    def __init__(self, token_type, content):
        self.token_type = token_type
        self.content = content


class Formatter:
    def __init__(
        self,
        input_text,
        operators=set(
            "+ - * / % ^ = ? : < > += -= *= %= ^= == <= >= != && | ||".split(" ")
        ),
        keywords=set(
            "def module function global local localf if else return static extern for while".split(
                " "
            )
        ),
    ):
        self.operators = operators
        self.ops = set("+ - * / % ^ = < > ? : ! & |".split(" "))
        self.keywords = keywords

        self.text = input_text
        self.i, self.n = 0, len(input_text)
        self.text += "$"
        self.ch = self.text[0]  # text[i] == ch
        self.delims = set(list("+-*/%^=,:;$(){}!?<>[]&|"))
        # self.tokens = self.split_tokens()

        # formatter
        self.current_line = ""
        self.output_lines = []
        self.depth = 0

    def advance(self):
        if self.ch == None:
            print("[log] self.ch is None")
            return
        self.ch = None if self.i + 1 >= self.n else self.text[self.i + 1]
        self.i += 1
        return self.ch

    def next_char(self):
        return self.text[self.i + 1]

    def skip_whitespace(self):
        while self.ch in {" ", "\n", "\t", "\r"}:
            self.advance()  # 空白と改行を飛ばす

    # 今の位置から2文字
    def next_two_char(self):
        return self.text[self.i : self.i + 2]

    def read_linecomment(self):
        begin = self.i
        while self.ch and self.ch != "\n":
            self.advance()
        return Token(Token.LINECOMMENT, self.text[begin : self.i])

    def read_blockcomment(self):
        begin = self.i
        while self.ch and self.next_two_char() != "*/":
            self.advance()
        assert self.next_two_char() == "*/", "not found: '*/'"
        self.advance()
        self.advance()
        return Token(Token.BLOCKCOMMENT, self.text[begin : self.i])

    def read_word(self):
        begin = self.i
        while self.ch and (not self.ch in (self.delims | {'"', " ", "\n", "\t"})):
            self.advance()
        assert self.ch == None or begin < self.i
        return Token(Token.WORD, self.text[begin : self.i])

    def read_string(self):
        begin = self.i
        self.advance()
        while self.ch and self.ch != '"':
            self.advance()
        assert self.ch == '"', "\ngot: '{}'\nwant: '\"'".format(self.ch)
        self.advance()
        return Token(Token.STRING, self.text[begin : self.i])

    def read_directive(self):
        begin = self.i
        while (
            self.ch and self.ch != "\n" and (not self.next_two_char() in {"//", "/*"})
        ):
            self.advance()
        return Token(Token.DIRECTIVE, self.text[begin : self.i].rstrip(" "))

    def read_token(self):
        self.skip_whitespace()
        t = Token("", "")
        if self.next_two_char() == "//":
            return self.read_linecomment()
        if self.next_two_char() == "/*":
            return self.read_blockcomment()
        if self.ch in self.ops:
            if self.ch in {"?", ":"}:
                t = Token(Token.OPERATOR, self.ch)
            elif self.ch == "&":
                assert self.next_char() == "&"
                t = Token(Token.OPERATOR, "&&")
                self.advance()
            elif self.ch == "|":
                if self.next_char() == "|":
                    t = Token(Token.OPERATOR, "||")
                    self.advance()
                else:
                    t = Token(Token.OPERATOR, "|")
            elif self.ch in {"+", "-"}:
                if self.next_char() in {self.ch, "="}:
                    t = Token(Token.OPERATOR, self.ch + self.next_char())
                    self.advance()
                else:
                    t = Token(Token.OPERATOR, self.ch)
            else:
                if self.next_char() == "=":
                    t = Token(Token.OPERATOR, self.ch + "=")
                    self.advance()
                else:
                    t = Token(Token.OPERATOR, self.ch)
        elif self.ch == "(":
            t = Token(Token.LPAR, "(")
        elif self.ch == ")":
            t = Token(Token.RPAR, ")")
        elif self.ch == "{":
            t = Token(Token.LBRACE, "{")
        elif self.ch == "}":
            t = Token(Token.RBRACE, "}")
        elif self.ch == "[":
            t = Token(Token.LBRACKET, "[")
        elif self.ch == "]":
            t = Token(Token.RBRACKET, "]")
        elif self.ch == ",":
            t = Token(Token.COMMA, ",")
        elif self.ch == ";":
            t = Token(Token.SEMICOLON, ";")
        elif self.ch == "$":
            t = Token(Token.END, "$")
        elif self.ch == '"':
            return self.read_string()
        elif self.ch == "#":
            return self.read_directive()
        else:
            return self.read_word()
        self.advance()
        return t

    def split_tokens(self):
        tokens = []
        while self.ch:
            t = self.read_token()
            # print(t.token_type, t.content)
            tokens.append(t)
        return tokens

    """
    formatter
    """

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

    def format(self):
        prev = Token("", "")
        semicolon_cnt, inside_for = 0, False
        while self.ch:
            t = self.read_token()
            if t.token_type == Token.LINECOMMENT:
                self.append_linecomment(t.content, prev.token_type)
            elif t.token_type == Token.BLOCKCOMMENT:
                self.append_blockcomment(t.content)
            elif t.token_type == Token.OPERATOR:
                if t.content == "!":
                    self.append_content("!")  # 前置
                elif t.content in {"++", "--"}:
                    self.append_after_rstrip(t.content, " ")
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
                    if self.output_lines[-1] == "}":
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
        return "\n".join(self.output_lines)


if __name__ == "__main__":
    import sys

    text = sys.stdin.read()
    f = Formatter(text)
    print(f.format())
