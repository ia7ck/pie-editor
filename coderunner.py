import subprocess
import re

import outputanalyzer


class CodeRunner:
    def __init__(self, editor):
        self.editor = editor

    def run_source_code(self, *args):
        e = self.editor
        sv = e.server
        sv.reset()
        e.clock_event.cancel()
        e.result.text = "running ..."
        e.footer.error_line.text = ""
        selection = e.source_code.selection_text
        text = selection if len(selection) > 0 else e.source_code.text
        server_input = (
            "if (1) { "
            + self.replace_macros(self.strip_end_keyword(text))
            + " } else {};"
        )
        sv.execute_string(server_input)
        e.clock_event()

    def strip_end_keyword(self, text):
        return re.sub(r"\bend\b", "", text)

    def replace_macros(self, text):
        proc = subprocess.run(
            ["openxm", "ox_cpp", "-P"], input=text.encode(), stdout=subprocess.PIPE
        )
        # TODO: 失敗時に何か表示する
        return proc.stdout.decode("utf-8")

    def fetch_result(self):
        e = self.editor
        sv = e.server
        finished = True if sv.select() != 0 else False
        if finished:
            res = sv.pop_string()
            e.clock_event.cancel()
            e.update_result(res)
            e.show_execute_error(res)
        else:
            e.result.text += " ..."

    def stop_running(self, *args):
        e = self.editor
        e.server.reset()
        e.clock_event.cancel()
        e.result.text = "stopped"
