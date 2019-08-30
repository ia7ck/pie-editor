import ctypes

# OpenXM/src/ox_toolkit/ox_toolkit.h
class StructTable(ctypes.Structure):
    _fields_ = [("tag", ctypes.c_int), ("flag", ctypes.c_int)]


class StructMathcap(ctypes.Structure):
    _fileds_ = [
        ("cmotbl", ctypes.POINTER(StructTable)),
        ("smtbl", ctypes.POINTER(StructTable)),
        ("opts", ctypes.POINTER(ctypes.c_char_p)),
    ]


class StructOXFILE(ctypes.Structure):
    pass


StructOXFILE._fields_ = [
    ("fd", ctypes.c_int),
    ("*send_int32", ctypes.c_int),
    ("*receive_int32", ctypes.c_int),
    ("serial_number", ctypes.c_int),
    ("received_serial_number", ctypes.c_int),
    ("control", ctypes.POINTER(StructOXFILE)),
    ("mathcal", ctypes.POINTER(StructMathcap)),
    ("error", ctypes.c_int),
    ("wbuf", ctypes.c_char_p),
    ("wbuf_size", ctypes.c_int),
    ("w_buf_count", ctypes.c_int),
    ("*send_double", ctypes.c_int),
    ("*receive_double", ctypes.c_double),
]


class Server:
    def __init__(self):
        self.lib = ctypes.cdll.LoadLibrary("./liba.so")

        self.lib.start.restype = ctypes.POINTER(StructOXFILE)
        self.lib.start.argtypes = None

        self.lib.execute_string.restype = None
        self.lib.execute_string.argtypes = (
            ctypes.POINTER(StructOXFILE),
            ctypes.c_char_p,
        )

        self.lib.pop_string.restype = ctypes.c_char_p
        self.lib.pop_string.argtypes = (ctypes.POINTER(StructOXFILE),)

        self.lib.shutdown.restype = None
        self.lib.shutdown.argtypes = (ctypes.POINTER(StructOXFILE),)

        self.server = None

    def start(self):
        self.server = self.lib.start()

    def execute_string(self, text):
        self.ensure_server_started()
        self.lib.execute_string(self.server, text.encode("utf-8"))

    def pop_string(self):
        self.ensure_server_started()
        return self.lib.pop_string(self.server).decode("utf-8")

    def shutdown(self):
        self.ensure_server_started()
        self.lib.shutdown(self.server)
        self.server = None

    def ensure_server_started(self):
        if self.server == None:
            raise RuntimeError("Server seems not to start.")


if __name__ == "__main__":
    asir_server = Server()
    asir_server.start()
    asir_server.execute_string(
        """ if (1) {
        X = 123;
        Y = X * X;
    };"""
    )
    result = asir_server.pop_string()
    print(result)  # => 15129
    asir_server.shutdown()
