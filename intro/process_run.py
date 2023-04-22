#! /usr/bin/env python
from argparse import ArgumentParser
import sys
import random

# process states
STATE_READY = "READY"
STATE_RUNNING = "RUNNING"
STATE_DONE = "DONE"
STATE_WAIT = "BLOCKED"

# members of process structure
PROC_ID = "pid_"
PROC_CODE = "code_"
PROC_PC = "pc_"
PROC_STATE = "proc_state_"

# process tasks
DO_COMPUTE = "cpu"
DO_IO = "io"
DO_IO_DONE = "io_done"

# I/O finished behavior
IO_RUN_LATER = "IO_RUN_LATER"
IO_RUN_IMMEDIATE = "IO_RUN_IMMEDIATE"

# process switch behavior
SCHED_SWITCH_ON_IO = "SWITCH_ON_IO"
SCHED_SWITCH_ON_END = "SWITCH_ON_END"


class Scheduler:
    def __init__(self, process_switch_behavior, io_done_behavior, io_duration) -> None:
        self.proc_info = {}
        self.curr_proc = -1
        self.process_switch_behavior = process_switch_behavior
        self.io_done_behavior = io_done_behavior
        self.io_duration = io_duration
        return

    def new_process(self):
        proc_id = len(self.proc_info)
        self.proc_info[proc_id] = {}
        self.proc_info[proc_id][PROC_ID] = proc_id
        self.proc_info[proc_id][PROC_PC] = 0
        self.proc_info[proc_id][PROC_CODE] = []
        self.proc_info[proc_id][PROC_STATE] = STATE_READY
        return proc_id

    # program looks like this:
    #   c6,i,c4,i
    # which means
    #   compute for 6, then I/O, then compute for 4, then I/O
    def load_program(self, program):
        proc_id = self.new_process()
        for line in program.split(","):
            opcode = line[0]
            if opcode == "c":  # compute
                count = int(line[1:])
                for i in range(count):
                    self.proc_info[proc_id][PROC_CODE].append(DO_COMPUTE)
            elif opcode == "i":  # I/O
                self.proc_info[proc_id][PROC_CODE].append(DO_IO)
                # add one compute to handle I/O completion
                self.proc_info[proc_id][PROC_CODE].append(DO_IO_DONE)
            else:
                # print("Bad opcode %s (should be `c` or `i`)!" % opcode)
                print(f"Bad opcode {opcode} (should be `c` or `i`)!")
                sys.exit(1)
        return

    def load(self, program_description):
        proc_id = self.new_process()
        tmp = program_description.split(":")
        if len(tmp) != 2:
            print(f"Bad description ({program_description}): Must be number <x:y>")
            print("  where X is the number of instructions,")
            print("  and Y is the percent chance that an instruction is CPU, not I/O")
            sys.exit(1)
        num_instructions, chance_cpu = int(tmp[0]), float(tmp[1]) / 100.0
        for i in range(num_instructions):
            if random.random() < chance_cpu:
                self.proc_info[proc_id][PROC_CODE].append(DO_COMPUTE)
            else:
                self.proc_info[proc_id][PROC_CODE].append(DO_IO)
                self.proc_info[proc_id][PROC_CODE].append(DO_IO_DONE)
        return

    def move_to_ready(self, expected, pid=-1):
        if pid == -1:
            pid = self.curr_proc
        assert self.proc_info[pid][PROC_STATE] == expected
        self.proc_info[pid][PROC_STATE] = STATE_READY
        return

    def move_to_wait(self, expected):
        assert self.proc_info[self.curr_proc][PROC_STATE] == expected
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_WAIT
        return

    def move_to_running(self, expected):
        assert self.proc_info[self.curr_proc][PROC_STATE] == expected
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_RUNNING
        return

    def move_to_done(self, expected):
        assert self.proc_info[self.curr_proc][PROC_STATE] == expected
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_DONE
        return

    def next_proc(self, pid=-1):
        if pid != -1:
            self.curr_proc = pid
            self.move_to_running(STATE_READY)
            return
        for pid in range(self.curr_proc + 1, len(self.proc_info)):
            if self.proc_info[pid][PROC_STATE] == STATE_READY:
                self.curr_proc = pid
                self.move_to_running(STATE_READY)
                return
        for pid in range(0, self.curr_proc + 1):
            if self.proc_info[pid][PROC_STATE] == STATE_READY:
                self.curr_proc = pid
                self.move_to_running(STATE_READY)
                return
        return

    def get_num_processes(self):
        return len(self.proc_info)

    def get_num_instructions(self, pid):
        return len(self.proc_info[pid][PROC_CODE])

    def get_instruction(self, pid, index):
        return self.proc_info[pid][PROC_CODE][index]

    def get_num_active(self):
        num_active = 0
        for _, state in self.proc_info.items():
            if state[PROC_STATE] != STATE_DONE:
                num_active += 1
        return num_active

    def get_num_runnable(self):
        num_runnable = 0
        for _, state in self.proc_info.items():
            if state[PROC_STATE] == STATE_RUNNING or state[PROC_STATE] == STATE_READY:
                num_runnable += 1
        return num_runnable

    def get_ios_in_flight(self, current_time):
        num_in_flight = 0
        for pid in self.proc_info:
            for t in self.io_finish_times[pid]:
                if t > current_time:
                    num_in_flight += 1
        return num_in_flight

    def check_for_switch(self):
        return

    def space(self, num_columns):
        for i in range(num_columns):
            # print("%10s" % " ", end="")
            print(f"{' ':>10}", end="")

    def check_if_done(self):
        if len(self.proc_info[self.curr_proc][PROC_CODE]) == 0:
            if self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING:
                self.move_to_done(STATE_RUNNING)
                self.next_proc()
        return

    def run(self):
        clock_tick = 0

        # Nothing to run, return
        if len(self.proc_info) == 0:
            return

        # Tracking outstanding I/Os, per process
        self.io_finish_times = {}
        for pid in self.proc_info:
            self.io_finish_times[pid] = []

        # Make the first process active
        self.curr_proc = 0
        self.move_to_running(STATE_READY)

        # Output: headers for each column
        print("Time", end="")
        for pid in self.proc_info:
            header = f"PID:{pid:2}"
            print(f"{header:>14}", end="")
        print(f"{'CPU':>14}", end="")
        print(f"{'I/Os':>14}", end="")
        print("")

        # init stats
        io_busy = 0
        cpu_busy = 0

        while self.get_num_active() > 0:
            clock_tick += 1

            # check for I/O finish
            io_done = False
            for pid in self.proc_info:
                if clock_tick in self.io_finish_times[pid]:
                    io_done = True
                    # initially this pid was waiting for I/O to finish
                    # now that I/O has finished, move to ready state
                    self.move_to_ready(STATE_WAIT, pid)
                    if self.io_done_behavior == IO_RUN_IMMEDIATE:
                        # IO_RUN_IMMEDIATE
                        if self.curr_proc != pid:
                            if (
                                self.proc_info[self.curr_proc][PROC_STATE]
                                == STATE_RUNNING
                            ):
                                self.move_to_ready(STATE_RUNNING)
                        self.next_proc(pid)
                    else:
                        # IO_RUN_LATER
                        if (
                            self.process_switch_behavior == SCHED_SWITCH_ON_END
                            and self.get_num_runnable() > 1
                        ):
                            # the process that issued the I/O should be run
                            self.next_proc(pid)
                        if self.get_num_runnable() == 1:
                            # there is only one thing to run; run it!
                            self.next_proc(pid)
                    self.check_if_done()

            # if curr_proc is running and has an instruction, execute it!
            instruction_to_execute = ""
            if (
                self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING
                and len(self.proc_info[self.curr_proc][PROC_CODE]) > 0
            ):
                instruction_to_execute = self.proc_info[self.curr_proc][PROC_CODE].pop(
                    0
                )
                cpu_busy += 1

            # OUTPUT - print
            if io_done:
                print(f"{clock_tick:>3}*", end="")
            else:
                print(f"{clock_tick:>3} ", end="")

            for pid in self.proc_info:
                if pid == self.curr_proc and instruction_to_execute != "":
                    instructoin_text = "RUN:" + instruction_to_execute
                    print(f"{instructoin_text:>14}", end="")
                else:
                    print(f"{self.proc_info[pid][PROC_STATE]:>14}", end="")

            # CPU output
            if instruction_to_execute == "":
                print(f"{' ':>14}", end="")
            else:
                print(f"{'1':>14}", end="")

            # I/O output
            num_outstanding = self.get_ios_in_flight(clock_tick)
            if num_outstanding > 0:
                print(f"{str(num_outstanding):>14}", end="")
                io_busy += 1
            else:
                print(f"{' ':>10}", end="")

            print("")

            # if this is I/O - start instrcution, switch to waiting state and add an I/O completion in the future
            if instruction_to_execute == DO_IO:
                self.move_to_wait(STATE_RUNNING)
                self.io_finish_times[self.curr_proc].append(
                    clock_tick + self.io_duration + 1
                )
                if self.process_switch_behavior == SCHED_SWITCH_ON_IO:
                    self.next_proc()

            # ENDCASE: check if currently running thing is out of instructions
            self.check_if_done()
        return (cpu_busy, io_busy, clock_tick)


# Parse arguments
parser = ArgumentParser()

parser.add_argument(
    "-l",
    "--processlist",
    default="",
    action="store",
    dest="process_list",
    help="a comma-separated list of processes to run, in the form X1:Y1,X2:Y2,... where X is the number of instructions that process should run, and Y the chances (from 0 to 100) that an instruction will use the CPU or issue an IO",
)
parser.add_argument(
    "-P",
    "--program",
    default="",
    dest="program",
    action="store",
    help="more specific controls over programs",
)
parser.add_argument(
    "-s",
    "--seed",
    default=0,
    help="the random seed",
    action="store",
    type=int,
    dest="seed",
)
parser.add_argument(
    "-L",
    "--ioduration",
    default=5,
    action="store",
    type=int,
    dest="io_duration",
    help="how long an I/O takes",
)
parser.add_argument(
    "-S",
    "--switch",
    default="SWITCH_ON_IO",
    action="store",
    dest="process_switch_behavior",
    help="when to switch between processes: SWITCH_ON_IO, SWITCH_ON_END",
)
parser.add_argument(
    "-I",
    "--iodone",
    default="IO_RUN_LATER",
    action="store",
    dest="io_done_behavior",
    help="type of bahavior when I/O ends: IO_RUN_LATER, IO_RUN_IMMEDIATE",
)
parser.add_argument(
    "-c",
    default=False,
    action="store_true",
    dest="solve",
    help="compute the answers for me",
)
parser.add_argument(
    "-p",
    "--printstats",
    default=False,
    action="store_true",
    dest="print_stats",
    help="print stats at end; only useful with the -c flag (otherwise stats are not printed)",
)
args = parser.parse_args()

random.seed(args.seed)

assert (
    args.process_switch_behavior == SCHED_SWITCH_ON_IO
    or args.process_switch_behavior == SCHED_SWITCH_ON_END
)
assert (
    args.io_done_behavior == IO_RUN_IMMEDIATE or args.io_done_behavior == IO_RUN_LATER
)
s = Scheduler(args.process_switch_behavior, args.io_done_behavior, args.io_duration)

if args.program != "":
    for p in args.program.split(":"):
        s.load_program(p)
else:
    for p in args.process_list.split(","):
        s.load(p)

assert args.io_duration >= 0

if args.solve == False:
    print("Produce a trace of what would happen when you run these processes:")
    for pid in range(s.get_num_processes()):
        print(f"Process {pid}")
        for inst in range(s.get_num_instructions(pid)):
            print(f"  {s.get_instruction(pid, inst)}")
        print("")
    print("Important behaviors:")
    print("  System will switch when ", end="")
    if args.process_switch_behavior == SCHED_SWITCH_ON_IO:
        print("the current process is FINISHED or ISSUES an I/O")
    else:
        print("the current process is FINISHED")
    print("  After I/Os, the process issuing the I/O will ", end="")
    if args.io_done_behavior == IO_RUN_IMMEDIATE:
        print("run IMMEDIATELY")
    else:
        print("run LATER (when it is its turn)")

    print("")
    sys.exit(0)

(cpu_busy, io_busy, clock_tick) = s.run()

if args.print_stats:
    print("")
    print(f"Stats: Total Time {clock_tick}")
    print("Stats: CPU Busy {} ({:.2%})".format(cpu_busy, float(cpu_busy) / clock_tick))
    print("Stats: I/O Busy {} ({:.2%})".format(io_busy, float(io_busy) / clock_tick))
    print("")
