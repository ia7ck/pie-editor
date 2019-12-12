# -*- encoding: utf-8 -*-

# for syntax highlighting

import pygments.lexer
import pygments.lexers.c_cpp
import pygments.token


# https://pygments.org/docs/tokens.html
# https://pygments.org/docs/lexerdevelopment/#subclassing-lexers-derived-from-regexlexer
class AsirLexer(pygments.lexers.c_cpp.CFamilyLexer):
    tokens = {
        "statements": [
            (
                r"\b(def|endmodule|function|global|local|localf|module)\b",
                pygments.token.Keyword,
            ),
            (
                r"\b(car|cdr|getopt|newstruct|map|pari|quote|recmap|timer)\b",
                pygments.token.Name.Builtin,  # functions
            ),
            pygments.lexer.inherit,
            (
                r"([a-z][A-Za-z0-9_]*)(\s*)(\()",  # 関数呼び出し
                pygments.lexer.bygroups(
                    pygments.token.Name.Function,
                    pygments.token.Whitespace,
                    pygments.token.Punctuation,
                ),
            ),
            (r"[a-z][A-Za-z0-9_]*", pygments.token.Name.Constant),  # 不定元
            (r"[0-9]+", pygments.token.Literal.Number),
            (r"\$", pygments.token.Other),
            # http://www.math.kobe-u.ac.jp/OpenXM/Current/doc/asir2000/html-ja/man/man_14.html
            (r"@.(@|\d+|i|pi|e||>|<|>=|<=|==|&&|\|\|)", pygments.token.Name.Builtin),
        ]
    }
