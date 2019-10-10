import textwrap

from beautifier import Beautifier

if __name__ == "__main__":
    testcases = [
        ("Abc=12+3;", "Abc = 12 + 3;"),
        (" - (1+  2)   /--3", "-(1 + 2) / --3"),
        ("1^2*3%4+(-56)", "1 ^ 2 * 3 % 4 + (-56)"),
        ("1 &&2|| 3", "1 && 2 || 3"),
        ('Msg   = "1  +2 "  ;', 'Msg = "1  +2 ";'),
        ("F =! true!=   false;", "F = !true != false;"),
        ("eval(    sin(@pi /2));", "eval(sin(@pi / 2));"),
        ("A+=B;", "A += B;"),
        ("A++ -B", "A++ - B"),
        ("++A* B;", "++A * B;"),
        ("A^=B;", "A ^= B;"),
        ("return   A<B?   A :B;", "return A < B ? A : B;"),
        ("A= [1,  2, - 3] ;", "A = [1, 2, -3];"),
        ("A[(1-1)];", "A[(1 - 1)];"),
        (
            "#define FLAG   1/* comment*/",
            """
            #define FLAG   1
            /* comment*/
            """,
        ),
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
              for (I=0;I<10;I++)
                  #if D
                      print( "debug print");
              #endif
               #endif
            }
            """,
            """
            {
            #if DEBUG
                for (I = 0; I < 10; I++)
            #if D
                print("debug print");
            #endif
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
            A =1+2;/* cm*/
            A;
            """,
            """
            A = 1 + 2;
            /* cm*/
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
            A; //   single line
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
            module my_module $// c
            localf  myfunc$
            //   c2
            endmodule$
            end $
            """,
            """
            module my_module$ // c
            localf myfunc$ //   c2
            endmodule$
            end$
            """,
        ),
    ]
    for input_text, output_text in [
        (textwrap.dedent(i).strip(), textwrap.dedent(o).strip()) for i, o in testcases
    ]:
        b = Beautifier(input_text)
        formatted = b.beautify()
        assert formatted == output_text, "\ngot:\n{}\nwant:\n{}".format(
            formatted, output_text
        )
        c = Beautifier(formatted)
        formatted_2 = c.beautify()
        assert formatted == formatted_2, "\nformat once:\n{}\nformat twice:\n{}".format(
            formatted, formatted_2
        )
