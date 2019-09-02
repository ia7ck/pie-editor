import kivy.app
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


class Editor(kivy.uix.boxlayout.BoxLayout):
    def __init__(self, **kwargs):
        self.server = kwargs["lang_server"]
        super().__init__(orientation="vertical")
        # buttons
        self.buttons = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=0.1, orientation="horizontal"
        )
        self.buttons.add_widget(
            kivy.uix.button.Button(
                text="Run",
                on_press=self.run_source,
                font_name=FONT_NAME,
                font_size=FONT_SIZE,
            )
        )
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
        self.source_code = kivy.uix.codeinput.CodeInput(
            text="""/* comment */
/* /* 入れ子 */ */
if (0) {
    car([]);
    X2 = x_0 ^ 2;
    Str = "string string";
}
def f(A) {
    return A * 2;
}
f(10) + f(100);""",
            cursor_width=3,
            cursor_color=(0.25, 0.25, 0.25, 1),
            lexer=lexer.AsirLexer(),
            background_normal=kivy.uix.textinput.TextInput.background_active.defaultvalue,
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
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

    def run_source(self, button):
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
