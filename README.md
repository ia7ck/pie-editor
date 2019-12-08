```
$ python3 -V
Python 3.7.5
```

### How to build and run

1. `$ source /path/to/OpenXM_HOME/rc/dot.bashrc`
2. `$ ./build.sh`
    - `liba.so` is created.
3. `$ pip install --upgrade pip && pip install -r requirements.txt`
4. `$ python3 main.py`

### Test

- All: `python3 -m unittest discover --start-directory tests`
- Each file: e.g. `python3 -m unittest tests/test_erroranalyzer.py`

### Support

- Replace macros (#define directives).
- Suspend execution.
- Preview png file generated by `print_png_form()`.
    -  `print_png_form` is a funcion in [Asir-contrib](http://www.math.kobe-u.ac.jp/OpenXM/Current/doc/asir-contrib/ja/cman-html/cman-ja.html#print_005fpng_005fform).
- Navigate to error line.
- Fix up indent style.
- Generate HTML from source code with syntax highlight.
    - Then open it in browser.

### Keyboard shortcut

- `Ctrl+Enter`: Run source code.
- `Ctrl+S`: Save File.
    - If some file is opened, overwrite it.
- `Ctrl+B`: Beautify source code.
- `Ctrl+/`: Comment/Uncomment current line.

### NOT implemented

- Syntax highlight for multiline comment.
- Find/Replace a word.
- Jump to open/close brace.
