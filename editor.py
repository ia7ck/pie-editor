import kivy.app
import kivy.config
import kivy.core.text
import kivy.core.window
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.textinput

kivy.core.window.Window.clearcolor = (1, 1, 1, 1)
kivy.core.window.Window.size = (1920, 1020)

FONT_NAME = "NotoSansCJK-Regular.ttc"
FONT_SIZE = 24


class Editor(kivy.uix.boxlayout.BoxLayout):
    def __init__(self):
        super().__init__(orientation="vertical")
        # buttons
        self.buttons = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=0.1, orientation="horizontal"
        )
        self.run_button = kivy.uix.button.Button(
            text="Run", font_name=FONT_NAME, font_size=FONT_SIZE
        )
        self.buttons.add_widget(self.run_button)
        self.add_widget(self.buttons)
        # source text
        self.source_text = kivy.uix.textinput.TextInput(
            text="hello\nworld", font_name=FONT_NAME, font_size=FONT_SIZE
        )
        self.add_widget(self.source_text)
        # result text
        self.result = kivy.uix.boxlayout.BoxLayout(
            size_hint_y=0.4, orientation="vertical"
        )
        self.result_label = kivy.uix.label.Label(
            size_hint_y=0.2,
            text="Result (read only)",
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
            text="result\nresult\n結果",
            readonly=True,
            font_name=FONT_NAME,
            font_size=FONT_SIZE,
        )
        self.result.add_widget(self.result_text)
        self.add_widget(self.result)


class Pie(kivy.app.App):
    def build(self):
        self.editor = Editor()
        return self.editor


if __name__ == "__main__":
    app = Pie()
    app.run()
