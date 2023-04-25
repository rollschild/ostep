#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
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
    char *myargs[3];
    myargs[0] = strdup("wc");
    myargs[1] = strdup("p3.c"); // file to count
    myargs[2] = NULL;           // marks end of array
    execvp(myargs[0], myargs);  // run word count
    printf("This line should NOT be printed out!");
  } else {
    // when child is done, `wait()` returns to its parent
    int rc_wait = wait(NULL);
    printf("I'm a parent of %d (rc_wait:%d) (pid: %d)\n", rc, rc_wait,
           (int)getpid());
  }

  return 0;
}
