---
title: 后端面试八股
date: 2025-08-28 20:06:49
categories: 
    - dev
    - backend
---

在学习过程中记录的一些问题，**并非面经**！

(1) 在一个复杂的SQL query的运行过程中，MySQL的执行过程是？将以下clause按照执行顺序先后排序。

`SELECT`, `FROM`, Window Functions, `WHERE`, `HAVING`, `JOIN`, `DISTINCT`, `ORDER BY`, `GROUP BY`, `LIMIT`, `OFFSET`

Tag: Database, MySQL

<details>
<summary>Answer: </summary>

`FROM` and `JOIN` < `WHERE` < `GROUP BY` < `HAVING` < Window Functions < `SELECT` < `DISTINCT` < `ORDER BY` < `LIMIT` and `OFFSET`

</details>

(2) Go语言的sysmon如何检查死锁？

Tag: Golang, Operating System

<details>
<summary>Answer: </summary>

先检查正在运行的线程数量，为0则检查goroutine状态，都为runnable，syscall，running则说明死锁；继续检查计时器，如果没有计时器则死锁。
</details>

(3) 简述Go语言的内存管理系统

Tag: Golang, Operating System

<details>
<summary>Answer: </summary>

分级分配。每个线程有线程缓存，在这之上还有中心缓存。对于大对象，直接在页堆进行分配。内存不足则向上一级申请，页堆不足则申请扩容。
</details>

(4) 在跳表中，如何决定插入一个值时是否需要向上建立索引？

Tag: Data Structure, Database

<details>
<summary>Answer: </summary>

随机决定
</details>

(5) 简述红黑树的插入过程

Tag: Data Structure

<details>
<summary>Answer: </summary>

插入默认红，维护不红红。看叔叔节点，不论哪种情况，都可以先旋转，再判断如何重新染色。删除也是这样。
</details>

(6) 在MySQL中，如何进行类似前缀和的操作？

Tag: Database, MySQL

<details>
<summary>Answer: </summary>

使用窗口函数，配合`ROWS BETWEEN`(行数范围)或者`RANGE`(数值范围)
</details>

(7) 在MySQL中，以下两句查询的区别是(`id`为主键)？

a. `select * from t_user where id + 1 = 10;`

b. `select * from t_user where id = 10 - 1;`

Tag: Database, MySQL

<details>
<summary>Answer: </summary>

前者会进行全表扫描，后者可以使用索引
</details>

(8) 在MySQL中，为什么对字符串类型的索引传入整型会导致索引失效，但反之并不会？

Tag: Database, MySQL

<details>
<summary>Answer: </summary>

假设`phone`字段是字符串索引，以下查询
```sql
select * from user where phone = 1330000111
```
实际上相当于
```sql
select * from user where CAST(phone AS signed int) = 1330000111
```
也就是自动转化了左边的phone到数字，而不是右边的数字到字符串。反过来的话，如果左边是int索引，右边用字符串会被转化int，最终int类型索引仍然可以生效。
</details>

(9) 日语中，祝你好运的口语和书面表法分别是？

Tag: Japanese

<details>
<summary>Answer: </summary>

ご幸運を、幸運(こううん)を祈(いの)ります
</details>

(10) 在MySQL中，用正则表达式匹配字符串中出现在单词开头的"hel"，单词由任意非空白字符组成

Tag: MySQL, Regular Expression

<details>
<summary>Answer: </summary>

`field REGEXP (^| )hel`
</details>

(11) `DENSE_RANK`和`RANK`的区别是？

Tag: MySQL

<details>
<summary>Answer: </summary>

`DENSE_RANK`会给相同值的行附加相同的rank
</details>

(12) 说一个简单的防止重放攻击(replay attack)的方式

Tag: Computer Networking, Cryptography, Cyber Security

<details>
<summary>Answer: </summary>

每次会话使用一个不重数(nonce)
</details>

(13) Go语言的map采用了特殊的扩容机制使得在不断插入元素的过程中不会发生performance的骤降。简述这种扩容机制。

Tag: Golang

<details>
<summary>Answer: </summary>

增量扩容。并不是一次性全部搬过去，而是在后续CRUD过程中，每次将几个bucket从旧的map搬到新的map。
</details>

(14) 简述Go语言的GC(垃圾回收)算法

Tag: Golang

<details>
<summary>Answer: </summary>

标记清除+三色抽象+混合写屏障，核心在于维护三色不变性，目的在于增量且并发地进行GC。增量并发GC带来的问题是，一次GC的过程中可能有objects之间的引用关系发生变化，而这时候我们必须保证GC不会错误地回收造成垂悬引用。可以接受的是，部分应当回收的没有被回收，而会在下一次GC被回收。
</details>

(15) 以下三个`grep`命令是等价的吗？为什么？

```bash
grep -r "^[a-zA-Z0-9_]* {$" .
grep -r "^([a-z]|[A-Z]|[0-9]|_)* {$" .
grep -r -E "^([a-z]|[A-Z]|[0-9]|_)* {$" .
```

Tag: Shell Scripting, Regular Expression

<details>
<summary>Answer: </summary>

1和3是一样的，3会把括号当中的东西当作一个group去匹配。而不开启`-E`时，括号和竖线都会默认不escape，即当成普通字符处理。所以将2改成如下形式就和13等价了：
```bash
grep -r "^\([a-z]\|[A-Z]\|[0-9]\|_\)* {$" .
```
而原来的2会匹配诸如`(p|C|7|_)))`之类的行
</details>

(16) 下面两段Go语言代码打印出的值，或者说效果一致吗？

一：

```go
func testSlice()[]uintptr{
    var r []uintptr
    for i := 0; i < 10; i++ {
        tc := new(int)
        *tc = rand.Int() % 100
        fmt.Printf("%x: %d\n", tc, *tc)
        r = append(r, uintptr(unsafe.Pointer(tc)))
    }

    return r
}
func main() {
    slice := testSlice()
    println("-----in main------")
    fmt.Printf("%x: %d\n",slice[0], *((*int)(unsafe.Pointer(slice[0]))))
    fmt.Printf("%x: %d\n",slice[1], *((*int)(unsafe.Pointer(slice[1]))))
    fmt.Printf("%x: %d\n",slice[2], *((*int)(unsafe.Pointer(slice[2]))))
}
```

二：

```go
func testSlice()[]uintptr{
    var r []uintptr
    for i := 0; i < 10; i++ {
        tc := new(int)
        *tc = rand.Int() % 100
        // fmt.Printf("%x: %d\n", tc, *tc)
        r = append(r, uintptr(unsafe.Pointer(tc)))
    }

    return r
}
func main() {
    slice := testSlice()
    println("-----in main------")
    fmt.Printf("%x: %d\n",slice[0], *((*int)(unsafe.Pointer(slice[0]))))
    fmt.Printf("%x: %d\n",slice[1], *((*int)(unsafe.Pointer(slice[1]))))
    fmt.Printf("%x: %d\n",slice[2], *((*int)(unsafe.Pointer(slice[2]))))
}
```

三：

```go
func testSlice()[]*int{
    var r []*int
    for i := 0; i < 10; i++ {
        tc := new(int)
        *tc = rand.Int() % 100
        // fmt.Printf("%x: %d\n", tc, *tc)
        r = append(r, tc)
    }

    return r
}
func main() {
    slice := testSlice()
    println("-----in main------")
    fmt.Printf("%x: %d\n",slice[0], *((*int)(unsafe.Pointer(slice[0]))))
    fmt.Printf("%x: %d\n",slice[1], *((*int)(unsafe.Pointer(slice[1]))))
    fmt.Printf("%x: %d\n",slice[2], *((*int)(unsafe.Pointer(slice[2]))))
}
```

Tag: Golang

<details>
<summary>Answer: </summary>

一和三的效果一致。二中编译器并没有将`tc`分配到堆上，由于使用了unsafe pointer导致逃逸分析出现问题，因此产生了悬空指针的问题。三很显然，一我也不是很确定为什么加了一句print就可以帮助编译器分析出`tc`逃逸了进而分配到堆上。
</details>

(17) 简述MVCC的工作原理

Tag: MySQL, Database, Concurrency

<details>
<summary>Answer: </summary>

每条记录中包含两个隐藏的字段，一个记录修改本条记录的事务id，另一个指向上一个版本的同一条记录，即历史版本被串成一个链表。而当一个事务查询本条记录时，这个事务知道自己被创建时有哪些事务是未提交的，该事务沿着链表查找直到遇到在自己被创建时已经提交的事务所修改的版本
</details>

(18) 在使用`stringer`工具时，解释生成的代码中以下部分的作用

```go
func _() {
    // An "invalid array index" compiler error signifies that the constant values have changed.
    // Re-run the stringer command to generate them again.
    var x [1]struct{}
    _ = x[Placebo-0]
    _ = x[Aspirin-1]
    _ = x[Ibuprofen-2]
    _ = x[Paracetamol-3]
}
```

Tag: Golang

<details>
<summary>Answer: </summary>

该代码不会被执行，如注释所说，用处是利用编译期的数组越界检查确保生成的代码合法且没有在生成后修改过原代码。
</details>

(19) 在MySQL中，对于当前读的语句，如`select ... for update`，在`where`语句中使用non-index列会对加锁产生什么影响？

Tag: MySQL, Concurrency

<details>
<summary>Answer: </summary>

使用index列只会小范围加锁，而使用non-index列直接全表加锁
</details>

(20) Linux操作系统中的调度器是？

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

主要有两个。一是CFS Completely Fair Scheduler，设计上，按照官方的说法是"model an ideal, precise multi-task CPU on real hardware"。使用红黑树把作为存放任务的数据结构，合适地处理NICE值。第二个是新出的EEVDF Earliest Eligible Virtual Deadline First，细节可以通过这里了解：[Completing the EEVDF scheduler [LWN.net]](https://lwn.net/Articles/969062/)。
</details>

(21) 构造出一个导致MySQL(InnoDB)中出现死锁的场景。

Tag: Operating System, MySQL, Concurrency

<details>
<summary>Answer: </summary>

实际上官网里就有[MySQL :: MySQL 8.4 Reference Manual :: 17.7.5.1 An InnoDB Deadlock Example](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlock-example.html)。简单来说就是两个事务A和B，A先获取锁1再获取锁2，B先获取锁2再获取锁1，就达成死锁了。因为死锁四大条件中，前三个 互斥、hold and wait、unpreemptive都是我们改变不了的，所以构成循环等待就等于构成死锁。
</details>

(22) MySQL中有redo log，即每次修改完数据库先把结果写在log里面，再写回磁盘。但redo log本身也需要写回磁盘来确保ACID中的持久性。为何要多此一举？

Tag: MySQL, Operating System

<details>
<summary>Answer: </summary>

因为log可以顺序写入，而记录本身是随机写入的。对于HDD/SSD来说，顺序写入比随机写入快得多。
</details>

(23) 解释一下预读失效和缓存污染。在MySQL(InnoDB)的buffer pool的设计中，是如何解决这两个问题的？

Tag: MySQL, Operating System

<details>
<summary>Answer: </summary>

预读失效即预读入的数据几乎没被用到，但却把一些热点数据挤出缓存。缓存污染即某些大范围扫描的命令一下子扫了很多数据进缓存，却几乎不会再次用到。MySQL中，将传统LRU队列划分为young和old两个区域，预读入的数据只会被塞到old区域中，而old区域中的数据必须再次被访问，并且与上次访问间隔1s(默认)，才能进入young区域。
</details>

(24) 解释一下有栈(stackful)和无栈(stackless) coroutine的区别

Tag: Operating System, Golang

<details>
<summary>Answer: </summary>

stackful coroutine会将整个当前的调用栈记录下来，好处是可以随时暂停，又方便调度，如go语言的goroutine就是采用的这种设计。stackless corouine只会记录局部变量为一个frame，不记录函数调用栈，好处是效率更高，内存占用少，坏处是coroutine无法在它调用的函数当中暂停，因为一旦暂停重新开始，他就不知道自己要回哪去了。但本身coroutine仍然可以调用(甚至递归)函数，因为运行的时候是借用主程序的调用栈的。采用这种设计的有C++20的coroutine，以及python的generator
</details>

(25) Python的generator采用了无栈协程(stackless coroutine)的设计，但为什么可以在调用的函数中暂停？

Tag: Operating System, Python

<details>
<summary>Answer: </summary>

实际上Python在遇到`yield from`关键字时会将多个frame串起来，对于用户来说，就好像stackful coroutine一样。
</details>

(26) 解释一下`sendfile`这个syscall的用途

Tag: Computer Networking, Operating System, Linux

<details>
<summary>Answer: </summary>

用于实现零拷贝。从磁盘读取到网卡发送，一般需要调用`read`将磁盘数据拷贝到kernel buffer，从kernel buffer拷贝到user buffer，再调用`write`从user buffer拷贝到socket buffer，最后从socket buffer拷贝给网卡。但sendfile可以直接从源FD复制到目标FD，如果网卡支持SG-DMA，还可以只将FD本身拷贝去socket，最终实现只有磁盘到kernel buffer到网卡，一共两次拷贝。
</details>

(27) Linux内核中用`struct sk_buff`结构体表示网络各个层的数据包。这个设计并没有遵循计算机网络各层分离的原则，为什么要这么做？

Tag: Computer Networking, Operating System, Linux

<details>
<summary>Answer: </summary>

为了提高效率。如果采用不同结构体，层与层之间传递数据就需要发生拷贝，但只使用一个结构体，我们可以通过调整`data`指针的形式来剥离或添加头部，当然，需要给头部预留足够的空间。
</details>

(28) Reference: [LeetCode 1963](https://leetcode.cn/problems/minimum-number-of-swaps-to-make-the-string-balanced/)

当满足以下条件时，字符串$s\in \Sigma^*$，$\Sigma = \{'[', ']'\}$被称为是平衡的。$\varepsilon$表示空字符串，$\cdot$表示字符串连接。$s$中的左括号和右括号数量相等。

* $s = \varepsilon$，字符串为空

* $s = s_l \cdot s_r$，且$s_l$和$s_r$都是平衡的(非空)

* $s = [s_0]$，且$s_0$是平衡的

证明，一个字符串$s\in\Sigma^*$当且仅当对任意$s[0:x]$，都有$[$ 的数量至少和 $]$一样多

Tag: Mathematics, Algorithm

<details>
<summary>Answer: </summary>

对字符串长度(用$l$表示长度函数)进行归纳法证明。我们先证明平衡字符串一定满足该性质。为空时显然；不为空时，如果
* $s = s_l\cdot s_r$，那么$l(s_l) < l(s)$, $l(s_r) < l(s)$，根据归纳假设，$s_l$和$s_r$都满足该性质，容易发现$s$也满足
* $s=[s_0]$，根据归纳假设，$s_0$满足该性质，$s$显然也满足，因为左括号加在最左边
而后证明满足该性质的字符串一定平衡。为空时显然；不为空时，那么我们知道，整个$s$中左括号数等于右括号数，故一定存在最早出现的右括号(位置记为$x$)，使得$s[0:x]$中左右括号数量相等。$s[0]$必为左括号。故我们可以将$s$划分为 $[s[1:x-1]]\cdot s[x+1:]$。根据归纳假设，两部分分别平衡，故$s$也平衡。
</details>

(29) 介绍一种算法，从$n$个样本点中抽取出$k$个，且每个样本点$i$被抽出的概率正比于其权重$w_i$，或等价地，$P(i)=\frac{kw_i}{\sum w_i}$

Tag: Mathematics, Algorithm

<details>
<summary>Answer: </summary>

我们使用类似线段树/树状数组的结构。原数组的元素在树的子节点。保证如下性质：`node.w = node.left.w + node.right.w`。至此预处理完成。而后我们只需每次随机一个$(0, \sum w_i]$的随机数，在树中查找，返回相应下标，更新置0即可
</details>

(31) 预测以下程序的输出

```cpp
#include <iostream>

struct A {
    void hi() {
        std::cout << "hi" << std::endl;
    }
};

int main() {
    A* a = nullptr;
    a->hi();
    return 0;
}
```

Tag: C++

<details>
<summary>Answer: </summary>

在编译器眼里，上述代码基本和`void hi(A* this)`一样。但该行为是UB，请勿在实际生产中使用！
</details>

(32) 以下Go代码有什么问题？

```go
type Cat struct{}
type Eat interface {
    eat()
}
func (c *Cat) eat() {
    fmt.Println("Cat is eating")
}
func DoEat[T Eat](animal *T) {
    animal.eat()
}

func main() {
    cat := &Cat{}
    DoEat(cat) 
```

Tag: Golang

<details>
<summary>Answer: </summary>

只有`*Cat`实现了`Eat`，因此`T`是`*Cat`，而animal的类型因此是`**Cat`，所以应该改成`*(animal).eat()`或`func DoEat[T Eat](animal T)`，后者中`animal`为`*Cat`
注释：鸽了几天，因为被一个leetcode题折磨了一整天，又休息了一天
</details>

(33) 有100本书，A和B轮流拿，A先拿，每人每次拿1到5本，A是否有必胜策略？

Tag: Critical Thinking

<details>
<summary>Answer: </summary>

我们发现，如果B拿了后A拿，不论B拿多少本，A都可以保证这一轮一共拿6本。我们希望最后剩下6本，然后B拿、A拿。所以开局给B只要是6的倍数就行。100本的话开局先拿掉四本即可。
</details>

(34) 如何实现一个互斥锁？

Tag: Operating System, Golang, Concurrency

<details>
<summary>Answer: </summary>

互斥锁本质上就是一个值为1的semaphore。我们这边讲述Go中的实现方式。`Mutex`结构体非常简单，就是一个semaphore加上一个int32的state，state中储存四个信息，锁定状态，正常模式被唤醒，饥饿状态，等待的goroutine个数。其中，等待的goroutine的`sudog`被串成队列，semaphore默认会FIFO唤醒。
锁定时，首先用CAS指令尝试快速直接锁定(如果目前没被锁则直接成功)，如果失败了，先判断是否能自旋。在饥饿模式下新来goroutine直接加入队列等着。而后就是在semaphore上等待了。
</details>

(35) Go语言中，`new`一个指针和用var创建一个变量后取地址有什么区别？

Tag: Golang

<details>
<summary>Answer: </summary>

没有区别。编译器眼里这俩是一样的。逃逸分析的时候如果发现这个指针逃逸了则自动分配到堆上。
</details>

(36) 简述TLS四次握手的过程

Tag: Computer Networking

<details>
<summary>Answer: </summary>

客户端发送Hello，告诉服务端自己支持的TLS版本、密码套件、以及生成的客户端随机数；服务端确认TLS版本和密码套件ok，发送给客户端自己的数字证书和生成的服务端随机数；客户端通过CA公钥验证证书，验证通过，向服务器发送一个随机数(这个随机数会被服务器的公钥加密，而前两个随机数是明文的)pre-master key、通知之后就用会话密钥来加密了、以及以上内容的hash供检验；最后，双方都可以通过三个随机数生成相同的会话密钥，服务器通知握手结束，完成整个流程。随机数的作用是防止replay attack，而生成这么多个，个人觉得是因为服务端不能相信客户端生成的足够随机，客户端反过来也是如此，因此双方只能信任自己生成的随机数，最好的方式自然是双方都生成。
</details>

(37) Go语言中的`sync.Map`是如何实现的？相比给`map`添加一个`sync.RWMutex`有什么区别？

Tag: Golong, Concurrency

<details>
<summary>Answer: </summary>

首先，`sync.Map`中的每个entry都是一个`atomic.Pointer`，指向实际的数据。而后，`sync.Map`维护了一个read-only的map以及一个dirty map。这两个map都把key map到`*entry`，即二级指针。read-only map有一个amended标记，记录是否有新的值在dirty map里。对read-only map的访问不需要加锁，而对dirty map的读写均需加锁。因此在读远大于写的情况下，`sync.Map`的性能会非常好。read-only map说是read-only，但其实只是不允许添加新的，其他的删改查任务都可以通过对指针的原子操作进行。
接下来来看一些细节。一个key被删除时首先被mark为deleted(`nil`)，一段时间内相同key被插入会直接复活；如果没有插入则mark为expunged(一个特殊的sentinel值)，此时在dirty map中会被直接删去，但read-only map中还不能删(因为无锁)
查找过程如下：如果read-only map里面有，那就直接返回。如果没有，看是不是amended，如果是，那就获取dirty map的锁，去dirty map里面找。每次去dirty map都会给miss加一，不管最后找没找到，miss太多说明这时候read-only map已经落后了，这时候直接把原来的dirty map promote成新的read-only map(这很简单，只需要进行一个指针的替换)，而后dirty map变成nil。而后，给dirty map上锁，把现在的read-only map再复制过来，复制的时候遇到nil和expunged都直接丢掉，在read-only map里设置为expunged。
</details>

(38) 什么是HOL(Head-of-Line)阻塞？HTTP3是如何解决这个问题的？

Tag: Computer Networking

<details>
<summary>Answer: </summary>

TCP是基于字节流的协议，它必须确保收到的数据完整且连续。如果我现在到了4个packet，第二个损坏了，那么第三第四个即使完整、即使和第二个不属于同一个stream，也必须等第二个packet重传完毕才能让应用层读取，在此之前只能在kernel buffer中暂存。而HTTP3基于QUIC，底层是UDP，自然不存在这个问题。
</details>

(39) 什么是单点登录(Single Sign On, SSO)？在现在，单点登录大多用什么实现？

Tag: Computer Networking

<details>
<summary>Answer: </summary>

单点登录，即依赖于一个单点进行用户身份的认证。例如，交大学生通过SSO登录飞书，在这个过程中，学生请求飞书的服务器，飞书的服务器返回让浏览器去找交大的服务器验证，浏览器照做，学生在交大的服务器上登录后(如果需要的话)，获取到一个token，而后学生的浏览器将这个token送回飞书服务器，这个token是签名过的，所以飞书服务器知道这是正版交大服务器验证过的用户，于是开始提供服务。目前SSO广泛地使用JWT(JSON web token)标准。
</details>

(40) 我们知道TCP的四次挥手中，接收到FIN的一方会回复ACK和FIN，那么为什么不将这两者合二为一，变成三次挥手呢？

Tag: Computer Networking

<details>
<summary>Answer: </summary>

接收到FIN后立刻回复ACK，而后会把EOF放到buffer最后，要等程序读到EOF才回复FIN。因此有时候确实会有三次挥手，即没有数据要发送且开启了TCP延迟确认机制。还有时候直接通过`close`粗暴关闭，则由内核回复RST，另一边的应用程序继续读就会产生`Connection reset by peer`错误。
</details>

(41) Go语言如何获取一个结构体的所有tag

Tag: Golang

<details>
<summary>Answer: </summary>

使用反射库`reflect`
</details>

(42) C#中，lambda的捕获规则是按值还是按引用？

Tag: CSharp

<details>
<summary>Answer: </summary>

默认全部按引用。即以下代码会全部print 3
```cs
var actions = new List<Action>();
for (int i = 0; i < 3; i++) {
  actions.Add(() => Console.WriteLine(i)); // All print 3
}
```
</details>

(43) 简述IO多路复用

Tag: Operating System, Golang, Computer Networking

<details>
<summary>Answer: </summary>

IO多路复用模型的思想是让一个进程维护多个socket，进行时分复用。Linux提供了三个有关多路复用的syscall，分别是select, poll, epoll。select和poll都是将需要监听的socket放入集合，每次直接遍历来检查是否有网络事件产生。而epoll是基于内核中维护的红黑树的，且是event based，一旦监测到有发生内核就调用callback，这样就不需要遍历了。
Go语言中提供select关键字用来同时监听多个channel，也是类似的。
</details>

(44) 预测以下代码的输出结果

```python
print(np.nan == np.nan)
print(np.nan is np.nan)
print(np.float32(np.nan) == np.float32(np.nan))
print(np.float32(np.nan) is np.float32(np.nan))
```

Tag: Python

<details>
<summary>Answer: </summary>

`False`, `True`, `False`, `False`。原因分别是
1. 在IEEE标准中，`nan`不等于任何值，包括自身。
2. `numpy`中`nan`是单例
3. 同1
4. 会创建新的instance，不再是单例
</details>

(45) 在Python中，`while True`和`while 1`在性能上有区别吗？

Tag: Python

<details>
<summary>Answer: </summary>

没有，可以通过`dis`查看字节码，会发现这两者生成的字节码完全一样
</details>

(46) C++中虚函数可以是静态(`static`)的吗？

Tag: C++

<details>
<summary>Answer: </summary>

不能。从设计理念上说，static意味着与具体是什么instance无关，只和class本身相关；而virtual恰恰相反，意味着完全取决于具体是什么instance，而不和class直接相关。
</details>

(47) 在一台物理内存为2G的Linux服务器上，一个进程尝试使用`malloc`分配10G的内存，可能会发生哪些情况？

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

与内核中memory overcommit(内核参数`overcommit_memory`)的设置有关。默认是启发式，即用某种算法判断是否合理，如果合理就允许overcommit。由于申请虚拟内存的过程中也会用一些物理内存，所以即使设置为全部允许，也会因为物理内存爆掉而无法一直申请。如果物理内存够的话，甚至可以直接申请满128T的虚拟内存。
</details>

(48) `malloc`如何分配内存？分配的内存一定在堆上吗？

Tag: Operating System, C

<details>
<summary>Answer: </summary>

实际上，`malloc`是一个glibc函数而不是syscall，这个函数封装了两种申请的方式：
* 对于较小(取决于版本，如128K)的内存，直接通过`brk`，向上调整堆指针而分配在堆上。
* 对于较大的内存，通过`mmap`的方式分配在文件和匿名映射区
可以通过`cat /proc/[pid]/maps`查看内存的分配详情。
</details>

(49) 现代CPU如何访问寄存器和缓存？通过物理地址还是虚拟地址？

Tag: Operating System

<details>
<summary>Answer: </summary>

寄存器没有地址，直接通过名称访问。缓存的话比较复杂，有三种方式
* 完全使用物理地址：坏处是查询前要先经过TLB，因为CPU访问内存用的是虚拟地址；好处是不会出现aliasing(即，同一块物理内存可能映射去不同虚拟内存)
* 完全使用虚拟地址：和前者正好相反
* Virtually indexed, physically tagged (VIPT)：也就是用虚拟地址做索引，但用物理地址做tag，综合了前两者的优点。大部分现代CPU的L1 cache都是这种方式。
</details>

(50) Context switch中的context包含哪些内容？

Tag: Operating System

<details>
<summary>Answer: </summary>

包含寄存器、内存管理状态(TLB会被清空，然后使用另一个process的page table)、OS管理的调度信息等。三级缓存不会被清空，但会出现缓存污染。branch predictor的状态、网络状态都不属于context。
</details>

(51) 除了syscall，还有哪些方式跨越用户态和内核态的边界？

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

和syscall对应的是`upcall`，允许内核去反过来通知用户进程。此外signal、interrupt、exceptions都会从用户态自动跨越到内核态去处理。
</details>

(52) C++的虚表存放在内存的什么地方？

Tag: C++

<details>
<summary>Answer: </summary>

一般来说放在数据段(即和初始化完毕的全局变量在一起)，但C++标准并没有进行指定，因此放哪取决于具体的编译器实现。
</details>

(53) 在内存不足时，OS对文件页和匿名页分别可能采取什么操作？

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

文件页也就是数据来源于磁盘中文件的页面，进行文件读取时内核会把数据缓存在page cache中。要回收内存也很简单，如果不是脏页就直接回收，如果是的话就先写回。
匿名页，比如堆内存，没有文件作为数据来源。要回收只能先放回磁盘，即swap分区或swap file，swap出后再回收。`swappiness`参数表示swap的积极程度。
</details>

(54) 设置内核参数`swappiness=0`相当于`swapoff -a`，即会完全关闭swap。这个说法对吗？

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

错误。`swappiness`实际上是指示内核回收匿名页的积极程度，根据官方doc:
> A value of 0 instructs the kernel not to initiate swap until the amount of free and file-backed pages is less than the high water mark in a zone.
当内存紧张且没有文件页能回收时，仍然会swap。"内存紧张"的具体定义由水位参数(watermark)给出，水位参数由内核参数`/proc/sys/vm/min_free_kbytes`计算出。
</details>

(55) 简单说说从`printf("Hello world")`到输出到console的过程。

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

首先，`printf`是libc中的实现的标准库函数，通过`strace`我们可以看到，其本质上就是调用`write`这个syscall把字符串写入标准输出(fd=1)。
那么fd=1的标准输出流是如何和console相关联的？我们先可以通过以下方式查看当前console是啥
```bash
$ sleep 10000 &
$ lsof -c sleep # 列出打开的文件，命令以sleep开头
```
在我的服务器上，可以发现console为`/dev/pts/0`。而将fd=1绑定到console的过程发生在init进程中的`console_init()`。
`write`这个syscall首先将数据复制到kernel space。而后，`console_fops`中的`.open`为`tty_open`，`.write`为`redirected_tty_write`。来到tty层后，还需要再向下到达UART硬件层，最终完成整个过程。
</details>

(56) 简述CAS(compare and swap)指令

Tag: Operating System

<details>
<summary>Answer: </summary>

CAS是一个原子操作，相当于原子地执行以下操作
```c
int cas(int* reg, int old, int new) {
    int old_reg = *reg;
    if (old_reg == old)
        *reg = new;
    return old_reg;
}
```
在C11(gcc/clang)下，`stdatomic.h`库中，有`__atomic_compare_exchange`可以使用
</details>

(57) 什么是NUMA架构？

Tag: Operating System, Computer Organization

<details>
<summary>Answer: </summary>

NUMA(non uniform memory access)，即多核服务器上，每个CPU核心拥有一个节点的内存，访问自己节点的内存不需要经过总线。内存不足时再去找别的节点要。CPU之间通过QPI(Intel QuickPath Interconnect)互联。与之相对应的是UMA，即所有CPU都在总线一侧，内存在另一侧，所有访问都需要经过总线。
</details>

(58) 进程A正在写入一个文件，此时如果进程崩溃了，写入的数据会丢失吗？如果OS宕机了(如直接断电)，数据会丢失吗？

Tag: Operating System, Linux

<details>
<summary>Answer: </summary>

写入文件实际上是在写入OS的page cache(如果不手动调用`fsync`的话)。因此，进程崩溃不会丢失，page cache由os管理。OS宕机，如果写入的是page cache则会丢失，如果用`fsync`直接写入磁盘则不会。
</details>

(59) 异步IO和非阻塞IO的区别是什么？

Tag: Operating System

<details>
<summary>Answer: </summary>

IO有两个过程可能阻塞，一是用户程序调用read这个syscall，而内核还没准备好；二是内核已经准备好了，但还没复制到user space。非阻塞IO是在一不发生阻塞，异步IO是一和二都不会阻塞。
</details>

(60) 证明以下排序算法的正确性

```python
for i in range(1, n):
    for j in range(1, n):
        if a[i] < a[j]:
            swap(a[i], a[j])
```

Tag: Algorithm

<details>
<summary>Answer: </summary>

Reference: https://arxiv.org/pdf/2110.01111
实际上这就是个代码更简洁，但更加耗时的插入排序。可以归纳法证明，在最后一次遍历前，每次遍历会把最大值放到最前面。
</details>

(61) 写一行vim指令在接下来的10行中完成以下替换

```python
d = {
    11: 2,
    23: 3, 
    55: 7, 
    ...
}
```

替换为

```python
d = {
    (11, 11, 11): 2,
    (23, 23, 23): 3, 
    (55, 55, 55): 7, 
    ...
}
```

Tag: Vim

<details>
<summary>Answer: </summary>

`:.,+10s/\(\d\+\):/(\1, \1, \1):/g`。注意，使用vscode的vim插件时部分字符不需要escape: `:.,+10s/(\d+):/\(\1, \1, \1):/g`即可(相当于开启了`\v`)。
</details>

(62) 以下代码可以正确运行吗？

```python
arr = np.zeros((50, 50), dtype=np.int32)
arr[arr > 0] = arr + 2
```

Tag: Python

<details>
<summary>Answer: </summary>

不能，实际上`arr[mask]`(mask是大小相同的boolean numpy array)返回的是一个一维的数组。改成`arr[arr > 0] += 2`，就可以运行了。
</details>

(63) 数据库应当如何安全储存用户密钥？

Tag: Cryptography, Cyber Security

<details>
<summary>Answer: </summary>

使用例如`bcrypt`之类的更安全的哈希而非朴素哈希算法如`sha256`。这是因为朴素哈希算法计算速度快，容易受到彩虹表攻击，相同密码会产生相同的哈希。而`bcrypt`自带salting，计算缓慢，更加安全。即使数据库发生泄漏，也能保障攻击者无法轻易从哈希值获取到用户密钥。
</details>

(64) 为什么MySQL没有scan sharing的feature?

Tag: Database, MySQL

<details>
<summary>Answer: </summary>

Scan sharing一般用在需要大量全表扫描的情景下，即OLAP(Online Analytical Processing)，而MySQL(InnoDB)的主要应用场景为OLTP(Online Transaction Processing)，注重的是并行处理小型的、快速的query的效率。在MySQL中出现全表扫描是很不正常的事情，毕竟一个大的表，比如千万量级，你再优化也一样很慢，不应该出现在注重实时性的线应用中。当然，可能还存在一些架构上的原因，或者实现的难点。
</details>