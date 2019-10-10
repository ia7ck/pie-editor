# -*- coding: utf-8 -*-


from _token import Token


class Lexer:
    def __init__(self, input_text):
        self.ops = set("+ - * / % ^ = < > ? : ! & |".split(" "))

        self.text = input_text
        self.i, self.n = 0, len(input_text)
        self.text += "$"
        self.ch = self.text[0]  # text[i] == ch
        self.delims = set(list("+-*/%^=,:;$(){}!?<>[]&|"))

    def is_end(self):
        return self.ch == None

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
