import kivy.app
import kivy.core.window
import kivy.uix.boxlayout
import kivy.uix.button

kivy.core.window.Window.clearcolor = (1, 1, 1, 1)


class Editor(kivy.app.App):
    def build(self):
        self.layout = kivy.uix.boxlayout.BoxLayout(orientation="vertical")
        self.layout.add_widget(kivy.uix.button.Button(text="hello"))
        self.layout.add_widget(kivy.uix.button.Button(text="world"))
        return self.layout


if __name__ == "__main__":
    editor = Editor()
    editor.run()
