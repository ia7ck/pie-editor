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
        try:
            with open(path) as f:
                e.source_code.text = f.read()
                self.end(path)
        except OSError as err:
            print(err)
            # TODO: read() に失敗したとき何か表示する

    def write_to_file(self, file):
        e = self.editor
        name = os.path.basename(file)
        path = os.path.join(os.getcwd(), name)
        if self.has_file_created():
            path = self.filepath  # 上書き保存
        try:
            with open(path, "w") as f:
                f.write(e.source_code.text)
                self.end(path)
        except OSError as err:
            e.show_save_error(path, err.strerror)

    def end(self, path):
        self.filepath = path
        self.editor.update_footer(path)
        self.editor.dismiss_popup()

    def has_file_created(self):
        return len(self.filepath) > 0
