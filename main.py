import textwrap

import kivy.app
import kivy.config
import kivy.core.window
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.codeinput
import kivy.uix.label
import kivy.uix.textinput

import lexer
import scanner
import server

# 右クリックで丸が出るのを防ぐ
# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")

# kivy.core.window.Window.clearcolor = (1, 1, 1, 1)  # 背景を白に
kivy.core.window.Window.size = (1920, 1020)  # 適当に大きめに設定しておく

FONT_NAME = "RictyDiminished-Regular.ttf"
FONT_SIZE = 24


class LabelWithBackgroundColor(kivy.uix.label.Label):
    def __init__(self, background_color=(1, 1, 1, 1), **kwargs):
        super(LabelWithBackgroundColor, self).__init__(
            font_name=FONT_NAME, font_size=FONT_SIZE, **kwargs
        )
        self.background_color = background_color

    def on_size(self, _label, _size):  # Widget の method ?
        self.canvas.before.clear()
        with self.canvas.before:
            kivy.graphics.Color(*self.background_color)
            kivy.graphics.Rectangle(pos=self.pos, size=self.size)

    def on_pos(self, _label, _pos):
        self.canvas.before.clear()
        with self.canvas.before:
            kivy.graphics.Color(*self.background_color)
            kivy.graphics.Rectangle(pos=self.pos, size=self.size)


class Header(kivy.uix.boxlayout.BoxLayout):
    def __init__(self, on_button_press):
        super(Header, self).__init__(
            size_hint_y=None, height=FONT_SIZE * 2, orientation="horizontal"
        )
        self.run_button = kivy.uix.button.Button(
            text="Run",
            on_press=on_button_press,
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.add_widget(self.run_button)


class SourceCode(kivy.uix.codeinput.CodeInput):
    # source code edit
    def __init__(self, on_ctrl_enter, on_cursor_move):
        super(SourceCode, self).__init__(
            text=textwrap.dedent(
                """\
                /* comment */
                /* /* 入れ子 */ */
                if (0) {
                    car([]);
                    X2 = x_0 ^ 2;
                }
                def f(A) {
                    return A * 2;
                }
                f(10) + f(100);
                """
            ),
            cursor_width=3,
            cursor_color=(0.25, 0.25, 0.25, 1),
            cursor_blink=False,
            lexer=lexer.AsirLexer(),  # for syntax highlight
            background_normal=kivy.uix.textinput.TextInput.background_active.defaultvalue,  # light background color
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
            on_touch_up=self._on_touch_up,
        )
        self.on_ctrl_enter = on_ctrl_enter
        self.on_cursor_move = on_cursor_move

    def keyboard_on_key_down(self, _window, keycode, _text, modifiers):
        if len(modifiers) == 1 and modifiers[0] == "ctrl" and keycode[1] == "enter":
            self.on_ctrl_enter()
            return True
        self.on_cursor_move(
            self.cursor_row + 1, self.cursor_col + 1
        )  # send new cursor position (line, col)

        # call classmethod to edit source code properly
        kivy.uix.textinput.TextInput.keyboard_on_key_down(
            self, _window, keycode, _text, modifiers
        )

    def _on_touch_up(self, _touched_object, _touch):
        self.on_cursor_move(self.cursor_row + 1, self.cursor_col + 1)

    def select_error_line(self, error_line_num):
        if error_line_num == -1:
            return
        lines = self.text.splitlines()
        if len(lines) < error_line_num:
            return
        start = sum([len(line) + 1 for line in lines[: error_line_num - 1]]) - 1
        end = sum([len(line) + 1 for line in lines[:error_line_num]]) - 1
        self.focus = False
        self.select_text(start=start, end=end)


class Footer(kivy.uix.boxlayout.BoxLayout):
    def __init__(self, **kwargs):
        super(Footer, self).__init__(orientation="horizontal", **kwargs)
        self.error_line = LabelWithBackgroundColor(
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.8, 0, 0, 1),
            text="",
            halign="left",
            valign="middle",
        )
        self.line_col = LabelWithBackgroundColor(
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1),
            text="Line:1 Col:1 ",
            halign="right",
            valign="middle",
        )
        self.line_col.bind(size=self.line_col.setter("text_size"))  # alginment のため
        self.error_line.bind(size=self.error_line.setter("text_size"))
        self.add_widget(self.error_line)
        self.add_widget(self.line_col)

    def update_line_col_from_cursor(self, new_line, new_col):
        self.line_col.text = "Line:{} Col:{} ".format(new_line, new_col)

    def update_error_line(self, error_line_num):
        if error_line_num == -1:
            self.error_line.text = ""
        else:
            self.error_line.text = " Error at Line {}".format(error_line_num)


class RunResult(kivy.uix.boxlayout.BoxLayout):
    def __init__(self, **kwargs):
        super(RunResult, self).__init__(**kwargs)
        self.label = LabelWithBackgroundColor(
            background_color=(0.3, 0.3, 0.3, 1),
            text=" Output (read only)",
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        self.label.bind(size=self.label.setter("text_size"))  # alignment のため
        self.label_layout = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=None, height=FONT_SIZE * 1.5
        )  # height 指定のため
        self.label_layout.add_widget(self.label)
        self.add_widget(self.label_layout)
        self.output = kivy.uix.textinput.TextInput(
            text="",
            readonly=True,
            cursor_width=0,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.add_widget(self.output)

    def update_output(self, response):
        self.output.text = response


class Editor(kivy.uix.boxlayout.BoxLayout):
    def __init__(self):
        super(Editor, self).__init__(orientation="vertical")

        self.server = None

        # run_button, TODO: file
        self.header = Header(on_button_press=self.run_source_code)
        self.footer = Footer(size_hint_y=None, height=FONT_SIZE * 1.5)
        self.add_widget(self.header)
        # source code, TODO: line_number
        self.editor = kivy.uix.boxlayout.BoxLayout(orientation="horizontal")
        self.source_code = SourceCode(
            on_ctrl_enter=self.run_source_code,
            on_cursor_move=self.footer.update_line_col_from_cursor,
        )
        self.editor.add_widget(self.source_code)
        self.add_widget(self.editor)
        # line/column number
        self.add_widget(self.footer)
        # label, output
        self.result = RunResult(size_hint_y=0.4, orientation="vertical")
        self.add_widget(self.result)

    def run_source_code(self, *args):  # run_button が渡される
        text = "if (1) { " + self.source_code.text + " };"
        self.server.execute_string(text)
        response = self.server.pop_string()
        self.result.update_output(response)
        error_line_num = scanner.get_error_line(response)
        self.footer.update_error_line(error_line_num)
        self.source_code.select_error_line(error_line_num)


class Pie(kivy.app.App):
    def __init__(self):
        super(Pie, self).__init__()
        self.editor = Editor()

    def build(self):
        return self.editor


if __name__ == "__main__":
    app = Pie()
    asir_server = server.Server()
    asir_server.start()
    app.editor.server = asir_server
    app.run()
    asir_server.shutdown()
