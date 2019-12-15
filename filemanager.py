import os

import kivy.clock


class FileManager:
    def __init__(self, editor):
        self.editor = editor

    def load_file(self, path):
        with open(path) as f:
            self.editor.source_code.text = f.read()
            self.editor.filepath = path
            # SourceCode.on_text のあとに更新する
            kivy.clock.Clock.schedule_once(
                lambda _dt: self.editor.footer.update_filename(os.path.basename(path))
            )

    def write_to_file(self, path, text):
        with open(path, "w") as f:
            f.write(text)
            self.editor.filepath = path
            # Editor に書くほうがいいかも?
            self.editor.footer.update_filename(os.path.basename(path))
