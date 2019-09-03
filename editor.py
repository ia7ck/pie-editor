import kivy.app
import kivy.uix.scrollview
import kivy.config
import kivy.core.window
import kivy.uix.codeinput
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.textinput
import kivy.uix.widget
import kivy.uix.label
import kivy.uix.anchorlayout

import textwrap
import server
import lexer

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
        self.ctrl_down = False

    def keyboard_on_key_down(self, _window, keycode, _text, _modifiers):
        if self.ctrl_down and ("enter" in keycode[1]):
            self.on_ctrl_enter()
            return True
        if "ctrl" in keycode[1]:
            self.ctrl_down = True
        # call classmethod to edit source code properly
        kivy.uix.textinput.TextInput.keyboard_on_key_down(
            self, _window, keycode, _text, _modifiers
        )

    def keyboard_on_key_up(self, _window, keycode):
        self.on_cursor_move(
            self.cursor_row + 1, self.cursor_col + 1
        )  # send new cursor position (line, col)
        if "ctrl" in keycode[1]:
            self.ctrl_down = False
        kivy.uix.textinput.TextInput.keyboard_on_key_up(self, _window, keycode)

    def _on_touch_up(self, _touched_object, _touch):
        self.on_cursor_move(self.cursor_row + 1, self.cursor_col + 1)
        return False  # not to stop dispatching touch event


class Footer(kivy.uix.boxlayout.BoxLayout):
    def __init__(self, **kwargs):
        super(Footer, self).__init__(orientation="horizontal", **kwargs)
        self.line_col = LabelWithBackgroundColor(
            background_color=(0.92, 0.9, 0.9, 1),
            color=(0, 0, 0, 1),
            text="Line:1 Col:1",
            halign="right",
            valign="middle",
        )
        self.line_col.bind(size=self.line_col.setter("text_size"))  # algin を有効にするため
        self.add_widget(self.line_col)


class Editor(kivy.uix.boxlayout.BoxLayout):
    def update_line_col_from_cursor(self, new_line, new_col):
        self.footer.line_col.text = "Line:{} Col:{}".format(new_line, new_col)

    def __init__(self, **kwargs):
        super(Editor, self).__init__(orientation="vertical")
        self.server = kwargs["lang_server"]
        # file, run_button, line, col
        self.header = Header(on_button_press=self.run_source_code)
        self.add_widget(self.header)
        # editor
        self.editor = kivy.uix.boxlayout.BoxLayout(orientation="horizontal")
        # TODO: line_number
        # source_code
        self.source_code = SourceCode(
            on_ctrl_enter=self.run_source_code,
            on_cursor_move=self.update_line_col_from_cursor,
        )
        self.editor.add_widget(self.source_code)
        self.add_widget(self.editor)
        self.footer = Footer(size_hint_y=None, height=FONT_SIZE * 1.5)
        self.add_widget(self.footer)
        # result text
        self.result = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=0.4, orientation="vertical"
        )
        self.result_label = LabelWithBackgroundColor(
            background_color=(0.3, 0.3, 0.3, 1),
            text=" Result (read only)",
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        self.result_label.bind(
            size=self.result_label.setter("text_size")
        )  # alignment のため
        self.result_label_layout = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=None, height=FONT_SIZE * 1.5
        )  # height 指定のため
        self.result_label_layout.add_widget(self.result_label)
        self.result.add_widget(self.result_label_layout)
        self.result_text = kivy.uix.textinput.TextInput(
            text="",
            readonly=True,
            cursor_width=0,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.result.add_widget(self.result_text)
        self.add_widget(self.result)

    def run_source_code(self, *args):  # self.run_button が渡される
        text = "if (1) { " + self.source_code.text + " };"
        self.server.execute_string(text)
        self.result_text.text = self.server.pop_string()


class Pie(kivy.app.App):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def build(self):
        self.editor = Editor(**self.kwargs)
        return self.editor


if __name__ == "__main__":
    asir_server = server.Server()
    asir_server.start()
    app = Pie(lang_server=asir_server)
    app.run()
    asir_server.shutdown()
