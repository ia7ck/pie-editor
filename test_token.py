import textwrap
from formatter import Formatter, Token

if __name__ == "__main__":
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
    f = Formatter(textwrap.dedent(input_text).strip())
    for tt, c in want:
        token = f.read_token()
        assert (
            token.token_type == tt and token.content == c
        ), "\ngot: {}\n'{}'\nwant: {}\n'{}'".format(
            token.token_type, token.content, tt, c
        )
