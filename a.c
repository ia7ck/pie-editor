#include "ox_toolkit.h"
#include <stdio.h>

// important!
extern OXFILE *ox_start(char *, char *, char *);
OXFILE *start(void) { return ox_start("localhost", "ox", "ox_asir"); }
void execute_string(OXFILE *server, char *str) {
  ox_execute_string(server, str);
}
char *pop_string(OXFILE *server) { return ox_popString(server); }
void shutdown(OXFILE *server) { ox_shutdown(server); }

int main(void) {

  OXFILE *server = start();
  execute_string(server, "1000000000 + 98765;");
  char *result = pop_string(server);
  printf("%s\n", result);
  shutdown(server);

  return 0;
}
