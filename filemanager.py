import sys
import os


class FileManager:
    def __init__(self, editor):
        self.editor = editor
        self.filepath = ""

    def load_file(self, filepaths):
        e = self.editor
        if len(filepaths) == 0:
            return
        path = filepaths[0]
        with open(path) as f:
            e.source_code.text = f.read()
        # TODO: read() に失敗したとき何か表示する
        self.filepath = path
        e.dismiss_popup()

    def write_to_file(self, filename):
        e = self.editor
        path = self.filepath
        if not self.has_file_created():
            path = os.path.join(os.getcwd(), filename)  # 新規作成
        try:
            with open(path, "w") as f:
                f.write(e.source_code.text)
            self.filepath = path
            e.dismiss_popup()
        except OSError as e:
            e.show_save_error(self.filepath, e.strerror)

    def has_file_created(self):
        return len(self.filepath) > 0

    def get_filename(self):
        return os.path.basename(self.filepath)
