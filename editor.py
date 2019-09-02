import kivy.app
import textwrap
import kivy.config
import kivy.core.window
import kivy.uix.codeinput
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.textinput
import kivy.uix.widget
import server
import lexer


# 右クリックで丸が出るのを防ぐ
# https://kivy.org/doc/stable/api-kivy.input.providers.mouse.html#using-multitouch-interaction-with-the-mouse
kivy.config.Config.set("input", "mouse", "mouse,disable_multitouch")

kivy.core.window.Window.clearcolor = (1, 1, 1, 1)  # 背景を白に
kivy.core.window.Window.size = (1920, 1020)  # 適当に大きめに設定しておく

FONT_NAME = "RictyDiminished-Regular.ttf"
FONT_SIZE = 24


class SourceCode(kivy.uix.codeinput.CodeInput):
    def __init__(self, run_source_code):
        super().__init__(
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
            lexer=lexer.AsirLexer(),
            background_normal=kivy.uix.textinput.TextInput.background_active.defaultvalue,
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.run_source_code = run_source_code
        self.ctrl_down = False

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if self.ctrl_down:
            if "enter" in keycode[1]:
                self.run_source_code()
                return True
        elif "ctrl" in keycode[1]:
            self.ctrl_down = True
        # 元々のメソッドを呼ぶ
        kivy.uix.textinput.TextInput.keyboard_on_key_down(
            self, window, keycode, text, modifiers
        )

    def keyboard_on_key_up(self, window, keycode):
        if "ctrl" in keycode[1]:
            self.ctrl_down = False
        kivy.uix.textinput.TextInput.keyboard_on_key_up(self, window, keycode)


class Editor(kivy.uix.boxlayout.BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical")
        self.server = kwargs["lang_server"]
        # buttons
        self.buttons = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=0.1, orientation="horizontal"
        )
        self.run_button = kivy.uix.button.Button(
            text="Run",
            on_press=self.run_source_code,
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.buttons.add_widget(self.run_button)
        self.add_widget(self.buttons)
        # main area
        self.editor = kivy.uix.boxlayout.BoxLayout(orientation="horizontal")
        self.line_number = kivy.uix.textinput.TextInput(
            size_hint=(None, 1),
            width=30,
            text="1\n2\n3",
            readonly=True,
            cursor_width=0,
            background_active=kivy.uix.textinput.TextInput.background_normal.defaultvalue,
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.editor.add_widget(self.line_number)
        self.source_code = SourceCode(run_source_code=self.run_source_code)
        self.editor.add_widget(self.source_code)
        self.add_widget(self.editor)
        # result text
        self.result = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=0.4, orientation="vertical"
        )
        self.result_label = kivy.uix.label.Label(
            size_hint_y=0.2,
            text=" Result (read only)",
            halign="left",
            valign="middle",
            color=(0, 0, 0, 1),
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.result_label.bind(
            size=self.result_label.setter("text_size")
        )  # alignment のため
        self.result.add_widget(self.result_label)
        self.result_text = kivy.uix.textinput.TextInput(
            text="",
            readonly=True,
            cursor_width=0,
            background_active=kivy.uix.textinput.TextInput.background_normal.defaultvalue,
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
