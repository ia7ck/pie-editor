import kivy.app
import kivy.clock
import kivy.core.window
import kivy.graphics
import kivy.properties
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.codeinput
import kivy.uix.label

import scanner
import server

# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")
# kivy.core.window.Window.size = (1920, 1020)  # 適当に大きめに設定しておく


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
        if self.editor.header.is_run_button_downed:
            self.focus = False  # ctrl+enter のときにこれをすると codeinput が変になる
        self.select_text(start=start, end=end)

    def keyboard_on_key_down(self, _window, keycode, _text, modifiers):
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "enter":
            self.editor.run_source_code()
            return True  # enter で改行しないために必要
        self.editor.footer.update_line_col_from_cursor(
            self.cursor_row + 1, self.cursor_col + 1
        )
        # call classmethod to edit source code properly
        kivy.uix.textinput.TextInput.keyboard_on_key_down(
            self, _window, keycode, _text, modifiers
        )


class Result(kivy.uix.boxlayout.BoxLayout):
    output_text = kivy.properties.StringProperty("")

    def update_output(self, new_text):
        self.output_text = new_text


class Footer(kivy.uix.boxlayout.BoxLayout):
    error_line_text = kivy.properties.StringProperty("")
    line_col_text = kivy.properties.StringProperty("Line:1 Col:1 ")

    def update_error_line(self, error_line_num):
        if error_line_num == -1:
            self.error_line_text = ""
        else:
            self.error_line_text = " Error at Line {}".format(error_line_num)

    def update_line_col_from_cursor(self, new_line, new_col):
        self.line_col_text = "Line:{} Col:{} ".format(new_line, new_col)


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


class Pie(kivy.app.App):
    def __init__(self):
        super(Pie, self).__init__()
        self.editor = None
        self.server = server.Server()

    def build(self):
        self.editor = Editor()  # ここで作る
        return self.editor

    def on_start(self):
        return
        self.server.start()

    def on_stop(self):
        return
        self.server.shutdown()


if __name__ == "__main__":
    app = Pie()
    app.run()
