import os


class FileManager:
    def __init__(self, editor):
        self.editor = editor
        self.filepath = ""

    def load_file(self, filepath_list):
        e = self.editor
        if len(filepath_list) == 0:
            return
        path = filepath_list[0]
        try:
            with open(path) as f:
                e.source_code.text = f.read()
                self.end(path)
        except OSError as err:
            print(err)
            # TODO: read() に失敗したとき何か表示する

    def write_to_file(self, dirname, filepath):
        e = self.editor
        path = os.path.join(dirname, filepath)
        if self.has_file_created():
            path = self.filepath  # 上書き保存
        try:
            with open(path, "w") as f:
                f.write(e.source_code.text)
                self.end(path)
        except OSError as err:
            print(err)
            # TODO: write() に失敗したとき何か表示する

    def end(self, path):
        self.filepath = path
        self.editor.update_footer(path)
        self.editor.dismiss_popup()

    def has_file_created(self):
        return len(self.filepath) > 0
