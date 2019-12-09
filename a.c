#include "ox_toolkit.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/select.h>

// ox_toolkit/oxf_old.c
extern OXFILE *ox_start(char *, char *, char *);

OXFILE *start(void) { return ox_start("localhost", "ox", "ox_asir"); }
void execute_string(OXFILE *server, char *str) {
  ox_execute_string(server, str);
  send_ox_command(server, SM_popString);
}
char *pop_string(OXFILE *server) {
  receive_ox_tag(server);
  return ((cmo_string *)receive_cmo(server))->s;
}
int my_select(OXFILE *server) {
  // https://linuxjm.osdn.jp/html/LDP_man-pages/man2/select.2.html
  fd_set rfds;
  struct timeval tv;
  FD_ZERO(&rfds);
  FD_SET(server->fd, &rfds);
  tv.tv_sec = 0;
  tv.tv_usec = 1;
  return select((server->fd) + 1, &rfds, NULL, NULL, &tv);
}
void reset(OXFILE *server) { ox_reset(server); }
void shutdown(OXFILE *server) { ox_shutdown(server); }

#include <unistd.h>
int main(void) { // test

  OXFILE *server = start();
  execute_string(server, "1000000000 + 98765;");
  puts("sleep 1 sec ...");
  sleep(1);
  assert(my_select(server) != 0);
  char *res1 = pop_string(server);
  assert(strcmp(res1, "1000098765") == 0);

  execute_string(server, "fctr(x^200000 - y^200000);");
  puts("sleep 1 sec ...");
  sleep(1);
  assert(my_select(server) == 0); // 計算中
  reset(server);

  execute_string(server, "fctr(x^2 - y^2);");
  puts("sleep 1 sec ...");
  sleep(1);
  assert(my_select(server) != 0);
  char *res2 = pop_string(server);
  assert(strcmp(res2, "[[1,1],[x-y,1],[x+y,1]]") == 0);

  reset(server);
  shutdown(server);

  return 0;
}
