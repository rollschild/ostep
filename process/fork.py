#! /usr/bin/env python3
"""
This file generates a "process tree" for processes that fork or are forked by 
each other.
"""
from argparse import ArgumentParser
import random
import sys
import string


def random_randint(low, high):
    return int(low + random.random() * (high - low + 1))


def random_choice(L):
    return L[random_randint(0, len(L) - 1)]


class Forker:
    def __init__(
        self,
        fork_percentage,
        actions,
        action_list,
        show_tree,
        just_final,
        leaf_only,
        local_reparent,
        print_style,
        solve,
    ) -> None:
        self.fork_percentage = fork_percentage
        self.max_actions = actions
        self.action_list = action_list
        self.show_tree = show_tree
        self.just_final = just_final
        self.leaf_only = leaf_only
        self.local_reparent = local_reparent
        self.print_style = print_style
        self.solve = solve

        # root process is always `a`
        self.root_name = "a"

        self.process_list = [self.root_name]

        self.children = {}
        self.children[self.root_name] = []

        self.parents = {}

        # pretty printing
        self.name_length = 1
        self.base_names = string.ascii_lowercase + string.ascii_uppercase
        self.curr_names = self.base_names
        self.curr_index = 1

        return

    def grow_names(self):
        new_names = []
        for b1 in self.curr_names:
            for b2 in self.base_names:
                new_names.append(b1 + b2)
        self.curr_names = new_names
        self.curr_index = 0
        return

    def get_name(self):
        if self.curr_index == len(self.curr_names):
            self.grow_names()

        name = self.curr_names[self.curr_index]
        self.curr_index += 1
        return name

    def walk(self, p, level, pmask, is_last):
        print(f"{' ':31}", end="")
        if self.print_style == "basic":
            for _ in range(level):
                print(f"{' ':3}", end="")
            print(f"{p:2}")
            for child in self.children[p]:
                self.walk(child, level + 1, {}, False)
            return
        if self.print_style == "line1":
            chars = ("|", "-", "+", "|")
        elif self.print_style == "line2":
            chars = ("|", "_", "|", "|")
        elif self.print_style == "fancy":
            chars = ("\u2502", "\u2500", "\u251c", "\u2514")
        else:
            print(f"BAD style {self.print_style}!")
            sys.exit(1)

        # print stuff before the node
        if level > 0:  # root has level of 0
            for i in range(level - 1):
                if pmask[i]:
                    # "|  "
                    print(f"{chars[0]}   ", end="")
                else:
                    print(f"{' ':4}", end="")
            if pmask[level - 1]:
                # "|__"
                if is_last:
                    print(f"{chars[3]}{chars[1]}{chars[1]} ", end="")
                else:
                    print(f"{chars[2]}{chars[1]}{chars[1]} ", end="")
            else:
                # "___"
                print(" {chars[1]}{chars[1]}{chars[1]} ", end="")

        # print the node
        print(f"{p}")

        # undo parent verticals
        if is_last:
            pmask[level - 1] = False

        # recurse
        pmask[level] = True
        for child in self.children[p][:-1]:
            self.walk(child, level + 1, pmask, False)
        for child in self.children[p][-1:]:
            self.walk(child, level + 1, pmask, True)
        return

    def print_tree(self):
        return self.walk(self.root_name, 0, {}, False)

    def do_fork(self, p, c):
        self.process_list.append(c)
        self.children[c] = []
        self.children[p].append(c)
        self.parents[c] = p
        return f"{p} forks {c}"

    def collect_children(self, p):
        if self.children[p] == []:
            return [p]
        else:
            L = [p]
            for c in self.children[p]:
                L += self.collect_children(c)
            return L

    def do_exit(self, p):
        # remove the process from the process_list
        if p == self.root_name:
            print("root process: CANNOT exit!")
            sys.exit(1)
        exit_parent = self.parents[p]
        self.process_list.remove(p)

        # for each orphan, set its parent to exiting process's parent or root
        if self.local_reparent:
            for orphan in self.children[p]:
                self.parents[orphan] = exit_parent
                self.children[exit_parent].append(orphan)
        else:
            # set ALL descendants to be child of ROOT
            desc = self.collect_children(p)
            desc.remove(p)
            for d in desc:
                self.children[d] = []
                self.parents[d] = self.root_name
                self.children[self.root_name].append(d)

        # remove the entry from its parent's child list
        self.children[exit_parent].remove(p)
        self.children[p] = -1  # should NEVER be used again
        self.parents[p] = -1  # should NEVER be used again

        return f"{p} EXITS!"

    def bad_action(self, action):
        print(f"BAD action ({action})! Must be X+Y or X- where X and Y are processes!")
        sys.exit(1)
        return

    def check_legal(self, action):
        if "+" in action:
            tmp = action.split("+")
            if len(tmp) != 2:
                self.bad_action(action)
            return [tmp[0], tmp[1]]
        elif "-" in action:
            tmp = action.split("-")
            if len(tmp) != 2:
                self.bad_action(action)
            return [tmp[0]]
        else:
            self.bad_action(action)
        return []

    def run(self):
        print(f"{' ':27}Process Tree:")
        self.print_tree()
        print("")

        if self.action_list != "":
            # use specific (user-provided) action_list
            action_list = self.action_list.split(",")
        else:
            action_list = []
            actions = 0
            tmp_process_list = [self.root_name]
            level_list = {}
            level_list[self.root_name] = 1

            while actions < self.max_actions:
                if random.random() < self.fork_percentage:
                    # FORK
                    fork_choice = random_choice(tmp_process_list)
                    new_child = self.get_name()
                    action_list.append(f"{fork_choice}+{new_child}")
                    tmp_process_list.append(new_child)
                else:
                    # EXIT
                    exit_choice = random_choice(tmp_process_list)
                    if exit_choice == self.root_name:
                        continue
                    tmp_process_list.remove(exit_choice)
                    action_list.append(f"{exit_choice}-")
                actions += 1

        for a in action_list:
            tmp = self.check_legal(a)
            if len(tmp) == 2:
                fork_choice, new_child = tmp[0], tmp[1]
                if fork_choice not in self.process_list:
                    self.bad_action(a)
                action = self.do_fork(fork_choice, new_child)
            else:
                exit_choice = tmp[0]
                if exit_choice not in self.process_list:
                    self.bad_action(a)
                if self.leaf_only and len(self.children[exit_choice]) > 0:
                    action = f"{exit_choice} EXITS (FAILED: has children!)"
                else:
                    action = self.do_exit(exit_choice)
            if self.show_tree:
                if self.solve:
                    print("Action:", action)
                else:
                    print("Action?")
                if not self.just_final:
                    self.print_tree()
            else:
                print("Action:", action)
                if not self.just_final:
                    if self.solve:
                        self.print_tree()
                    else:
                        print("Process Tree?")
        if self.just_final:
            if self.show_tree:
                print(f"\n{' ':24}Final Process Tree:")
                self.print_tree()
                print("")
            else:
                if self.solve:
                    print(f"\n{' ':24}Final Process Tree:")
                    self.print_tree()
                    print("")
                else:
                    print(f"\n{' ':24}Final Process Tree?")
        return


# Main running point

# Parse args
parser = ArgumentParser()
parser.add_argument(
    "-s",
    "--seed",
    default=-1,
    help="the random seed",
    action="store",
    type=int,
    dest="seed",
)
parser.add_argument(
    "-f",
    "--forks",
    default=0.7,
    help="percent of actions that are forks (NOT exits)",
    action="store",
    type=float,
    dest="fork_percentage",
)
parser.add_argument(
    "-A",
    "--action_list",
    default="",
    help="the action list, instead of randomly generated ones (format: a+b,b+c,b- means a fork b, b fork c, b exit)",
    action="store",
    dest="action_list",
)
parser.add_argument(
    "-a",
    "--actions",
    default=5,
    help="number of forks/exits to do",
    action="store",
    type=int,
    dest="actions",
)
parser.add_argument(
    "-t",
    "--show_tree",
    default=False,
    help="show tree (not actions)",
    action="store_true",
    dest="show_tree",
)
parser.add_argument(
    "-P",
    "--print_style",
    default="fancy",
    help="tree print style (basic, line1, line2, fancy)",
    action="store",
    dest="print_style",
)
parser.add_argument(
    "-F",
    "--final_only",
    default=False,
    help="just show the final state!",
    action="store_true",
    dest="just_final",
)
parser.add_argument(
    "-L",
    "--leaf_only",
    default=False,
    help="only leaf processes exit",
    action="store_true",
    dest="leaf_only",
)
parser.add_argument(
    "-R",
    "--local_reparent",
    default=False,
    help="reparent to local parent",
    action="store_true",
    dest="local_reparent",
)
parser.add_argument(
    "-c",
    "--compute",
    default=False,
    help="compute answers for me",
    action="store_true",
    dest="solve",
)

args = parser.parse_args()

if args.seed != -1:
    random.seed(args.seed)

if args.fork_percentage <= 0.001:
    print("fork_percentage must be > 0.001")
    sys.exit(1)

print("")
print("ARG seed", args.seed)
print("ARG fork_percentage", args.fork_percentage)
print("ARG actions", args.actions)
print("ARG action_list", args.action_list)
print("ARG show_tree", args.show_tree)
print("ARG just_final", args.just_final)
print("ARG leaf_only", args.leaf_only)
print("ARG local_reparent", args.local_reparent)
print("ARG print_style", args.print_style)
print("ARG solve", args.solve)
print("")

f = Forker(
    args.fork_percentage,
    args.actions,
    args.action_list,
    args.show_tree,
    args.just_final,
    args.leaf_only,
    args.local_reparent,
    args.print_style,
    args.solve,
)
f.run()
