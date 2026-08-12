---
title: 365 Days Xuanwu Job Note
date: 2026-08-11 15:33:37
categories:
- dev
- cybersecurity
---

来源: 知名开源项目https://github.com/Vancir/365-days-get-xuanwulab-job

对内容进行了一些更新，以及部分比较基础的内容去除/合并了。以下是学习笔记

### Day 1
这两日的主要内容是经典的stackoverflow加上ROP exploit. 主要使用的工具是pwntools, pwndbg, ghidra
首先是复习一些x86的汇编

`call`等价于
* push the address of the next instruction (return address)
* jump to the function

cdecl calling convention: 由caller来修改esp(即清除stack上的arguments)

`leave`即离开当前stack frame，约等于把ebp和esp归位
`ret` pop出return address然后jump回去
`dword ptr`: double word pointer
`dword ptr [esp], eax`: 将esp视作指向32bit value的pointer，将eax的值写入其中

工具和小技巧:
* `pwndbg`中可以设置`layout pwndbg`，类似于gdb自己的tui，可以可视化地看assembly, stack之类的。ctrl+x a关闭/开启
* `pwndbg`可以用`tele`查看stack上的状况
* `strings`查看executable中的ascii字符串，用`-n`指定最短长度，比如5

ROP(return oriented programming)是一种利用程序中已有的一些gadgets来改变某些register/变量的值，进而达到控制整个control flow的目的的攻击方式

接下来讲解[basic ROP](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/basic-rop/)中的几个案例。

**ret2text**: 首先用`checksec`看到没有PIE。然后直接启动pwndbg在main打上bp。用`strings`查找字符串发现有`/bin/sh`，然后在pwndbg中search找到对应的位置。
我们会发现有个隐藏的`secure`函数(可以通过ghidra/IDA也可以通过直接查看symbols来确认)
然后我们查看ebp和buffer的地址，然后算出偏移，就可以直接构造payload了。需要overwrite的值就是`buffer - ebp + 4`，`ebp`指向的地方存的是旧的ebp，在他上面则是存的return address
也可以直接用`pwn cyclic`生成cyclic 串然后输入，再直接看ebp的地方存了什么，然后用`pwn cyclic -l`查看就行。

**ret2shellcode**: 基本上一样，区别在于目标buffer从stack移动到了bss。然后我们需要自己构造shellcode填入buffer然后执行。

**ret2syscall**: 这个更加复杂一些。首先找到return address的offset是112。然后我们的目标是利用gadgets来执行`execve("/bin/sh", NULL, NULL)`来获得shell。

我们需要构造的stack长这样
```text
lower addresses
+-----------------------------+
| 0x080bb196                  | <- pop eax ; ret
+-----------------------------+
| 0x0000000b                  | <- value for EAX // pop eax会吃掉这个
+-----------------------------+
| 0x0806eb90                  | <- pop edx ; pop ecx ; pop ebx ; ret
+-----------------------------+
| 0x00000000                  | <- value for EDX
+-----------------------------+
| 0x00000000                  | <- value for ECX
+-----------------------------+
| 0x080be408                  | <- value for EBX: address of "/bin/sh"
+-----------------------------+
| 0x08049421                  | <- int 0x80 // trigger syscall的interrupt
+-----------------------------+
higher addresses
```

基本原理就是，`ret`会从stack上pop出下一个instruction的地址，所以可以通过这种方式chain起来
我们需要用`ROPgadget`寻找这些gadget的地址，然后再构造payload

**ret2libc**: 
plt: Procedure Linkage Table
在执行libc函数，比如`puts`的时候，会出现`call puts@plt`，其中`.plt`中的`puts`不是真正的代码，而是一个跳板，帮助找到libc中真正`puts`的位置。
got: Global Offset Table
地址表，在第一次call的时候got中还没有libc函数的真正地址，因此plt会直接跑到`plt0`然后把控制权交给linker的resolver。最终会计算出`puts = libc_base + puts_offset`，而后写会got (即lazy binding，要用的时候再bind)。

因此，只需要把got中某个libc函数的address print出来，我们就可以知道offset，进而可以把control flow导向libc中的gadgets
如果PIE关闭，那么程序本身的`puts@plt`和`puts@got`是知道的。构造rop chain: 
```
pop rdi ; ret
puts@got  // elf.got["puts"]
puts@plt
main
```
然后再从print出的信息，计算offset从而构造新的payload执行attack。
如果开启了PIE，则main program自己也会被随机化base address，在这种情况下需要先想办法获取main program中某些的address，然后获得base，再加上`puts@plt`和`puts@got`的offset

这个就对应ret2libc的example 3的操作

