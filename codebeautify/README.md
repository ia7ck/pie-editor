### Example
```sh
$ cat sample.rr | ./beautifier.py
Abc = 12 + 3;
-(1 + 2) / --3;
1 ^ 2 * 3 % 4 + (-56);
1 && 2 || 3;
Msg = "1  +2 ";
f = !true != false;
eval(sin(@pi / 2));
A += B;
A++ - B;
++A * B;
A ^= B;
M = A < B ? A : B;
A = [1, 2, -3];
A[(1 - 1)];
def f() {
    for (I = 0; I < 10; I++) {
        continue;
        break;
    }
    return 0;
}
```

### Test
```sh
$ python -m unittest discover -s tests
```
