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
