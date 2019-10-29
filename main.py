# -*- encoding: utf-8 -*-

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "./codebeautify"))

import kivy.app
import kivy.base
import kivy.clock
import kivy.core.text
import kivy.core.window
import kivy.graphics
import kivy.properties
import kivy.uix.actionbar
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.codeinput
import kivy.uix.label
import kivy.uix.popup

import erroranalyzer
import server
from codebeautify import beautifier


# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")  # 右クリック時の赤丸を表示しない
kivy.core.window.Window.size = (800, 600)
kivy.core.text.LabelBase.register("M+ P Type-1 Regular", "./mplus-1p-regular.ttf")
kivy.core.text.LabelBase.register("M+ M Type-1 Regular", "./mplus-1m-regular.ttf")

FONT_SIZE = 24  # LABEL_FONT_SIZE in pie.kv


class FileOpenDialog(kivy.uix.boxlayout.BoxLayout):
    editor = kivy.properties.ObjectProperty(None)


class FileSaveDialog(kivy.uix.boxlayout.BoxLayout):
    editor = kivy.properties.ObjectProperty(None)


class LabelWithBackgroundColor(kivy.uix.label.Label):
    background_color = kivy.properties.ListProperty((0.5, 0.5, 0.5, 1))  # default


class Header(kivy.uix.actionbar.ActionBar):
    editor = kivy.properties.ObjectProperty(None)


class SourceCode(kivy.uix.codeinput.CodeInput):
    editor = kivy.properties.ObjectProperty(None)

    def select_error_line(self, error_line_num):
        if error_line_num == -1:
            return
        lines = self.text.splitlines()
        if len(lines) < error_line_num:
            return
        start = sum([len(line) + 1 for line in lines[: error_line_num - 1]])
        end = sum([len(line) + 1 for line in lines[:error_line_num]]) - 1
        self.select_text(start=start, end=end)

    def keyboard_on_key_down(self, _window, keycode, _text, modifiers):
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "enter":
            self.editor.run_source_code()
            return True  # enter で改行しないために必要
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "s":
            self.editor.handle_file_save()
            return True
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "b":
            self.editor.beautify_source_code()
            return True
        self.editor.footer.update_line_col_from_cursor(
            self.cursor_row + 1, self.cursor_col + 1
        )
        # https://pyky.github.io/kivy-doc-ja/examples/gen__demo__kivycatalog__main__py.html
        # https://kivy.org/doc/stable/api-kivy.uix.behaviors.focus.html#kivy.uix.behaviors.focus.FocusBehavior.keyboard_on_key_down
        return super(SourceCode, self).keyboard_on_key_down(
            _window, keycode, _text, modifiers
        )

    def keyboard_on_key_up(self, _window, _keycode):
        self.editor.footer.update_line_col_from_cursor(
            self.cursor_row + 1, self.cursor_col + 1
        )
        return super(SourceCode, self).keyboard_on_key_up(_window, _keycode)

    def on_touch_down(self, touch):
        super(SourceCode, self).on_touch_down(touch)
        if touch.button == "right":
            self._show_cut_copy_paste(
                touch.pos, kivy.base.EventLoop.window, mode="paste"
            )


class Result(kivy.uix.boxlayout.BoxLayout):
    pass


class Footer(kivy.uix.boxlayout.BoxLayout):
    error_line = kivy.properties.ObjectProperty(None)
    line_col = kivy.properties.ObjectProperty(None)

    def update_error_line(self, error_line_num):
        if error_line_num == -1:
            self.error_line.text = ""
        else:
            self.error_line.text = "Error at Line {}".format(error_line_num)

    def update_line_col_from_cursor(self, new_line, new_col):
        self.line_col.text = "Line:{} Col:{}".format(new_line, new_col)


class Editor(kivy.uix.boxlayout.BoxLayout):
    header = kivy.properties.ObjectProperty(None)
    source_code = kivy.properties.ObjectProperty(None)
    footer = kivy.properties.ObjectProperty(None)
    result = kivy.properties.ObjectProperty(None)
    filepath = kivy.properties.StringProperty("")

    def __init__(self, **kwargs):
        super(Editor, self).__init__(**kwargs)
        # https://pyky.github.io/kivy-doc-ja/api-kivy.clock.html#kivy.clock.CyClockBase.create_trigger
        self.clock_event = kivy.clock.Clock.create_trigger(
            lambda _dt: self.fetch_result(), 1, interval=True
        )

    def run_source_code(self, *args):
        app.server.reset()
        self.clock_event.cancel()
        self.result.output.text = "running ..."
        self.footer.error_line.text = ""
        selection = self.source_code.selection_text
        server_input = (
            "if (1) { "
            + (selection if len(selection) > 0 else self.source_code.text)
            + " } else {};"
        )
        app.server.execute_string(server_input)
        self.clock_event()

    def fetch_result(self):
        finished = True if app.server.select() != 0 else False
        if finished:
            res = app.server.pop_string()
            self.result.output.text = res
            error_line_num = erroranalyzer.get_error_line(res)
            # TODO: selection 部分だけ実行したときにエラー行がずれるので直す
            self.footer.update_error_line(error_line_num)
            self.source_code.select_error_line(error_line_num)
            self.clock_event.cancel()
        else:
            self.result.output.text += " ..."

    def stop_running(self, *args):
        app.server.reset()
        self.clock_event.cancel()
        self.result.output.text = "stopped"

    def beautify_source_code(self, *args):
        b = beautifier.Beautifier(self.source_code.text)
        self.source_code.text = b.beautify()

    # ファイル関係
    def show_files(self):
        self.popup = kivy.uix.popup.Popup(
            title="Open File", size_hint=(0.8, 0.8), content=FileOpenDialog(editor=self)
        )
        self.popup.open()

    def load_file(self, filepaths):
        if len(filepaths) == 0:
            return
        with open(filepaths[0]) as f:
            self.source_code.text = f.read()
        self.filepath = filepaths[0]
        self.dismiss_popup()

    def show_filename_input_form(self):
        self.popup = kivy.uix.popup.Popup(
            title="Save File",
            size_hint=(0.8, None),
            height=FONT_SIZE * 7.5,
            content=FileSaveDialog(editor=self),
        )
        self.popup.open()

    def write_source_code_to_file(self, filename):
        filepath = (
            self.filepath  # 上書き
            if self.has_file_created()
            else os.path.join(os.getcwd(), filename)  # 新規作成
        )
        try:
            with open(filepath, "w") as f:
                f.write(self.source_code.text)
            self.filepath = filepath
            self.dismiss_popup()
        except OSError as e:
            self.show_save_error(filepath, e.strerror)

    def show_save_error(self, filepath, message):
        self.popup.height = FONT_SIZE * 16
        self.popup.content.error_hint.text = "Failed to save: {}\n[color=FF0000]{}[/color]".format(
            filepath, message
        )

    def dismiss_popup(self):
        self.popup.dismiss()

    def has_file_created(self):
        return len(self.filepath) > 0

    def get_filename(self):
        return os.path.basename(self.filepath)

    def handle_file_save(self):  # 上書き or 新規作成
        if self.has_file_created():
            self.write_source_code_to_file(self.get_filename())
        else:
            self.show_filename_input_form()

    def on_filepath(self, *args):
        app.title = "Pie -- " + self.filepath
        self.footer.filename.text = self.get_filename()


class Pie(kivy.app.App):
    def __init__(self):
        super(Pie, self).__init__()
        self.editor = None
        self.server = None

    def build(self):
        self.editor = Editor()  # ここで作る
        return self.editor

    def on_start(self):
        try:
            self.server = server.Server()
        except OSError as e:
            print("Asir サーバを起動できませんでした。環境変数 OpenXM_HOME が正しく設定されているか確認してください。")
            import traceback

            print(traceback.format_exc())
            self.stop()
        if self.server:
            self.server.start()

    def on_stop(self):
        if self.server:
            self.server.shutdown()


if __name__ == "__main__":
    app = Pie()
    app.run()
