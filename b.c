/* liba.so を使うプログラム */
#include "ox_toolkit.h"
#include <stdio.h>

extern OXFILE *start(void);
extern void execute_string(OXFILE *, char *);
extern char *pop_string(OXFILE *);
extern void shutdown(OXFILE *);

int main(void) {

  OXFILE *server = start();
  execute_string(server, "1000000000 + 98765;");
  char *result = pop_string(server);
  printf("%s\n", result);
  shutdown(server);

  return 0;
}
