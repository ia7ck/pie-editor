from unittest import TestCase
from textwrap import dedent

from _lexer import Lexer
from _token import Token


class TestLexer(TestCase):
    def test_read_token(self):
        input_text = """
            A+ B = -123;
            (1 *--2)   /-3++;
            Msg = "  msg000"
            flag =! true?1:0!=   false
            {eval(@pi)}
            //comment
            #define FLAG 1 /*
            comment c */
            if(1) return 1; else {[a, 0]}
        """
        want = [
            [Token.WORD, "A"],
            [Token.OPERATOR, "+"],
            [Token.WORD, "B"],
            [Token.OPERATOR, "="],
            [Token.OPERATOR, "-"],
            [Token.WORD, "123"],
            [Token.SEMICOLON, ";"],
            [Token.LPAR, "("],
            [Token.WORD, "1"],
            [Token.OPERATOR, "*"],
            [Token.OPERATOR, "--"],
            [Token.WORD, "2"],
            [Token.RPAR, ")"],
            [Token.OPERATOR, "/"],
            [Token.OPERATOR, "-"],
            [Token.WORD, "3"],
            [Token.OPERATOR, "++"],
            [Token.SEMICOLON, ";"],
            [Token.WORD, "Msg"],
            [Token.OPERATOR, "="],
            [Token.STRING, '"  msg000"'],
            [Token.WORD, "flag"],
            [Token.OPERATOR, "="],
            [Token.OPERATOR, "!"],
            [Token.WORD, "true"],
            [Token.OPERATOR, "?"],
            [Token.WORD, "1"],
            [Token.OPERATOR, ":"],
            [Token.WORD, "0"],
            [Token.OPERATOR, "!="],
            [Token.WORD, "false"],
            [Token.LBRACE, "{"],
            [Token.WORD, "eval"],
            [Token.LPAR, "("],
            [Token.WORD, "@pi"],
            [Token.RPAR, ")"],
            [Token.RBRACE, "}"],
            [Token.LINECOMMENT, "//comment"],
            [Token.DIRECTIVE, "#define FLAG 1"],
            [Token.BLOCKCOMMENT, "/*\ncomment c */"],
            [Token.WORD, "if"],
            [Token.LPAR, "("],
            [Token.WORD, "1"],
            [Token.RPAR, ")"],
            [Token.WORD, "return"],
            [Token.WORD, "1"],
            [Token.SEMICOLON, ";"],
            [Token.WORD, "else"],
            [Token.LBRACE, "{"],
            [Token.LBRACKET, "["],
            [Token.WORD, "a"],
            [Token.COMMA, ","],
            [Token.WORD, "0"],
            [Token.RBRACKET, "]"],
            [Token.RBRACE, "}"],
        ]
        le = Lexer(dedent(input_text).strip())
        for tt, c in want:
            token = le.read_token()
            self.assertEqual(token.token_type, tt)
            self.assertEqual(token.content, c)
