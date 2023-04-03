# Intro to Operating Systems

## Intro

- **The Von Neumann Model of Computing**
  - Fetch
  - Decode
  - Execute
- **Virtualization**
- OS is a _resource manager_

## _Virtualizing the CPU_

- turn a single CPU into multiple CPUs
- governed by _policies_
- Use `&` to allow multiple jobs to run _in the background_

## Virtualizing Memory

- Memory is accessed on _each_ instruction fetch
- OS also virtualizes memory
- Each process accesses its own private **virtual address space**
  - where OS maps to physical memory

## Concurrency

## Persistence

- Data in system memory can be easily lost, because DRAM stores values in **volatile** manner
- To handle the problems of system crashes during writes, most file systems incorporate some kind of write protocol, such as:
  - **journaling**, or **copy-on-write**
  - carefully ordering writes to disk to ensure that if a failure occurs during the write sequence, the system can recover to _reasonable_ state afterwards

## Design Goals

- **Abstraction**
- **performance**
- **protetion**
  - **isolation**
  - **security**
- **system call** vs. **procedural call**
  - **system call** _transfers_ control into the OS while simultaneously raising the **hardware priviledge level**
  - user applications run in **user mode**
  - How system call is made:
    1. usually **system call** is initiated via a special hardware instruction, **trap**
    2. hardware transfers control to a pre-specified **trap handler** and simultaneously raise the privilege level to **kernel level**
    - In **kernel mode** OS has full access to the hardware and can do things like:
      - initiate I/O requests
      - make more memory available to a program
    3. when OS is done, it passes control back to the user via **return-from-trap** instruction, which:
    - reverts to **user mode**, while simultaneously
    - passes control back to where the application left off
-
