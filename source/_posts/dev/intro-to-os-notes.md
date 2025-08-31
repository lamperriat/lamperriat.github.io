---
title: 'Notes: Introduction to Operating Systems (English)'
date: 2025-08-30 11:35:12
categories:
    - dev
    - notes
---


*本篇为课程笔记，仅供参考*

# ECE482

SPOOL: Simultaneous Peripheral Operation On Line. Load a new job from disk, run it, and output it on disk (slow). (take turn)

Commands to see processes: `ps aux`, `top`
Some other commands: `wc`(word count), `hexdump`(display in hex/oct)

Some open-source projects to look at:

* TinyCC compiler
* qemu, KVM, FFmpeg, xephir

controller = a chip that controls the mechanical part. 

seg fault: access memory does not belong to the program

Three rings. (user, root, kernel)

* For users: only able to access part of the memory
  * root: software privilege, but still a user 
  * kernel: hardware privilege
* Inside the kernel: be able to access everything
* System calls: for users to run kernel-only instructions

Program status word: control bits indicating what priv I have

VM: emulators. translate. only 2 rings, priv or unpriv

CPUs:

* pipeline: fetch($n+2$-th instruction)->decode($n+1$-th ins)->execute($n$-th ins)
  * any ins fetched must be executed
  * issue: conditional statements. until execution, we cannot know where to branch
* superscalar:
  * multiple exec units
  * multiple ins fetched and decoded at a time
  * ins in buffer to be exec
  * issue: no specific order in buffer (some exec unit can go faster)

Simultaneously (real parallel, access one CPU at the same time) vs. Concurrently (alive at the same time, take turn to access the CPU)

`lscpu`: see info about cpu

Terms:

* socket: physical computing component (cpu slot)
* threads: max number of instr that ca be passed through or processed simultaneously by a single core. 
* num of logical cores: num of cores times num of threads

process = software + info the software need

nvme: ssd

block vs. stream devices

* block files: for storage devices (e.g. hard disks, RAM) 
* character files: for devices accepting/outputting streams (e.g. random, stdin, stdout, stderr, network card)

most devices are stream

`mkfifo`: create a FIFO, a named pipe. 
`mount`: display devices mounted. mount a device somewhere. `umount` to unmount.
`sshfs`: mount the server files locally

Most OS are interrupt driven

DMA: Direct Memory Access
Controller directly go to the memory without going through the CPU.

* If CPU is busy, good because it will not interrupt CPU often.
* If CPU is not busy, bad because CPU is faster.

Three strategies(!):

* busy waiting
* interrupt
* DMA

IO are all privilege instructions.

Common OS structures:

* monolithic: most in kernel space. if something crashes (privileged), we have to reboot
* micro: most in user space. potentially slower. if something crashes (no much different from other user programs), the kernel can still work

linux: monolithic but there are modules.
mac: micro
Crossing the line between user/kernel space is expensive.

# C2 Processes and threads

* CPU *quickly* switches from process to process
* each process for 10-100ms (Important!)
* processes hide the effect of interrupts

multiprogramming: a PC for each program

* rate of computation of a procss is not uniform/reproducible
* potential issues (time constraints):
  * eg. read from tape. switch back too late

run a program twice generates two processes

* program = sequence of ops to perform
* process: program + io + state (everything the program needs)
* `/proc/pid` stores the info about a process.

init process: pid 1

* command: `/sbin/init`

processes end

* voluntarily: work completed or error noticed and exit nicely
* involuntary: crash or be killed
  * `killall`: kill processes by name
  * `kill -L` see the signals that can be used to kill
  * `kill` by default use `15: SIGTERM`, i.e. tell the process to exit (nicely)
  * `kill -9` use `9: SIGKILL`
  * `ctrl \`: real kill

process hierarchies:

* unix-like:
  * a parent creates a child
  * process group
  * cannot disinherit a child
* windows:
  * all processes are equal
  * parent has the token to control the child, but can be given to another process

How to choose who to run?
process states:

* running, ready, blocked
  * blocked: wait for some input, etc.
  * ready: processes that could be running
* lowest level of OS is the scheduler
* interrupt handling, starting/stopping processes are hidden
* abstraction. higher level only needs to think of processes.

Process: a data structure *process control block*.

* includes: state, PC, SP, memory alloc, files, scheduling info

On interrupt:

* save reg/setup new stack in assembly. 
* low level hardware only in assembly.

## Thread

A process is a big box. Threads are inside the box to help it run.

A thread is the basic unit of CPU utilisation

* Thread ID, PC, reg set, stack space

* Threads in a process share the same data section, OS resources, code section.

* thread has the same possible states as a process

* a process starts with one thread and can create more

* processes compete; thread cooperate

* threads can give up the CPU

Keep one thread listerning, and create new threads.

segfault detect: hardware-interrupt-OS-check indeed illegal-SIGSEGV(seg violation)-awake-by default kill

## Implmentation

POSIX threads:

All in user space

* one blocked, process blocked
* but efficient switch

All in kernel space

* one blocked, others still run (chosen by kernel)
* slower

Hybrid

* hard to handle schedule

# Interprocess communication

race condition

Synchronization mechanism
Interrupts are not predictable. (even at `&&`)

Peterson's idea:

* When wanting to enter:
  * show your interest
  * busy waiting
  * signal the departure

Mutual Exclusion

* Disable interrupts
  * short amount of time
  * interrupts may be long/short.  
* Atomic operations: Something that cannot be divided
  * Either happen, or not
  * Supported in hardware level
  * `A = B` -> read B AND save to A. atomic: do it at once 

More locks -> slower performance
Semaphore

```c
sem.down() {
  while (sem == 0) sleep();
  sem--;
}
sem.up() {
  sem++;
}
```

Semaphore: block a process

* a down on a semaphore with 0 is blocked

Mutex: lock itself

Monitors: attempt to merge sync with OOP.

* mutex and locks are handled automatically by the compiler
* a special type of class

Barriers:

* useful when several processes must be completed before a certain stage
* example: several threads that sieve the space. should be finished before starting execution

# Scheduling

## Requirements

MPI: message passing interface: lower level

Compute bound/IO bound. 
Scheduling algo: choose processes with intense IO first

Preemptive (most common, in linux):

* a process is run for at most $n$ ms. 
* not completed then suspended, another process is selected.

Non-preemptive:

* a process is run until it blocks
* resumed after an interrupt, unless there is process of higher priority.

Goals:

* fairness
* balance
* follow the policy (kind of some extra param, can be modified in /sys/kernel/)

Interactive system:

* quick response
* meet user's expect

Batch system:

* no need to be preemptive
* throughput: maximize the number of jobs
* turnaround time: minimize time between submission and termination

Real-time system:

* meet deadlines: avoid data loss
* predictability: avoid quality degration

## Common algo

first come first served: for batch sys. 
shortest job first: for batch sys. (less turnaround time) need pre-info.
round-robin: interactive sys. processes run until blocked, quantun elapsed, interrupted, completed
priority scheduling: interactive sys. priority classes + robin in the class (most used)
lottery scheduling: interactive sys, sometimes real-time. random tickets choosed. can simulate priority sche
early deadline first: realtime sys. may miss the deadline if too close

policy = extra parameters
mechanism = algorithm

# Deadlock

Resources type

* Preemptable: resources that can be safely taken away
* Non-preemptable: resources cannot be safely taken away

Ostrich algorithm:

* The OS simply ignores it

Recovery strategy:

* preemption: taking the resource from others
* kill: hard to decide who to kill
* rollback: expensive

# Memory management

Allocating memory:

* first fit: used in practice
* best fit: greedy, cause the memory to be fragmented
* quick fit: faster best fit

virtual memory:

* address space $\to$ pages
* pages $\to$ physical memory

Swap:

* defined by origin and size (two numbers)
* allocate pages on disk
* a list of free chunks
* process start. swap reserved. process ends, swap freed.
  * One on one map. Each page has a swap on disk. allocate, but not used immediately
  * disk map. map pages not frequently used to swap.

pagesize: `/proc/meminfo`, free, vmstat
swap file: /proc/swaps
enable/disable swap: swapon/swapoff <swapfile>
swap is at the end of disk
fallocate: allocate empty big file. can be used as swap file
oomkiller: out of memory:

* either swap
* or kill

reasonable size for swap: twice the RAM.

* when hibernate: all content of RAM will be copied to swap

CPU package = the square chip = subchips (CPU+MMU+...)
`%s` is bad in scanf. use `%6s` ensures at most 6 chars are read. 

in linux

* buddy system: for at least 4kb (page size). if the buddy of chunk not freed, then wait for it freed
* slab system: divide the page into small chunks

copy on write (cow):

* when fork, copy the page table only, but marked as read only
* if write occurs, do the real copy and points to the copied page

`ldd [executable]`: list dynamic library dependencies
`pmap [pid]`: see memory use of process

dangerours to work remotely: update ssh, firewall, disk partition
firewall should be reset at least once a day
In `/etc/ld*`, tell the system where to find dynamic lib

Non-shared library is faster (libraries are distributed in a more compact way in memory, smaller jumps will be needed )

C keyword:

* `register`: hint the compiler to store the variable in register because it will be heavily used. not recommended because modern compilers can do that better than humans.

* `volatile`: for global variables that will be accessed by others. avoid compiler optimization. for stream devices (say network card), there is no need to cache the buffer. it can be modifed by the device easily, so it should be volatile. everything will be modifed externally need `volatile`. 

JIT compiler: just-in-time

segment: each segment composes of pages.

segment table = record base (starting physical address) + size (limit)

|                        | page    | segmentation | reason                            |
| ---------------------- | ------- | ------------ | --------------------------------- |
| limited by size of ram | n       | n            | swap                              |
| separate to protect    | n       | y            | seg can be set as rw, x, rwx, ... |
| share between programs | complex | easy         |                                   |

# IO Devices

xmodmap: modify keycode map

device = mechanical + electronic (device controller)

error correction: in each level, from hardware to software

telnet

modern approach: map buffer to memory space

* no need for assembly

* buffer should not be cached

SLAB system: for far smaller than one page

Buddy system: for pages

`kmalloc` decides what to do depending on the page size

Q: how does `malloc` work?

sysctl -a

* precise interrput: PC represents the precise progress. Fast to handle, but hard to be precise in modern CPUs

* inprecise interrupt: Instructions near PC may be in different stages. Slow to handle.

* Balance: 
  
  * More parallel: faster, but slower to deal with interrupt
  
  * Add interrupt unit: faster to handle, but spaces are occupied and things become slower

Software IO strategies

* programmed IO: kind of like busy waiting

* interrupt IO

* DMA: similar to programmed IO, but work are done by DMA

IO software:

* In linux, every device is represented as a file

* Unified high level API

* `snd`: sound card

* `/dev/disk` or `nvme0*`: ssd

* get color for `ls`: `ls --color`

Common functions: read, write

`fluxbox` window manager

Use `ls -l /dev`

* Two numbers: major, minor

* `mknod`: make block or character device

Modules:

* `lsmod`: list module. name, size, used by (dependency)

* `depmod -a`: see module dependcies

* `modprobe`: install module, can handle dependency (preferred)

* `insmod`: simple one, cannot handle dependency

* `/lib/modules`: modules loaded when booting

* `/sys/class/...`: config for screen brightness/volume/...

* map the keyboard buttons to some script that changes the brightness. all done in software

* `lshw`: see all hardware info (\*)

* `dmidecode`: more detailed information 

* `lspci`: (with `-n`: computer-friendly message) 

Key idea: everything is a file

# File System

VM: small, volatile, process-dependent

filename: case-sensitive (linux)/insensitive (mac, win)

file type in metadata (magic number at the first few bytes), changing the suffix does not affect the result of file.

* advantage of linux approach: safer, no false positive

* advantage of win approach: not safe, but faster (no need opening file)

`lsattr`, `chattr`: more about file attributes

* `i` attribute: immutable

Link:

* softlink: creates a new file pointing to another file

* hardlink: different path/name for the same file. there will be a counter (`ls -l`). unless counter reaches 1, we cannot remove the file.

* `sshfs remote: local_dir`: mount remote directory to a local one

* cannot cross-device hardlink (limited to the same partition), but symbolic (soft) link is fine.

Disk = MBR(master boot record, old style)+partition table+partitions

modern: `EFI`

each file system has a magic number (to identify what it is), also each file type

parition = 

* Boot block

* super block: what is this filesystem about

* free space management

* I-nodes

* root dir

Boot with no OS:

* Bios start and try to load something

* cannot find. ask you to plug in the device

`ls /dev/disk`: list by ...

* `nvme0n1p?` is not fixed. may change after rebooting

* `uuid` is fixed.

Contiguous allcoation:

* simple to implement

* good for read-only files

`testdisk/photorec`: recover

We can directly read the `/dev/<disk>` in hex.

Index Nodes:

* a data structure storing

* file attrs

* 12 regular blocks containing data (fast access to small files)

* block 12: points a block that contains pointers to more blocks (one step)

* block 13: two steps before reaching the data

* block 14: three steps

* even more levels...

* `ls -i`: inode. inode 1 in `/` is used for root, everything is mounted instead of real folder

* The essence of hardlink: same inode. A counter is on the inode structure to keep track of the number 

Management:

* small block size: waste of time

* large block size: waste of space

Commands:

* `fdisk -l`: disk info

* `free`: memory info

* `blockdev --getbsz ...`: 

* `du -h file`: size of a file

* different file systems may have different block size

`git-fsck`: file system check. running it on a mounted file system is dangerous, may cause data loss.

Magic sysRq key

RAID: Redundant Arrays of Inexpensive Disks

* `chmod`: e.g. `wrx` for user `u+wrx` 

facl: file access control list

* `id -a`: list groups I belong to

* `usermod`, `groupadd`

SMP: Symmetric Multi-Processor
