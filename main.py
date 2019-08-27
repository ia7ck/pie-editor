import ctypes

lib = ctypes.cdll.LoadLibrary("./liba.so")


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

lib.start.restype = ctypes.POINTER(StructOXFILE)
lib.start.argtypes = None  # ?

lib.execute_string.restype = None
lib.execute_string.argtypes = (ctypes.POINTER(StructOXFILE), ctypes.c_char_p)

lib.pop_string.restype = ctypes.c_char_p
lib.pop_string.argtypes = (ctypes.POINTER(StructOXFILE),)

lib.shutdown.restype = None
lib.shutdown.argtypes = (ctypes.POINTER(StructOXFILE),)

server = lib.start()
lib.execute_string(server, "1 + 2 + 12345678901234567890;".encode("utf-8"))
result = lib.pop_string(server)
lib.shutdown(server)
print(result.decode("utf-8"))
