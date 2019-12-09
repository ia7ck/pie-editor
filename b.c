/* liba.so を使うプログラム */
#include "ox_toolkit.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

extern OXFILE *start(void);
extern void execute_string(OXFILE *, char *);
extern char *pop_string(OXFILE *);
extern int my_select(OXFILE *);
extern void reset(OXFILE *);
extern void shutdown(OXFILE *);

#include <unistd.h>
int main(void) { // test

  OXFILE *server = start();
  execute_string(server, "1000000000 + 98765;");
  puts("sleep 1 sec...");
  sleep(1);
  assert(my_select(server) != 0);
  char *res1 = pop_string(server);
  assert(strcmp(res1, "1000098765") == 0);

  execute_string(server, "fctr(x^200000 - y^200000);");
  puts("sleep 1 sec...");
  sleep(1);
  assert(my_select(server) == 0); // 計算中
  reset(server);

  execute_string(server, "fctr(x^2 - y^2);");
  puts("sleep 1 sec...");
  sleep(1);
  assert(my_select(server) != 0);
  char *res2 = pop_string(server);
  assert(strcmp(res2, "[[1,1],[x-y,1],[x+y,1]]") == 0);

  reset(server);
  shutdown(server);

  return 0;
}
