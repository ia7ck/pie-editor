from textwrap import dedent
from unittest import TestCase

from beautifier import Beautifier


class TestBeautifier(TestCase):
    def _beautify(self, input_text):
        b = Beautifier(input_text)
        return b.beautify()

    def _test(self, input_text, output_text):
        result_1 = self._beautify(dedent(input_text).strip())  # strip() していい?
        self.assertEqual(result_1, dedent(output_text).strip())
        result_2 = self._beautify(result_1)
        self.assertEqual(result_2, result_1)

    def test_operators(self):
        testcases = [
            ("Abc=12+3;", "Abc = 12 + 3;"),
            (" - (1+  2)   /--3", "-(1 + 2) / --3"),
            ("1>= - 2;", "1 >= -2;"),
            ("1^2*3%4+(-56)", "1 ^ 2 * 3 % 4 + (-56)"),
            ("1 &&2|| 3", "1 && 2 || 3"),
            ("F =! true!=   false;", "F = !true != false;"),
            ("A+=B;", "A += B;"),
            ("A++ -B", "A++ - B"),
            ("++A* B;", "++A * B;"),
            ("A^=B;", "A ^= B;"),
            ("return   A<B?   A :B;", "return A < B ? A : B;"),
        ]
        for i, o in testcases:
            self._test(i, o)

    def test_string(self):
        testcases = [('Msg   = "1  +2 "  ;', 'Msg = "1  +2 ";')]
        for i, o in testcases:
            self._test(i, o)

    def test_atmark_symbol(self):
        testcases = [("eval(    sin(@pi /2));", "eval(sin(@pi / 2));")]
        for i, o in testcases:
            self._test(i, o)

    def test_array(self):
        testcases = [
            ("A= [1,  2, - 3] ;", "A = [1, 2, -3];"),
            ("A[(1-1)];", "A[(1 - 1)];"),
            ("A[     0]*=1;", "A[0] *= 1;"),
        ]
        for i, o in testcases:
            self._test(i, o)

    def test_if_else(self):
        testcases = [
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
                "if(Cond) return 1; else {return 0;}",
                """
                if (Cond) return 1;
                else {
                    return 0;
                }
                """,
            ),
        ]
        for i, o in testcases:
            self._test(i, o)

    def test_comment(self):
        testcases = [
            (
                "#define FLAG   1/* comment*/",
                """
                #define FLAG   1
                /* comment*/
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
                A;
                //   single line
                B;
                //single line2
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
                module my_module$
                // c
                localf myfunc$
                //   c2
                endmodule$
                end$
                """,
            ),
        ]
        for i, o in testcases:
            self._test(i, o)

    def test_directive(self):
        testcases = [
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
            )
        ]
        for i, o in testcases:
            self._test(i, o)

    def test_forloop(self):
        testcases = [
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
            )
        ]
        for i, o in testcases:
            self._test(i, o)
