# -*- encoding: utf-8 -*-

import locale
import os
import re
import urllib.request
import webbrowser

import kivy.app
import kivy.base
import kivy.clock
import kivy.core.clipboard
import kivy.core.text
import kivy.core.window
import kivy.graphics
import kivy.properties
import kivy.uix.actionbar
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.codeinput
import kivy.uix.image
import kivy.uix.label
import kivy.uix.popup
import kivy.utils
import pygments

import asirlexer
import asirserver
import coderunner
import filemanager
import outputanalyzer
from codebeautify.beautifier import AsirSyntaxError
from codebeautify.beautifier import Beautifier

# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")  # 右クリック時の赤丸を表示しない
kivy.core.window.Window.size = (900, 600)
# https://kivy.org/doc/stable/api-kivy.core.text.html#kivy.core.text.LabelBase.register
kivy.core.text.LabelBase.register("M+ P Type-1 Regular", "./mplus-1p-regular.ttf")
kivy.core.text.LabelBase.register("M+ M Type-1 Regular", "./mplus-1m-regular.ttf")

FONT_SIZE = 24  # LABEL_FONT_SIZE in pie.kv


class FileOpenDialog(kivy.uix.boxlayout.BoxLayout):
    editor = kivy.properties.ObjectProperty(None)


class FileSaveDialog(kivy.uix.boxlayout.BoxLayout):
    editor = kivy.properties.ObjectProperty(None)


class ImageViewer(kivy.uix.boxlayout.BoxLayout):
    source = kivy.properties.StringProperty("")
    editor = kivy.properties.ObjectProperty(None)


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
        e = self.editor
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "enter":
            e.coderunner.run_source_code()
            return True  # enter で改行しないために必要
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "s":
            e.handle_file_save()
            return True
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "b":
            e.beautify_source_code()
            return True
        e.footer.update_line_col_from_cursor(self.cursor_row + 1, self.cursor_col + 1)
        # https://kivy.org/doc/stable/examples/gen__demo__kivycatalog__main__py.html
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
        y = touch.pos[1]
        # https://kivy.org/doc/stable/api-kivy.uix.widget.html#kivy.uix.widget.Widget.top
        if self.y <= y and y <= self.top:  # source_code がクリックされたか
            if touch.button == "right":
                self._show_cut_copy_paste(
                    touch.pos, kivy.base.EventLoop.window, mode="paste"
                )


class ResultHeader(kivy.uix.boxlayout.BoxLayout):
    pass


class Result(kivy.uix.boxlayout.BoxLayout):
    editor = kivy.properties.ObjectProperty(None)
    text = kivy.properties.StringProperty("")

    def __init__(self, **kwargs):
        super(Result, self).__init__(**kwargs)
        self.imagefile_path = ""

    def on_touch_down(self, touch):
        super(Result, self).on_touch_down(touch)
        y = touch.pos[1]
        if self.y <= y and y <= self.top:  # result がクリックされたか
            if touch.button == "left":
                if self.imagefile_path:
                    self.editor.show_image(self.imagefile_path)


class Footer(kivy.uix.boxlayout.BoxLayout):
    error_message = kivy.properties.ObjectProperty(None)
    line_col = kivy.properties.ObjectProperty(None)

    def show_error_line_number(self, error_line_num):
        if error_line_num == -1:
            self.error_message.text = ""
        else:
            self.error_message.text = "Error at Line {}".format(error_line_num)

    def update_line_col_from_cursor(self, new_line, new_col):
        self.line_col.text = "Line:{} Col:{}".format(new_line, new_col)


class Editor(kivy.uix.boxlayout.BoxLayout):
    header = kivy.properties.ObjectProperty(None)
    source_code = kivy.properties.ObjectProperty(None)
    footer = kivy.properties.ObjectProperty(None)
    result = kivy.properties.ObjectProperty(None)
    # https://kivy.org/doc/stable/guide/lang.html#rule-context
    app = kivy.properties.ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Editor, self).__init__(**kwargs)
        self.server = None
        self.coderunner = coderunner.CodeRunner(editor=self)
        self.filemanager = filemanager.FileManager(editor=self)
        # https://kivy.org/doc/stable/api-kivy.clock.html#kivy.clock.CyClockBase.create_trigger
        self.clock_event = kivy.clock.Clock.create_trigger(
            lambda _dt: self.coderunner.fetch_result(), 1, interval=True
        )

    def open_link(self, url):
        lang_code = locale.getlocale()[0]
        if lang_code != "ja_JP":
            url = url.replace("ja", "en")
        # https://docs.python.org/ja/3/library/webbrowser.html
        webbrowser.open(url)

    def beautify_source_code(self):
        try:
            b = Beautifier(self.source_code.text)
            self.source_code.text = b.beautify()
        except AsirSyntaxError as err:
            self.footer.error_message.text = err.message

    def generate_html(self):
        path = os.path.join(os.environ["HOME"], "output.html")
        current_file_path = self.filemanager.filepath
        if current_file_path:
            path = os.path.splitext(current_file_path)[0] + ".html"
        with open(path, "w") as f:
            pygments.highlight(
                self.source_code.text,
                asirlexer.AsirLexer(),
                pygments.formatters.get_formatter_by_name(
                    "html", linenos=True, full=True
                ),
                outfile=f,
            )
            webbrowser.open("file:" + urllib.request.pathname2url(path))

    def copy_to_clipboard(self):
        kivy.core.clipboard.Clipboard.copy(self.result.text)

    def show_execute_error(self, res):
        # TODO: selection 部分だけ実行したときにエラー行がずれるので直す
        error_line_num = outputanalyzer.find_error_line(res)
        self.footer.show_error_line_number(error_line_num)
        self.source_code.select_error_line(error_line_num)

    def update_result(self, res):
        r = self.result
        escape = kivy.utils.escape_markup
        path = outputanalyzer.find_imagefile_path(res)
        r.imagefile_path = path
        if path:
            # https://kivy.org/doc/stable/api-kivy.utils.html#kivy.utils.escape_markup
            p = escape(path)
            r.text = escape(res).replace(p, "[u]" + p + "[/u]")
        else:
            r.text = res

    # ファイル関係
    def show_files(self):
        self.popup = kivy.uix.popup.Popup(
            title="Open File", size_hint=(0.8, 0.8), content=FileOpenDialog(editor=self)
        )
        self.popup.open()

    def show_filename_input_form(self):
        self.popup = kivy.uix.popup.Popup(
            title="Save File", size_hint=(0.8, 0.8), content=FileSaveDialog(editor=self)
        )
        self.popup.open()

    def update_footer(self, filepath):
        app.title = "Pie -- " + filepath
        self.footer.filename.text = os.path.basename(filepath)

    def dismiss_popup(self):
        self.popup.dismiss()

    def handle_file_save(self):  # 上書き or 新規作成
        fm = self.filemanager
        if fm.has_file_created():
            fm.write_to_file(dirname="", filepath=fm.filepath)
        else:
            self.show_filename_input_form()

    def show_image(self, path):
        self.popup = kivy.uix.popup.Popup(
            title=path,
            size_hint=(0.8, 0.8),
            content=ImageViewer(source=path, editor=self),
        )
        self.popup.open()


class Pie(kivy.app.App):
    def __init__(self):
        super(Pie, self).__init__()
        self.editor = None

    def build(self):
        self.editor = Editor()  # ここで作る
        return self.editor

    def on_start(self):
        e = self.editor
        try:
            e.server = asirserver.Server()
        except OSError as err:
            print("Asir サーバを起動できませんでした。環境変数 OpenXM_HOME が正しく設定されているか確認してください。")
            import traceback

            print(traceback.format_exc())
            self.stop()
        if e.server:
            e.server.start()

    def on_stop(self):
        e = self.editor
        if e.server:
            e.server.shutdown()


if __name__ == "__main__":
    app = Pie()
    app.run()
