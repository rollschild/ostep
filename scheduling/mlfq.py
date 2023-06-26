#! /usr/bin/env python3
from argparse import ArgumentParser
import random
import sys
from enum import Enum


class JobStatus(Enum):
    IO_DONE = "IO_DONE"


class Key(Enum):
    CURR_PRIORITY = "curr_priority"
    ALLOT_LEFT = "allot_left"
    TICKS_LEFT = "ticks_left"
    DOING_IO = "doing_io"
    TIME_LEFT = "time_left"
    FIRST_RUN = "first_run"


# Parse Arguments
parser = ArgumentParser()
parser.add_argument(
    "-s",
    "--seed",
    help="the random seed",
    default=0,
    action="store",
    type=int,
    dest="seed",
)
parser.add_argument(
    "-n",
    "--numQueues",
    help="number of queues in MLFQ (if not using -Q)",
    default=3,
    action="store",
    type=int,
    dest="num_queues",
)
parser.add_argument(
    "-q",
    "--quantum",
    help="length of time slice (if not using -Q)",
    default=10,
    action="store",
    type=int,
    dest="quantum",
)
parser.add_argument(
    "-a",
    "--allotment",
    help="length of allotment (if not using -A)",
    default=1,
    action="store",
    type=int,
    dest="allotment",
)
parser.add_argument(
    "-Q",
    "--quantumList",
    help="length of time slice per queue level, specified as "
    + "x,y,z,... where x is the quatum length of the highest "
    + "priority queue, y the next highest, and so forth",
    default="",
    action="store",
    dest="quantum_list",
)
parser.add_argument(
    "-A",
    "--allotmentList",
    help="length of time allotment per queue level, specified as "
    + "x,y,z,... where x is the # of time slices for the highest "
    + "priority queue, y the next highest, and so forth",
    default="",
    action="store",
    dest="allotment_list",
)
parser.add_argument(
    "-j",
    "--numJobs",
    help="number of jobs in the sytem",
    default=3,
    action="store",
    type=int,
    dest="num_jobs",
)
parser.add_argument(
    "-m",
    "--maxLen",
    help="max runtime of a job (if randomly generating)",
    default=100,
    action="store",
    type=int,
    dest="max_len",
)
parser.add_argument(
    "-M",
    "--maxIO",
    help="max I/O frequency of a job (if randomly generating)",
    default=10,
    action="store",
    type=int,
    dest="max_io",
)
parser.add_argument(
    "-B",
    "--boost",
    help="how often to boost the priority of all jobs back to high priority",
    default=0,
    action="store",
    type=int,
    dest="boost",
)
parser.add_argument(
    "-i",
    "--ioTime",
    help="how long an I/O should last (fixed constant)",
    default=5,
    action="store",
    type=int,
    dest="io_time",
)
parser.add_argument(
    "-S",
    "--stay",
    help="reset and stay at same priority level when issuing I/O",
    default=False,
    action="store_true",
    dest="stay",
)
parser.add_argument(
    "-I",
    "--ioBump",
    help="if specified, jobs that finished I/O move immediately to front of current queue",
    default=False,
    action="store_true",
    dest="io_bump",
)
parser.add_argument(
    "-l",
    "--jobList",
    help="a comma-separated list of jobs to run, in the form x1,y1,z1:x2,y2,z2:... where x is start time, y is run time, and z is how often the job issues an I/O request",
    default="",
    action="store",
    dest="job_list",
)
parser.add_argument(
    "-c",
    help="compute answers for me",
    default=False,
    action="store_true",
    dest="solve",
)

args = parser.parse_args()


# MLFQ: how many queues
num_queues = args.num_queues

# queue_level -> time slice length
quantum_dict = {}
if args.quantum_list != "":
    # extract number of queues and their time slices from args
    quantum_lens = args.quantum_list.split(",")
    num_queues = len(quantum_lens)
    q_idx = num_queues - 1
    for i in range(num_queues):
        quantum_dict[q_idx] = int(quantum_lens[i])
        q_idx -= 1

else:
    for i in range(num_queues):
        quantum_dict[i] = int(args.quantum)

allotment_dict = {}
if args.allotment_list != "":
    allotment_lens = args.allotment_list.split(",")
    if num_queues != len(allotment_lens):
        print("number of allotments must match number of quantums!")
        exit(1)
    q_idx = num_queues - 1

    for i in range(num_queues):
        allotment_len = int(allotment_lens[i])
        if q_idx != 0 and allotment_len <= 0:
            print("allotment must be positive integer!")
            exit(1)
        allotment_dict[q_idx] = allotment_len
        q_idx -= 1
else:
    for i in range(num_queues):
        allotment_dict[i] = int(args.allotment)


io_time = int(args.io_time)

# tracks when I/Os and other interrupts are complete
io_done_dict = {}

# stores all info about jobs
job_dict = {}
job_idx = 0
hi_q = num_queues - 1

random.seed(args.seed)

if args.job_list != "":
    all_jobs = args.job_list.split(":")
    for j in all_jobs:
        job_info = j.split(",")
        if len(job_info) != 3:
            print("job string is in wrong format! shoudl be x1,y1,z1:x2,y2,z2:...")
            exit(1)
        assert len(job_info) == 3
        start_time = int(job_info[0])
        run_time = int(job_info[1])
        io_freq = int(job_info[2])
        job_dict[job_idx] = {
            Key.CURR_PRIORITY: hi_q,
            Key.TICKS_LEFT: quantum_dict[hi_q],
            Key.ALLOT_LEFT: allotment_dict[hi_q],
            "start_time": start_time,
            "run_time": run_time,
            Key.TIME_LEFT: run_time,
            "io_freq": io_freq,
            Key.DOING_IO: False,
            Key.FIRST_RUN: -1,
        }

        if start_time not in io_done_dict:
            io_done_dict[start_time] = []
        io_done_dict[start_time].append((job_idx, "JOB BEGINS"))
        job_idx += 1
else:
    # randomly generate jobs
    for j in range(args.num_jobs):
        start_time = 0
        run_time = int(random.random() * (args.max_len - 1) + 1)
        io_freq = int(random.random() * (args.max_io - 1) + 1)
        job_dict[job_idx] = {
            Key.CURR_PRIORITY: hi_q,
            Key.TICKS_LEFT: quantum_dict[hi_q],
            Key.ALLOT_LEFT: allotment_dict[hi_q],
            "start_time": start_time,
            "run_time": run_time,
            Key.TIME_LEFT: run_time,
            "io_freq": io_freq,
            Key.DOING_IO: False,
            Key.FIRST_RUN: -1,
        }
        if start_time not in io_done_dict:
            io_done_dict[start_time] = []
        io_done_dict[start_time].append((job_idx, "JOB BEGINS"))
        job_idx += 1

num_jobs = len(job_dict)


print("Here is the list of inputs:")
print("OPTIONS jobs", num_jobs)
print("OPTIONS queues", num_queues)
for i in range(len(quantum_dict) - 1, -1, -1):
    print(f"OPTIONS allotments for queue {i:2} is {allotment_dict[i]:3}")
    print(f"OPTIONS quantum length for queue {i:2} is {quantum_dict[i]:3}")
print("OPTIONS boost", args.boost)
print("OPTIONS ioTime", args.io_time)
print("OPTIONS stayAfterIO", args.stay)
print("OPTIONS iobump", args.io_bump)

print("\n")
print("For each job, three defining characteristics are given:")
print("  startTime : at what time does the job enter the system")
print("  runTime   : the total CPU time needed by the job to finish")
print("  ioFreq    : every ioFreq time units, the job issues an I/O")
print("              (the I/O takes ioTime units to complete)\n")

print("Job List:")
for i in range(num_jobs):
    start_time = job_dict[i]["start_time"]
    run_time = job_dict[i]["run_time"]
    io_freq = job_dict[i]["io_freq"]
    print(
        f"  Job {i:2}: startTime {start_time:3} - runTime {run_time:3} - ioFreq {io_freq:3}"
    )
print("")

if args.solve == False:
    print("Compute the execution trace for the given workloads.")
    print("If you would like, also compute the response and turnaround")
    print("times for each of the jobs.")
    print("")
    print("Use the -c flag to get the exact results when you are finished.\n")
    exit(0)

# Initialize the MLFQ queue
queue = {}
for q in range(num_queues):
    queue[q] = []

curr_time = 0

total_num_jobs = len(job_dict)
num_finished_jobs = 0


# Finds the highest non-empty queue
# reutrn -1 if they are all empty
def find_queue():
    q = hi_q
    while q > 0:
        if len(queue[q]) > 0:
            return q
        q -= 1
    if len(queue[q]) > 0:
        return 0
    return -1


def abort_job(str):
    sys.stderr.write(str + "\n")
    exit(1)


print("\nExecution Trace:\n")

while num_finished_jobs < total_num_jobs:
    # Find job with highest priority
    # run it runtil either:
    #   - job uses up its time quantum
    #   - job performs an I/O

    # check for piority boost
    if args.boost > 0 and curr_time != 0:
        # note boost is _how often_ to boost
        if curr_time % args.boost == 0:
            print(f"[ time {curr_time} ] BOOST ( every {args.boost} )")
            # Remove _all_ jobs from queues except for the highest queue
            # Put them in the highest queue
            for q in range(num_queues - 1):
                for j in queue[q]:
                    if job_dict[j][Key.DOING_IO] is False:
                        queue[hi_q].append(j)
                queue[q] = []

            # change priority to highest
            for j in range(num_jobs):
                if job_dict[j][Key.TIME_LEFT] > 0:
                    job_dict[j][Key.CURR_PRIORITY] = hi_q
                    job_dict[j][Key.TICKS_LEFT] = allotment_dict[hi_q]

    # check for any I/Os done
    if curr_time in io_done_dict:
        for j_id, type in io_done_dict[curr_time]:
            q = job_dict[j_id][Key.CURR_PRIORITY]
            job_dict[j_id][Key.DOING_IO] = False
            print(f"[ time {curr_time} ] {type} by JOB {j_id}")
            if args.io_bump is False or type == "JOB BEGINS":
                queue[q].append(j_id)
            else:
                queue[q].insert(0, j_id)

    # Find the highest priority job
    curr_queue = find_queue()
    if curr_queue == -1:
        print(f"[ time {curr_time} ] IDLE")
        curr_time += 1
        continue

    # at lease one runnable job
    curr_job = queue[curr_queue][0]
    curr_priority = job_dict[curr_job][Key.CURR_PRIORITY]
    if curr_priority != curr_queue:
        abort_job(
            f"curr_priority {curr_priority} does NOT match curr_queue {curr_queue}"
        )

    job_dict[curr_job][Key.TIME_LEFT] -= 1
    job_dict[curr_job][Key.TICKS_LEFT] -= 1

    if job_dict[curr_job][Key.FIRST_RUN] == -1:
        job_dict[curr_job][Key.FIRST_RUN] = curr_time

    run_time = job_dict[curr_job]["run_time"]
    io_freq = job_dict[curr_job]["io_freq"]
    ticks_left = job_dict[curr_job][Key.TICKS_LEFT]
    allot_left = job_dict[curr_job][Key.ALLOT_LEFT]
    time_left = job_dict[curr_job][Key.TIME_LEFT]

    print(
        f"[ time {curr_time} ] Run JOB {curr_job} at PRIORITY {curr_queue} [ TICKS {ticks_left} ALLOT {allot_left:d} TIME {time_left} (of {run_time}) ]"
    )

    if time_left < 0:
        abort_job("ERROR: should never have less than 0 time left to run!")

    # UPDATE TIME
    curr_time += 1

    # Check for JOB ending
    if time_left == 0:
        print(f"[ time {curr_time} ] FINISHED JOB {curr_job}")
        num_finished_jobs += 1
        job_dict[curr_job]["end_time"] = curr_time
        done_job = queue[curr_queue].pop(0)
        assert done_job == curr_job
        continue

    # Check for I/O
    io_issued = False
    if io_freq > 0 and (((run_time - time_left) % io_freq) == 0):
        # Issue an I/O
        print(f"[ time {curr_time} ] IO_START by JOB {curr_job}")
        io_issued = True
        desched = queue[curr_queue].pop(0)
        assert desched == curr_job
        job_dict[curr_job][Key.DOING_IO] = True
        if args.stay:
            job_dict[curr_job][Key.TICKS_LEFT] = quantum_dict[curr_queue]
            job_dict[curr_job][Key.ALLOT_LEFT] = allot_left[curr_queue]

        # Add to I/O queue
        future_time = curr_time + io_time
        if future_time not in io_done_dict:
            io_done_dict[future_time] = []
        print("IO DONE")
        io_done_dict[future_time].append((curr_job, JobStatus.IO_DONE))

    # Check for quantum ending at this level
    # BUT there still may be allotment left
    # quantum: length of time slice
    if ticks_left == 0:
        if io_issued is False:
            # I/O NOT been issued - pop from queue
            desched = queue[curr_queue].pop(0)
        assert desched == curr_job

        job_dict[curr_job][Key.ALLOT_LEFT] = job_dict[curr_job][Key.ALLOT_LEFT] - 1

        # job can have multiple allotments - multiple slices
        if job_dict[curr_job][Key.ALLOT_LEFT] == 0:
            # job is DONE at _this_ level
            # Move on to next queue
            if curr_queue > 0:
                # change priority of the curr_job
                job_dict[curr_job][Key.CURR_PRIORITY] = curr_queue - 1
                job_dict[curr_job][Key.TICKS_LEFT] = quantum_dict[curr_queue - 1]
                # allotment:
                job_dict[curr_job][Key.ALLOT_LEFT] = allotment_dict[curr_queue - 1]
                if io_issued is False:
                    queue[curr_queue - 1].append(curr_job)
            else:
                # lowest queue
                job_dict[curr_job][Key.TICKS_LEFT] = quantum_dict[curr_queue]
                job_dict[curr_job][Key.ALLOT_LEFT] = allotment_dict[curr_queue]
                if io_issued is False:
                    queue[curr_queue].append(curr_job)
        else:
            # this job has more time at this level
            # just push it to the end of queue
            job_dict[curr_job][Key.TICKS_LEFT] = quantum_dict[curr_queue]
            if io_issued is False:
                queue[curr_queue].append(curr_job)

# Print out stats
print("")
print("Final stats:")
response_sum = 0
turnaround_sum = 0

for i in range(num_jobs):
    start_time = job_dict[i]["start_time"]
    response = job_dict[i][Key.FIRST_RUN] - start_time
    turnaround = job_dict[i]["end_time"] - start_time
    print(
        f"  Job {i:2d}: startTime {start_time:3d} - response {response:3d} - turnaround {turnaround:3d}"
    )
    response_sum += response
    turnaround_sum += turnaround

avg_response = float(response_sum) / num_jobs
avg_turnaround = float(turnaround_sum) / num_jobs
print(f"\n  Avg response {avg_response:.2f} - turnaround {avg_turnaround:.2f}")
print("\n")
