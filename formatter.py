# -*- coding: utf-8 -*-


import textwrap


def split_tokens(s):
    i, n = 0, len(s)
    s += "$"  # s[n] == "$"
    tokens, delims = [], set(list("+-*/%^=,:;$(){}!?<>[]&|"))
    while i < n:
        if s[i] == '"':  # 文字列の中は token に分割しない
            string = ""
            i += 1
            while i < n and s[i] != '"':
                string += s[i]
                i += 1
            assert s[i] == '"', "got: '{}', want: '\"'".format(s[i])
            tokens.append('"' + string + '"')
            i += 1
        elif s[i] == "#":  # #if FLAG, #endif, ...
            directive = ""
            i += 1
            while i < n and s[i] != "\n":
                directive += s[i]
                i += 1
            tokens.extend(["#", directive])
            i += 1
        elif s[i : i + 2] == "//":
            comment = ""
            i += 2
            while i < n and s[i] != "\n":
                comment += s[i]
                i += 1
            tokens.extend(["//", comment])
            i += 1
        elif s[i : i + 2] == "/*":
            comment = ""
            i += 2
            while i < n and s[i : i + 2] != "*/":
                comment += s[i]
                i += 1
            assert s[i : i + 2] == "*/", "got: '{}', want: '*/'".format(s[i : i + 2])
            tokens.extend(["/*", comment.strip("\n"), "*/"])  # 先頭末尾の改行を取り除く
            i += 2
        else:
            c = s[i]
            if c == "&":  # &&
                assert s[i + 1] == "&", "got: '{}', want: '&'".format(s[i + 1])
                tokens.append("&&")
                i += 2
            elif c in {"|", ":"}:  # ||, ::
                t = c + c if s[i + 1] == c else c
                tokens.append(t)
                i += len(t)
            elif c in {"*", "/", "%", "^", "=", ">", "<", "!"}:  # *, <=, !, !=, ...
                t = c + "=" if s[i + 1] == "=" else c
                tokens.append(t)
                i += len(t)
            elif c in {"+", "-"}:  # +, ++, +=, ...
                t = c + s[i + 1] if s[i + 1] in {c, "="} else c
                tokens.append(t)
                i += len(t)
            elif c in delims:
                if c == ";" and s[i + 1] == "\n":
                    tokens.append(";" + "\n")
                    i += 2
                else:
                    tokens.append(c)
                    i += 1
            else:  # @pi, Abc_123, return, def
                idt = ""
                while i < n and (not s[i] in (delims | {'"', " ", "\n", "\t"})):
                    idt += s[i]
                    i += 1
                tokens.append(idt)
        while i < n and s[i] in {" ", "\n", "\t"}:
            i += 1  # 空白と改行を飛ばす
    return tokens


class Formatter:
    def __init__(
        self,
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
        self.keywords = keywords

        self.text = ""
        self.current_line = ""
        self.output_lines = []
        self.depth = 0

    def should_append_space(self):
        return len(self.current_line) >= 1 and (
            not self.current_line[-1] in {" ", "(", "["}
        )

    def append_singleline_comment(self, begin, comment):
        assert comment.count("\n") == 0
        if len(self.current_line) >= 1 and self.current_line[-1] != " ":
            self.append_token(" ")
        self.append_token(begin + comment)
        if begin == "/*":
            self.append_token("*/")
        self.append_current_line()

    def append_multiline_comment(self, comment):
        if len(self.current_line) >= 1:
            self.append_current_line()
        self.append_token("/*")
        self.append_current_line()
        self.output_lines.append(comment.rstrip())
        self.append_token("*/")
        self.append_current_line()

    def append_token(self, token):
        self.current_line += token

    def append_current_line(self):
        assert len(self.current_line) >= 1
        self.output_lines.append((" " * (self.depth * 4)) + self.current_line)
        self.current_line = ""

    def generate_output(self, input_text):
        self.text = input_text
        tokens = split_tokens(self.text)
        tokens.append("$")
        self.current_line, self.output_lines, self.depth = "", [], 0
        lpar, lpar_at_for, inside_for = 0, -1, False
        i = 0
        while i + 1 < len(tokens):
            t = tokens[i]
            if t == "$":
                self.append_token("$")
                self.append_current_line()
            elif t == "#":
                assert len(self.current_line) == 0
                self.output_lines.append("#" + tokens[i + 1])
                i += 1
            elif t == "//":
                self.append_token("//" + tokens[i + 1])
                self.append_current_line()
                i += 1
            elif t == "/*":
                assert tokens[i + 2] == "*/", "got: {}, want: */".format(tokens[i + 2])
                comment = tokens[i + 1]
                if comment.count("\n") >= 1:  # 複数行コメント
                    self.append_multiline_comment(comment)
                else:
                    self.append_singleline_comment("/*", comment)
                i += 2
            elif t.rstrip() == ";":  # t == ";" or t == ";\n"
                if inside_for:  # for (I = 0; I < 10; I++)
                    self.append_token(";" + " ")
                else:
                    if tokens[i + 1] in {"//", "/*"}:  # ; // ... or ; /* ... */
                        self.append_token(";")
                        begin = tokens[i + 1]
                        body = tokens[i + 2]
                        if begin == "/*":
                            if body.count("\n") >= 1:  # 複数行コメント
                                self.append_multiline_comment(body)
                            else:
                                if t[-1] == "\n":
                                    self.append_current_line()
                                self.append_singleline_comment(begin, body)
                            i += 3
                        else:  # //
                            if t[-1] == "\n":
                                self.append_current_line()
                            self.append_singleline_comment(begin, body)
                            i += 2
                    else:
                        self.append_token(";")
                        self.append_current_line()
            elif t in self.operators:
                if self.should_append_space():  # (, [, などの直後だと False
                    self.append_token(" ")
                self.append_token(t + " ")
            elif t == "{":
                self.append_token("{")
                self.append_current_line()
                self.depth += 1
            elif t == "}":
                self.depth -= 1
                if tokens[i + 1] == "else":  # } else
                    self.append_token("}" + " ")
                else:
                    self.append_token("}")
                    self.append_current_line()
            elif t == ",":
                self.append_token("," + " ")
            elif t == ")":
                if tokens[i + 1].rstrip() in {",", ";", "$", "[", "]", ")"}:
                    self.append_token(")")
                else:  # () { ... }, () return
                    self.append_token(")" + " ")
                lpar -= 1
                if lpar == lpar_at_for:
                    inside_for = False
            elif t in self.keywords:
                self.append_token(t + " ")
                if t == "for":
                    inside_for = True
                    lpar_at_for = lpar
            else:
                self.append_token(t)
                if t == "(":
                    lpar += 1
            i += 1
        assert self.depth == 0, "Missing right brace: '}'"
        assert lpar == 0, "Missing right parenthesis: ')'"
        if len(self.current_line) >= 1:
            self.append_current_line()
        return "\n".join(self.output_lines)


def test_format_code():
    testcases = [
        ("Abc=12+3;", "Abc = 12 + 3;"),
        ("  (1+  2)   /3", "(1 + 2) / 3"),
        ("1^2*3%4+(-56)", "1 ^ 2 * 3 % 4 + (- 56)"),
        ("1 &&2|| 3", "1 && 2 || 3"),
        ('Msg   = "1  +2 "  ;', 'Msg = "1  +2 ";'),
        ("f =! true!=   false;", "f = !true != false;"),
        ("eval(    sin(@pi /2));", "eval(sin(@pi / 2));"),
        ("A+=B;", "A += B;"),
        ("A++ -B", "A++ - B"),
        ("++A* B;", "++A * B;"),
        ("A^=B;", "A ^= B;"),
        ("return   A<B?   A :B;", "return A < B ? A : B;"),
        ("A= [1,  2, -3] ;", "A = [1, 2, - 3];"),
        ("A[(1-1)];", "A[(1 - 1)];"),
        (
            "if(1){I;}else{E;}",
            """
            if (1) {
                I;
            } else {
                E;
            }
            """,
        ),
        (
            """
            if(Cond) return 1; else {return 0;}
            """,
            """
            if (Cond) return 1;
            else {
                return 0;
            }
            """,
        ),
        (
            """
            {
                #if DEBUG
                      print( "debug print");
              #endif
            }
            """,
            """
            {
            #if DEBUG
                print("debug print");
            #endif
            }
            """,
        ),
        (
            """
              for(I  =0; I< 10;   I++){continue;
              break;}
            """,
            """
            for (I = 0; I < 10; I++) {
                continue;
                break;
            }
            """,
        ),
        (
            """
            A =1 +/*   comment  comment*/- 3/*c*//5;/* cm*/
            A;
            """,
            """
            A = 1 + /*   comment  comment*/
            - 3 /*c*/
            / 5; /* cm*/
            A;
            """,
        ),
        (
            """
            /*   multi
            line
              comment*/
            A;/*
              a
                b
            */
            B;
            /*      ccmm*/
            """,
            """
            /*
               multi
            line
              comment
            */
            A;
            /*
              a
                b
            */
            B;
            /*      ccmm*/
            """,
        ),
        (
            """
            A;
            //   single line
            B;//single line2
            """,
            """
            A;
            //   single line
            B; //single line2
            """,
        ),
        (
            """
            if (1) {/*comment */
            Xyz;
                /*
                c
                    o*/
            }//   comment
            else{
              /*
                c o  mment
                */
            }
            """,
            """
            if (1) {
                /*comment */
                Xyz;
                /*
                c
                    o
                */
            }
            //   comment
            else {
                /*
                c o  mment
                */
            }
            """,
        ),
        (
            """
            module my_module $
            localf  myfunc$
            endmodule$
            end $
            """,
            """
            module my_module$
            localf myfunc$
            endmodule$
            end$
            """,
        ),
    ]
    f = Formatter()
    for input_text, output_text in [
        (textwrap.dedent(i).strip(), textwrap.dedent(o).strip()) for i, o in testcases
    ]:
        formatted = f.generate_output(input_text)
        assert formatted == output_text, "\ngot:\n{}\nwant:\n{}".format(
            formatted, output_text
        )
        assert formatted == f.generate_output(
            formatted
        ), "\nformat once:\n{}\nformat twice:\n{}".format(
            formatted, f.generate_output(formatted)
        )


if __name__ == "__main__":
    test_format_code()
