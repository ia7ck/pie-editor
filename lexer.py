import pygments.lexer
import pygments.token

# http://www.math.kobe-u.ac.jp/Asir/cfep/html-ja_JP.utf8/html-ja/man_23.html#SEC23
class AsirLexer(pygments.lexer.RegexLexer):
    tokens = {
        "root": [
            (
                r"(break|continue|do|else|extern|for|if|return|static|struct|while)",
                pygments.token.Keyword,
            ),
            (
                r"(def|endmodule|function|global|local|localf|module)",
                pygments.token.Keyword,
            ),
            (
                r"(car|cdr|getopt|newstruct|map|pari|quote|recmap|timer)",
                pygments.token.Name.Builtin,
            ),
            (r"/\*", pygments.token.Comment.Multiline, "comment"),
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
        "comment": [
            (r"[^\*/]", pygments.token.Comment.Multiline),
            (r"\*/", pygments.token.Comment.Multiline, "#pop"),
            (r"[\*/]", pygments.token.Comment.Multiline),
        ],
        "string": [
            (r'[^"]', pygments.token.Literal.String),
            (r'"', pygments.token.Literal.String, "#pop"),
        ],
    }
