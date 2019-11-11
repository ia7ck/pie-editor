from unittest import TestCase, main

from outputanalyzer import find_error_line, find_imagefile_path


class TestOutputAnalyzer(TestCase):
    def test_find_error_line(self):
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
            find_error_line(
                "error([7,4294967295,evalf : h undefined,[asir_where,[[toplevel,7],[string,f,5],[string,g,2],[,end,0]]]])"
            ),
            2,
        )

    def test_success(self):
        """
        X = 1 + 2;
        """
        self.assertEqual(find_error_line(""), -1)

    def test_find_imagefile_path(self):
        """
        print_png_form(x^2 - y)
        """
        self.assertEqual(
            find_imagefile_path(
                "["
                + "/home/xxx/.OpenXM_tmp/21258/work0.png,"
                + "/home/xxx/.OpenXM_tmp/21258/work0,"
                + "/home/ikd/.OpenXM_tmp/21258/work0.tex,"
                + "/home/xxx/.OpenXM_tmp/21258"
                + "]"
            ),
            "/home/xxx/.OpenXM_tmp/21258/work0.png",
        )

    def test_notfound_imagefile_path(self):
        self.assertEqual(find_imagefile_path("[[1, 1],[x, y]]"), "")
