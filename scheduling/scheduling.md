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
-
