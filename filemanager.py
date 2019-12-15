class FileManager:
    def __init__(self, editor):
        self.editor = editor

    def load_file(self, path):
        with open(path) as f:
            self.editor.source_code.text = f.read()
            self.editor.filepath = path

    def write_to_file(self, path, text):
        with open(path, "w") as f:
            f.write(text)
            self.editor.filepath = path
