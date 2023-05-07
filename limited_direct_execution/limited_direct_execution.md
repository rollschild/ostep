# Mechanism: Limited Direct Execution

- Virtualization by \***\*time sharing\*\*** the CPU
  - share the physical CPU among many jobs running _seemingly_ at the same time
  - run one process for a while, then run another one
- Key/Goal: **Obtaining high performance while maintaining control**

## Basic technique: Limited Direct Execution

## Retricted Operations

- Introduce a new processor mode - \***\*user mode\*\***
  - code running in user mode _CANNOT_ issue I/O requests
    - exception would be raised
  - when code wishes to perform a privileged operation, it performs a **system call**
- \***\*kernel mode\*\***
  - where OS (or kernel) runs in

### System Calls

- System calls
  - access the file system
  - create/destroy processes
  - communicate with other processes
  - allocate more memory
- To execute a system call, the program must execute a special \***\*trap\*\*** instruction, which simultaneously:
  - jumps into the kernel
  - raises the privilege level to kernel mode
- when operation completes, OS calls the \***\*return-from-trap\*\*** instruction, which simultaneously:
  - reduces privilege level back to user mode, and
  - returns into the calling user program
- system calls ~= procedure calls?
  - system call _is_ a procedure call, but
  - hidden inside the procedure call is the \***\*trap instruction\*\***
- OS provides the special instructions to:
  - \***\*trap\*\*** into the kernel, and
  - \***\*return-from-trap\*\*** back to user-mode programs
- OS also provides instructions to allow itself to tell the hardware where the _trap table_ resides _memory_
- On x86, the processor pushes the following onto a per-process \***\*kernel stack\*\***
  - program counter,
  - flags,
  - a few other registers
- To prevent the code from executing arbitrary code upon a trap, the OS sets up a \***\*trap table\*\*** at _boot time_
  - when machine boots up, it's in kernel mode
  - during which OS tells hardware what code to run when certain exceptional events occur
  - tells the hardware the locations of these \***\*trap handlers\*\***
  - hardware remembers the location of the trap handlers _until_ next boot
- Each system call is assigned \***\*system-call number\*\***

## Switching between processes

- When a user program is running on CPU, technically the OS is _NOT_ running

### The Cooperative Approach

- Used by old OS
- OS trusts the processes of the system to behave reasonably
- By:
  - waiting for a system call, or
  - waiting for an illegal operation
- Processes give up control of CPU to OS _periodically_
  - when making system calls
- by `yield` system call
  - does nothing but transfer control to the OS

### Non-Cooperative Approach

- A \***\*timer interrupt\*\***
- OS informs hardware of which code to run when the timer interrupt occurs
  - at boot time
- OS also starts the timer at boot time!
- Timer _can_ be turned off!
- Hardware makes sure it saves enough of the state of the program that was running when an interrupt occurs

### Saving and restoring context

- \***\*Scheduler\*\*** - decides whether to continue running the current process or switch to a new one
- If switching to a new process:
  - \***\*context switch\*\***
  - save a few register values for the currently-executing process (onto its kernel stack)
  - restore a few register values for the soon-to-be-executing process (from kernel stack)
- OS might _disable interrupts_ during interrupt processing
  - ensures when one interrupt is being handled, no other one will be delivered to CPU
-
