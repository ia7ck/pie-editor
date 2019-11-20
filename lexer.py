# -*- encoding: utf-8 -*-

# for syntax highlighting

import pygments.lexer
import pygments.token

# https://pygments.org/docs/lexerdevelopment.html#regexlexer
# https://pygments.org/docs/tokens.html
class AsirLexer(pygments.lexer.RegexLexer):
    tokens = {
        "root": [
            # http://www.math.kobe-u.ac.jp/OpenXM/Current/doc/asir2000/html-ja/man/man_20.html
            (
                r"\b(break|continue|do|else|extern|for|if|return|static|struct|while)\b",  # \b は fore とかにマッチしないために必要
                pygments.token.Keyword,
            ),
            (
                r"\b(def|endmodule|function|global|local|localf|module)\b",
                pygments.token.Keyword,
            ),
            (
                r"\b(car|cdr|getopt|newstruct|map|pari|quote|recmap|timer)\b",
                pygments.token.Name.Builtin,
            ),
            (r"/\*.*?\*/", pygments.token.Comment.Multiline),
            (r"//.*$", pygments.token.Comment.Singleline),
            (r'"', pygments.token.Literal.String, "string"),
            (r"[A-Z][A-Za-z0-9_]*", pygments.token.Name.Variable),
            (
                r"([a-z][A-Za-z0-9_]*)(\s*)(\()",
                pygments.lexer.bygroups(
                    pygments.token.Name.Function,
                    pygments.token.Whitespace,
                    pygments.token.Punctuation,
                ),
            ),
            (r"[a-z][A-Za-z0-9_]*", pygments.token.Name.Constant),  # 不定元
            (r"[0-9]+", pygments.token.Literal.Number),
        ],
        # https://pygments.org/docs/lexerdevelopment.html#changing-states
        "string": [
            (r'[^"]', pygments.token.Literal.String),
            (r'"', pygments.token.Literal.String, "#pop"),
        ],
    }
