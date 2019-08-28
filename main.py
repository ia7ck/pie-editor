import server

if __name__ == "__main__":
    asir_server = server.Server()
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
