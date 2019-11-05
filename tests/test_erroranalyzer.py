from unittest import TestCase, main

from erroranalyzer import get_error_line


class TestErrorAnalyzer(TestCase):
    def test_error_analyze(self):
        """
        def g() {
            h();
        }
        def f() { 
            g();
        } 
        f();
        """
        self.assertEqual(
            get_error_line(
                "error([7,4294967295,evalf : h undefined,[asir_where,[[toplevel,7],[string,f,5],[string,g,2],[,end,0]]]])"
            ),
            2,
        )

    def test_success(self):
        """
        X = 1 + 2;
        """
        self.assertEqual(get_error_line(""), -1)
