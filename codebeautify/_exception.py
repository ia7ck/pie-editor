class CodeBeautifierError(Exception):
    pass


class AsirSyntaxError(CodeBeautifierError):
    def __init__(self, message):
        self.message = message
