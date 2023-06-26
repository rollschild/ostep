# Scheduling

- **scheduling policies** (a.k.a. **disciplines**)
- **workload**
- **job** - a.k.a. process

## Scheduling Metrics

- **turnaround time**
  - $T_{turnaround} = T_{completion} - T_{arrival}$
- **fairness**
  - Jain's Fairness Index

### FIFO

- First Come, First Served (**FCFS**)
- **Convoy Effect**
  - a number of relatively-short potential consumers of a resource get queued behind a heavyweight resource consumer

### Shortest Job First (SJF)

- run the shortest job first, then the next shortest, and so on
- suitable for any system where the **perceived turnaround time per customer/job** matters
- **Non-preemptive** vs. **Preemptive**
  - **non-preemptive** - run each job to completion _before_ considering whether to run a new job
  - **preemptive** - willing to stop one process from running in order to run another
- optimal for jobs arriving at the same time

### Shortest Time-to-Completion First (STCF)

- a.k.a. \***\*Preemptive Shortest Job First (PSJF)\*\***
- Jobs do _NOT_ have to run to completion
- preempts a job and runs another instead
- Any time a new job enters the system, STCF scheduler determines which of the remaining jobs (including the new ones) has the _least time left_ and schedules that one

## New Metric: Response Time

- \***\*Response Time\*\***
  - $T_{response} = T_{firstrun} - T_{arrival}$

### Round Robin

- Instead of running jobs to completion, run a job for a **time slice** (**scheduling quantum**) and then switches to the next job in the run queue
- Repeatedly until jobs are finished
- a.k.a. **time slicing**
- length of the time slice is critical
  - shorter the better - in terms of response time metric
  - BUT cost of **context switching** will dominate overall performance
- Context switching's cost:
  - saving/restoring registers
  - state buildup in CPU cache, TLBs, branch predictors
    - flushed and brought in new state

## With I/O

- **overlap**
  - CPU being used by one process while waiting for the I/O of another to complete

# The Multi-Level Feedback Queue

- \***\*MLFQ\*\***
- First described in **Compatible Time-Sharing System (CTSS)**
- Goals:
  - optimize **turnaround time**
  - minimize **response time** - make the system feel responsive/interactive

## Basic Rules

- MLFQ has a number of distinct **queues**
  - each assigned a different **priority level**
  - **priorities** determine which job should be run at a given time
- **Rule 1**
  - if $Priority(A) > Priority(B)$, A runs; B does not
- **Rule 2**
  - if $Priority(A) == Priority(B)$, A and B run in Round Robin
- How does MLFQ set priorities?
  - it _varies_ the priority of a job based on its _observed behavior_
  - a more interactive process (interactions with keyboard) has higher priority
  - a process using CPU for a long periods of time has _reduced_ priority
  - MLFQ _learns_ the **history** of the processes and _predicts_ their **future** behavior
  - job priorities _change_ over time

## How to Change Priority

- **Rule 3**
  - when a job enters the system, it's placed at the _highest_ priority (topmost queue)
- **Rule 4**
  - if job uses up entire time slice while running, its priority is _reduced_
  - if job gives up the CPU before time slice is up, it stays at the _same_ priority level
- Potential problems:
  - **starvation**:
    - if too many interactive jobs, they will consume _all_ CPU time
    - long-running jobs will **starve**
  - easy to **game the scheduler**
    - before time slice is over, issue an I/O to relinquish the CPU
    - could monopolize the CPU
  - program could change behavior

## Priority Boost

- _Periodically_ boost the priority of _all_ jobs in the system
- **Rule 5**
  - after some time period $S$, move all jobs in the system to the topmost queue
- processes are guaranteed not to starve
  - they will be run in **round robin**
- if $S$ is too low, interactive jobs may not get a proper share of the CPU

## Better Accounting

- **accounting** of CPU time at _each_ level of MLFQ
- scheduler keeps track of **how much of a time slice a process used at a given level**
  - once a process has used its allotment, it's demoted
- **Revised Rule 4**
  - Once a job uses up its time allotment at a given level (regardless of how many times it has given up the CPU), its priority is reduced down one level

## Remaining Issues

- How to parameterize the scheduler?
- Allow for verying time-slice length across different queues
  - high priority queues have short time slices (10 or fewer milliseconds)
  - low priority queues (CPU bound) have longer time slices - 100s of ms
- some schedulers allow some user **advice** to help set priorities
  - use CLI `nice`
  - `madvise` - memory manager
-
