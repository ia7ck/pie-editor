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
- Navigate to error line.

### Keyboard shortcut

- `Ctrl+Enter`: Run source code.
- `Ctrl+S`: Save File.
    - If some file is opened, overwrite it.
- `Ctrl+B`: Beautify source code.
