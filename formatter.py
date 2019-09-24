import textwrap


def split_tokens(s):
    i, n = 0, len(s)
    s += " "  # s[n] == " "
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
            pre = ""
            i += 1
            while i < n and s[i] != "\n":
                pre += s[i]
                i += 1
            tokens.extend(["#", pre])
            i += 1
        elif s[i : i + 2] == "//":
            comment = ""
            i += 2
            while i < n and s[i] != "\n":
                comment += s[i]
                i += 1
            tokens.extend(["//", comment.lstrip()])  # 先頭の空白を取り除く
            i += 1
        elif s[i : i + 2] == "/*":
            comment = ""
            i += 2
            while i < n and s[i : i + 2] != "*/":
                comment += s[i]
                i += 1
            assert s[i : i + 2] == "*/", "got: '{}', want: '*/'".format(s[i : i + 2])
            tokens.extend(["/*", comment.strip("\n"), "*/"])  # 先頭末尾に改行があったら取り除く
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
                tokens.append(c)
                i += 1
            else:  # @pi, Abc_123, return, def
                idt = ""
                while (
                    i < n
                    and (not s[i] in {'"', " ", "\n", "\t"})
                    and (not s[i] in delims)
                ):
                    idt += s[i]
                    i += 1
                tokens.append(idt)
        while i < n and s[i] in {" ", "\n", "\t"}:
            i += 1  # 空白と改行を飛ばす
    return tokens


def should_append_space(text):
    return len(text) >= 1 and (not text[-1] in {" ", "(", "["})


def indent_text(text, depth):
    return " " * (depth * 4) + text


def format_code(input_text):
    tokens = split_tokens(input_text.strip())
    tokens.append(" ")
    output_lines, ln = [], ""
    depth = 0  # indent の深さ
    lpar, lpar_at_for, inside_for = 0, -1, False
    ops = set("+ - * / % ^ = ? : < > += -= *= %= ^= == <= >= != && | ||".split(" "))
    keywords = set(
        "def module function global local localf if else return static extern for while".split(
            " "
        )
    )
    i = 0
    while i + 1 < len(tokens):
        t = tokens[i]
        if t == "$":
            output_lines.append(indent_text(ln + "$", depth))
            ln = ""
        elif t == "#":
            assert ln == ""
            output_lines.append("#" + tokens[i + 1])
            i += 1
        elif t == "//":
            if len(ln) >= 1 and ln[-1] != " ":
                ln += " "
            output_lines.append(indent_text(ln + t + " " + tokens[i + 1], depth))
            i += 1
            ln = ""
        elif t in {"/*", "*/"}:
            if len(ln) >= 1:
                output_lines.append(indent_text(ln, depth))
                ln = ""
            output_lines.append(indent_text(t, depth))
        elif t == ";":
            if inside_for:  # for (I = 0; I < 10; I++)
                ln += ";" + " "
            else:
                output_lines.append(indent_text(ln + ";", depth))
                ln = ""
        elif t in ops:
            if should_append_space(ln):  # (, [, などの直後だと False
                ln += " "
            ln += t + " "
        elif t == "{":
            output_lines.append(indent_text(ln + "{", depth))
            ln = ""
            depth += 1
        elif t == "}":
            depth -= 1
            if tokens[i + 1] == "else":  # } else
                ln += "}" + " "
            else:
                output_lines.append(indent_text(ln + "}", depth))
                ln = ""
        elif t == ",":
            ln += "," + " "
        elif t == ")":
            if tokens[i + 1] in {",", ";", "[", "]", ")"}:
                ln += ")"
            else:  # () { ... }, () return
                ln += ")" + " "
            lpar -= 1
            if lpar == lpar_at_for:
                inside_for = False
        elif t in keywords:
            ln += t + " "
            if t == "for":
                inside_for = True
                lpar_at_for = lpar
        else:
            ln += t
            if t == "(":
                lpar += 1
        i += 1
    assert depth == 0, "Missing right brace: '}'"
    assert lpar == 0, "Missing right parenthesis: ')'"
    if len(ln) >= 1:
        output_lines.append(indent_text(ln, depth))
    return "\n".join(output_lines)


def test_format_code():
    testcases = [
        (
            """
            Abc=(12  +3 )/  4^  (5%6)*( -7  )- 89  -0;
            Msg   = "1  +2*_ "  ;
            f =! true!=   false;
            eval(    sin(@pi /2));
            """,
            """
            Abc = (12 + 3) / 4 ^ (5 % 6) * (- 7) - 89 - 0;
            Msg = "1  +2*_ ";
            f = !true != false;
            eval(sin(@pi / 2));
            """,
        ),
        (
            """
            A+=B;
            A++ -B;
            ++A* B;
            A^=B;
            """,
            """
            A += B;
            A++ - B;
            ++A * B;
            A ^= B;
            """,
        ),
        (
            """
            A =1 +/*comment  comment*/- 3 ;
            /*   multi
            line
              comment*/
            /*
              a
                b
            */
            A=-1;
            //   single line
            A =123;//single line2
            """,
            """
            A = 1 + 
            /*
            comment  comment
            */
            - 3;
            /*
               multi
            line
              comment
            */
            /*
              a
                b
            */
            A = - 1;
            // single line
            A = 123;
            // single line2
            """,
        ),
        (
            """
            #if DEBUG
             print( "debug print");
            #endif
            """,
            """
            #if DEBUG
            print("debug print");
            #endif
            """,
        ),
        (
            """
            def f123  (A,  B  ){
            if(1== 2 &&true||  false){ X=1+2;  someFunc(X);}
            else
            {
                  Y =123;
            }}
            """,
            """
            def f123(A, B) {
                if (1 == 2 && true || false) {
                    X = 1 + 2;
                    someFunc(X);
                } else {
                    Y = 123;
                }
            }
            """,
        ),
        (
            """
            def sign(X )
            {return (X==0)? 0: (X<0)? -1: 1;
            }
            """,
            """
            def sign(X) {
                return (X == 0) ? 0 : (X < 0) ? - 1 : 1;
            }
            """,
        ),
        (
            """
              for(I  =0; I< 10;   I++)
            {for(J=0;J<I  ;++J   ){
            continue;  K= I *J;
            L =I + J;} print(I*2 ); break  ;}
            """,
            """
            for (I = 0; I < 10; I++) {
                for (J = 0; J < I; ++J) {
                    continue;
                    K = I * J;
                    L = I + J;
                }
                print(I * 2);
                break;
            }
            """,
        ),
        (
            """
            def f(Cond) {
                if(Cond)return 1;
                else{return 0 ; }
            }
            """,
            """
            def f(Cond) {
                if (Cond) return 1;
                else {
                    return 0;
                }
            }
            """,
        ),
        (
            """
            A= [1,  2, -3] ;
            A[(1-1)];
            """,
            """
            A = [1, 2, - 3];
            A[(1 - 1)];
            """,
        ),
    ]
    for input_text, output_text in [
        (textwrap.dedent(i).strip(), textwrap.dedent(o).strip()) for i, o in testcases
    ]:
        formatted = format_code(input_text)
        assert formatted == output_text, "\ngot:\n{}\nwant:\n{}".format(
            formatted, output_text
        )
        assert formatted == format_code(formatted)


if __name__ == "__main__":
    test_format_code()
