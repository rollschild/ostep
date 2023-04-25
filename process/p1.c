#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  printf("Hello, world! (pid: %d)\n", (int)getpid());
  int rc = fork();
  if (rc < 0) {
    // fork failed!
    fprintf(stderr, "Fork has failed!\n");
    exit(1);
  } else if (rc == 0) {
    // child (NEW process)
    printf("Hello, I'm a child process! (pid: %d)\n", (int)getpid());
  } else {
    // parent goes down this path? (main)
    printf("I'm a parent of %d! (pid: %d)\n", rc, (int)getpid());
  }

  return 0;
}
