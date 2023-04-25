# The Abstraction: The Process

- _process_: a running program
- OS runs multiple processes at the same time by _virtualizing_ the CPU
- To virtualize CPU:
  - **mechanism**
    - _time sharing_ of the CPU
    - _context switch_
  - **policy**
    - **scheduling policy**
- In UNIX, `init` is the _initial_ process that _spawns_ other processes as the system runs

## Process

- **machine state** - what the process can read/write during execution
  - _memory_
    - **address space** - the memory that the process can address
  - **registers**
  - persistent storage
- Special registers:
  - **program counter (PC)**, a.k.a. **instruction pointer (IP)**
    - tells which instruction the CPU will execute next
  - **stack pointer** and **frame pointer**
    - manage function parameters, local variables, and return addresses

## Process Creation

- OS loads the code of a program and any static data into the _address space_ of the process in memory
  - early/simple OS loads the program _eagerly_ - all at once
  - modern OS loads the program _lazily_
    - by loading _pieces_ of code/data only as they are needed during program execution
      - _paging_
      - _swapping_
- Allocate memory for the program's **run-time stack**
- Allocate memory for **heap**
  - in C, heap is for explicitly requested _dynamically-allocated_ data
    - by calling `malloc()` and `free()`
  - needed for data structures such as _linked lists_, _hash tables_, _trees_, etc
- I/O requests
  - In UNIX, each process by default has _three_ open _file descriptors_
    - for std input/output/error
- Start the program at the entry point, `main()`
  - OS transfers control of CPU to the newly created process
- When an I/O completes, the process that issued it is _not necessarily_ run right away
  - rather, whatever was running at the time keeps running

## Process States

- In one of three states:
  - _running_
  - _ready_
  - _blocked_
- **scheduled**: ready -> running
- **descheduled**: running -> ready

## Data Structures

- **process list** - to track the state of each process
- **register context** - holds the contents of its registers for a stopped process
  - used for restoring the registers
  - **context switch**
- **Process Control Block (PCB)**
  - a C structure that contains information about each process
  - a.k.a. **process descriptor**

## Process API

- Two APIs to create a new process:
  - `fork()`
  - `exec()`
- Use `wait()` to wait for a process which another process has created to complete

### The `fork()` System Call

- to create a new process
  - (almost) copy of the parent process
- the child process has its own:
  - address space - own private memory
  - registers
  - own PC
- The order of execution of parent and child processes is _NOT_ deterministic
  - determined by the CPU \***\*scheduler\*\***
- \***\*non-determinism\*\***

### `wait()`

- parent waits for a child process to finish
  - `wait()`, or
  - `waitpid()`

### `exec()`

- when you want to run a program that is _different_ from the calling one
- Given the name of an executable (`wc` in the `p3.c`):
  - it _loads_ code (and static data) from the executable
  - overwrites its current code segment (and current static data) with it
  - the heap and stack and other parts of the memory space of the program are _re-initialized_
  - then OS simply runs that program, passing in any arguments as the `argv` of that process
- `exec()` does _NOT_ create a new process
  - rather, it transforms the currently running program (formerly `p3.o`) into a different running program (`wc`)
- After the `exec()` in the child, it is almost as if `p3.c` never ran - a successful call to `exec()` _NEVER_ returns

## Motivation of the Design

- shell can run code _after_ the call to `fork()` but _before_ the call to `exec()`
- When you type a command in shell,
  - shell finds the executable in the file system,
  - calls `fork()` to create a new child process to run the command,
  - calls some variant of `exec()` to run the command,
  - then waits for the command to complete by calling `wait()`
  - when the child process completes, the shell returns from `wait()` and prints out the prompt (again), ready for the next command
- Example: `$ wc p3.c > word_count.txt`
  - output of `wc` is _redirected_ into `word_count.txt`
  - when the child process is created, before calling `exec()`, the shell:
    - closes **standard output**, and
    - opens the file `word_count.txt`
- UNIX starts looking for free file descriptors at zero
- Unix pipe
  - output of one process is connected to an in-kernel \***\*pipe\*\***
  - intput of another process is connected to that same pipe

## Process Control and Users

- `kill()`: send **signals** to a process
- `<C-c>` sends `SIGINT` (interrupt) to a process
- `<C-z>` sends `SIGSTP` (stop) to a process
  - to pause the process in mid-execution
  - can be resumed later with a command, e.g. `fg`
- Can send signals to an entire \***\*process group\*\***
  - a process should use the `signal()` system call to "catch" various signals
- \***\*User\*\***
  - users generally can only control their own processes

## Tools

- `ps()`
- `top()`
- `kill()` and `killall()`
-
