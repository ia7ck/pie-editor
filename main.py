import os

import kivy.app
import kivy.core.window
import kivy.graphics
import kivy.properties
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.codeinput
import kivy.uix.label
import kivy.uix.popup

import scanner
import server

# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")
# kivy.core.window.Window.size = (1920, 1020)  # 適当に大きめに設定しておく

FONT_SIZE = 24


class FileOpenDialog(kivy.uix.boxlayout.BoxLayout):
    load_file = kivy.properties.ObjectProperty(None)
    cancel = kivy.properties.ObjectProperty(None)


class FileSaveDialog(kivy.uix.boxlayout.BoxLayout):
    save_file = kivy.properties.ObjectProperty(None)
    cancel = kivy.properties.ObjectProperty(None)


class LabelWithBackgroundColor(kivy.uix.label.Label):
    background_color = kivy.properties.ListProperty((0.5, 0.5, 0.5, 1))


class Header(kivy.uix.boxlayout.BoxLayout):
    pass


class SourceCode(kivy.uix.codeinput.CodeInput):
    def select_error_line(self, error_line_num):
        if error_line_num == -1:
            return
        lines = self.text.splitlines()
        if len(lines) < error_line_num:
            return
        start = sum([len(line) + 1 for line in lines[: error_line_num - 1]])
        end = sum([len(line) + 1 for line in lines[:error_line_num]]) - 1
        if self.is_run_button_downed:
            self.focus = False  # ctrl+enter のときにこれをすると codeinput が変になる
        self.select_text(start=start, end=end)

    def keyboard_on_key_down(self, _window, keycode, _text, modifiers):
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "enter":
            self.run_source_code()
            return True  # enter で改行しないために必要
        self.update_line_col_from_cursor(self.cursor_row + 1, self.cursor_col + 1)
        # call classmethod to edit source code properly
        kivy.uix.textinput.TextInput.keyboard_on_key_down(
            self, _window, keycode, _text, modifiers
        )

    def update_source_code(self, new_text):
        self.text = new_text


class Result(kivy.uix.boxlayout.BoxLayout):
    output = kivy.properties.ObjectProperty(None)

    def update_output(self, new_text):
        self.output.text = new_text


class Footer(kivy.uix.boxlayout.BoxLayout):
    error_line = kivy.properties.ObjectProperty(None)
    line_col = kivy.properties.ObjectProperty(None)

    def update_error_line(self, error_line_num):
        if error_line_num == -1:
            self.error_line.text = ""
        else:
            self.error_line.text = " Error at Line {}".format(error_line_num)

    def update_line_col_from_cursor(self, new_line, new_col):
        self.line_col.text = "Line:{} Col:{} ".format(new_line, new_col)


class Editor(kivy.uix.boxlayout.BoxLayout):
    header = kivy.properties.ObjectProperty(None)
    source_code = kivy.properties.ObjectProperty(None)
    footer = kivy.properties.ObjectProperty(None)
    result = kivy.properties.ObjectProperty(None)

    def run_source_code(self, *args):
        server_input = "if (1) { " + self.source_code.text + " };"
        app.server.execute_string(server_input)
        server_output = app.server.pop_string()
        self.result.update_output(server_output)
        error_line_num = scanner.get_error_line(server_output)
        self.footer.update_error_line(error_line_num)
        self.source_code.select_error_line(error_line_num)

    def show_files(self):
        self.popup = kivy.uix.popup.Popup(
            title="Open File",
            size_hint=(0.8, 0.8),
            content=FileOpenDialog(load_file=self.load_file, cancel=self.dismiss_popup),
        )
        self.popup.open()

    def load_file(self, filenames):
        if len(filenames) == 0:
            return
        with open(filenames[0]) as f:
            self.source_code.update_source_code(f.read())
        self.dismiss_popup()

    def show_filename_form(self):
        self.popup = kivy.uix.popup.Popup(
            title="Save File",
            size_hint=(0.8, None),
            height=FONT_SIZE * 7.5,
            content=FileSaveDialog(save_file=self.save_file, cancel=self.dismiss_popup),
        )
        self.popup.open()

    def save_file(self, filename):
        filepath = os.path.join(os.getcwd(), filename)
        try:
            with open(filepath, "w") as f:
                f.write(self.source_code.text)
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


class Pie(kivy.app.App):
    def __init__(self):
        super(Pie, self).__init__()
        self.editor = None
        self.server = server.Server()

    def build(self):
        self.editor = Editor()  # ここで作る
        return self.editor

    def on_start(self):
        self.server.start()

    def on_stop(self):
        self.server.shutdown()


if __name__ == "__main__":
    app = Pie()
    app.run()
