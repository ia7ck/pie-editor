from time import sleep
from unittest import TestCase

from server import Server


class TestServer(TestCase):
    def setUp(self):
        self.sv = Server()
        self.sv.start()

    def tearDown(self):
        self.sv.shutdown()

    def test_select(self):
        sv = self.sv
        sv.execute_string(
            """
            if (1) {
                X = 123;
                Y = X * X;
            } else {};
            """
        )
        sleep(1)  # 必要?
        self.assertNotEqual(sv.select(), 0)
        result = sv.pop_string()
        self.assertEqual(result, "15129")

        sv.execute_string("fctr(x^20000 - y^20000);")
        sleep(1)
        self.assertEqual(sv.select(), 0)
        sv.reset()
        sv.execute_string("fctr(x^2 - y^2);")
        sleep(1)
        self.assertNotEqual(sv.select(), 0)
        result = sv.pop_string()
        self.assertEqual(result, "[[1,1],[x-y,1],[x+y,1]]")

    def test_undefined_error(self):
        sv = self.sv
        sv.execute_string(
            """
            if (1) {
                def f() {
                    g();
                }
                f();
            } else {};
            """
        )
        result = sv.pop_string()
        self.assertEqual(
            result,
            "error([4,4294967295,evalf : g undefined,[asir_where,[[toplevel,6],[string,f,4]]]])",
        )
