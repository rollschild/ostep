# The Abstraction: The Process

- _process_: a running program
- OS runs multiple processes at the same time by _virtualizing_ the CPU
- To virtualize CPU:
  - **mechanism**
    - _time sharing_ of the CPU
    - _context switch_
  - **policy**
    - **scheduling policy**

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
-
