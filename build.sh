gcc -fPIC -c a.c -o a.o -Wall -Wextra -I$OpenXM_HOME/include
gcc a.o -o a.out -Wall -Wextra -L$OpenXM_HOME/lib -lox -lgc -lmpfr -lgmp
gcc -shared a.o -o liba.so -Wall -Wextra -L$OpenXM_HOME/lib -lox -lgc -lmpfr -lgmp

gcc b.c -o b.out -Wall -Wextra -I$OpenXM_HOME/include -L. -la -L$OpenXM_HOME/lib -lox -lgc -lmpfr -lgmp -Wl,-rpath -Wl,.
