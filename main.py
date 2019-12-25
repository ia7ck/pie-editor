# -*- encoding: utf-8 -*-

import bisect
import itertools
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
import kivy.logger
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
from codebeautify.beautifier import AsirSyntaxError, Beautifier

root_dir = os.path.dirname(__file__)

# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")  # 右クリック時の赤丸を表示しない
kivy.core.window.Window.size = (900, 600)
# https://kivy.org/doc/stable/api-kivy.core.text.html#kivy.core.text.LabelBase.register
kivy.core.text.LabelBase.register(
    "M+ P Type-1 Regular", os.path.join(root_dir, "./static/mplus-1p-regular.ttf"),
)
kivy.core.text.LabelBase.register(
    "M+ M Type-1 Regular", os.path.join(root_dir, "./static/mplus-1m-regular.ttf"),
)

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

    # error_line_num: 1-indexed
    def select_error_line(self, error_line_num):
        if error_line_num == -1:
            return
        lines = self.text.splitlines()
        if len(lines) < error_line_num:
            return
        self.cursor = (0, error_line_num - 1)
        start = sum([len(line) + 1 for line in lines[: error_line_num - 1]])
        end = sum([len(line) + 1 for line in lines[:error_line_num]]) - 1
        self.select_text(start=start, end=end)

    def comment_out(self):
        c = self.cursor  # keep
        lines = self.text.splitlines(keepends=True)
        acc_char_count = [0] + list(itertools.accumulate([len(l) for l in lines]))
        acc_char_count[-1] += 1
        f, t = (
            min(self.selection_from, self.selection_to),
            max(self.selection_from, self.selection_to),
        )
        num_add_comment = 0
        for i in range(len(lines)):
            # TODO: use `bisect` module instead
            if (
                (acc_char_count[i] <= f < acc_char_count[i + 1])
                or (f <= acc_char_count[i] < t)
                or (acc_char_count[i] <= t < acc_char_count[i + 1])
            ):
                if lines[i].strip().startswith("//"):  # uncomment
                    lines[i] = lines[i].replace("//", "")
                    num_add_comment -= 1
                else:
                    space = re.search(r"(\s*).*$", lines[i]).group(1)
                    lines[i] = space + "//" + lines[i].lstrip(" ")
                    num_add_comment += 1
        self.text = "".join(lines)
        self.cursor = c  # revert
        if f < t:
            self.select_text(start=f, end=t + num_add_comment * 2)

    def keyboard_on_key_down(self, _window, keycode, _text, modifiers):
        e = self.editor
        e.footer.update_line_col_from_cursor(self.cursor_row + 1, self.cursor_col + 1)
        if len(modifiers) == 1 and modifiers[0] == "ctrl":
            if keycode[1] == "enter":
                e.coderunner.run_source_code()
                return True  # enter で改行しないために必要
            if keycode[1] == "s":
                e.handle_file_save()
                return True
            if keycode[1] == "b":
                e.beautify_source_code()
                return True
            if keycode[1] == "/":
                self.comment_out()
                return True
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

    def on_touch_up(self, touch):
        # https://kivy.org/doc/stable/api-kivy.uix.widget.html#kivy.uix.widget.Widget.collide_point
        if self.collide_point(*touch.pos):  # source_code がクリックされたか
            if touch.button == "right":
                self._show_cut_copy_paste(
                    touch.pos, kivy.base.EventLoop.window, mode="paste"
                )
        return super(SourceCode, self).on_touch_up(touch)


class ResultHeader(kivy.uix.boxlayout.BoxLayout):
    pass


class Result(kivy.uix.boxlayout.BoxLayout):
    editor = kivy.properties.ObjectProperty(None)
    text = kivy.properties.StringProperty("")

    def __init__(self, **kwargs):
        super(Result, self).__init__(**kwargs)
        self.imagefile_path = ""

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):  # result がクリックされたか
            if touch.button == "left":
                if self.imagefile_path:
                    self.editor.show_image(self.imagefile_path)
        return super(Result, self).on_touch_up(touch)


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

    def inform_unsaved_changes(self):
        f = self.filename
        if f.text:
            f.text = "*" + f.text.lstrip("*")

    def update_filename(self, newname):
        self.filename.text = newname


class Editor(kivy.uix.boxlayout.BoxLayout):
    header = kivy.properties.ObjectProperty(None)
    source_code = kivy.properties.ObjectProperty(None)
    footer = kivy.properties.ObjectProperty(None)
    result = kivy.properties.ObjectProperty(None)
    # https://kivy.org/doc/stable/guide/lang.html#rule-context
    app = kivy.properties.ObjectProperty(None)
    # https://kivy.org/doc/stable/guide/events.html#declaration-of-a-property
    filepath = kivy.properties.StringProperty("")

    def __init__(self, filepath="", **kwargs):
        super(Editor, self).__init__(**kwargs)
        self.server = None
        self.coderunner = coderunner.CodeRunner(editor=self)
        self.filemanager = filemanager.FileManager(editor=self)
        # TODO: filemanager.py に移動させる
        if len(filepath) > 0:
            try:
                self.filemanager.load_file(filepath)
            except OSError as err:
                kivy.logger.Logger.error(err)
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
        c = self.source_code.cursor
        try:
            b = Beautifier(self.source_code.text)
            self.source_code.text = b.beautify()
            self.source_code.cursor = c
        except AsirSyntaxError as err:
            self.footer.error_message.text = err.message

    def generate_html(self):
        path = os.path.join(os.getcwd(), "output.html")
        current_file_path = self.filepath
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

    def dismiss_popup(self):
        self.popup.dismiss()

    # self.filepath が変更されたら呼ばれる
    def on_filepath(self, _, path):
        self.app.title = "Pie -- " + path

    def handle_select_files(self, filepath_list):
        if len(filepath_list) == 0:
            return
        path = filepath_list[0]
        try:
            self.filemanager.load_file(path)
            self.dismiss_popup()
        except OSError as err:
            kivy.logger.Logger.error(err)

    def handle_input_filename(self, dirname, basename):
        path = os.path.join(dirname, basename)
        try:
            self.filemanager.write_to_file(path, self.source_code.text)
            self.dismiss_popup()
        except OSError as err:
            kivy.logger.Logger.error(err)

    def handle_file_save(self):  # 上書き or 新規作成
        if self.filepath:
            try:
                self.filemanager.write_to_file(self.filepath, self.source_code.text)
            except OSError as err:
                kivy.logger.Logger.error(err)
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
    def __init__(self, **kwargs):
        super(Pie, self).__init__()
        self.editor = None
        self.kwargs = kwargs

    def build(self):
        self.editor = Editor(**self.kwargs)  # ここで作る
        return self.editor

    def on_start(self):
        e = self.editor
        try:
            e.server = asirserver.Server()
        except OSError as err:
            kivy.logger.Logger.error(
                "Asir サーバを起動できませんでした。環境変数 OpenXM_HOME が正しく設定されているか確認してください。"
            )
            kivy.logger.Logger.error(err)
            self.stop()
        if e.server:
            e.server.start()

    def on_stop(self):
        e = self.editor
        if e.server:
            e.server.shutdown()


def main():
    import sys, os

    if len(sys.argv) == 2:
        filepath = os.path.join(os.getcwd(), sys.argv[1])
        app = Pie(filepath=filepath)
    else:
        app = Pie()
    app.run()


if __name__ == "__main__":
    main()
