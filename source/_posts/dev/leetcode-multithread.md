---
title: Leetcode多线程题解(更新中)
date: 2025-09-04 20:38:20
categories: 
    - dev
    - notes
---

最近发现Leetcode加了多线程的板块，虽然没几个题，不过正好拿来练习一下。以下包含题解，还没做的话请自行决定是否阅读。


### 1114.按序打印
题干: 
```java
public class Foo {
  public void first() { print("first"); }
  public void second() { print("second"); }
  public void third() { print("third"); }
}
```
三个不同的线程 A、B、C 将会共用一个 Foo 实例。要求按序打印。

一看，很简单啊，直接搞两个`atomic<bool>`让线程自旋等着就行。
```cpp
class Foo {
    std::atomic<bool> first_done;
    std::atomic<bool> second_done;
public:
    Foo() {
        first_done = false;
        second_done = false;
    }

    void first(std::function<void()> printFirst) {
        printFirst();
        first_done.store(true, std::memory_order_release);
    }

    void second(std::function<void()> printSecond) {
        while (!first_done.load(std::memory_order_acquire)) {}
        printSecond();
        second_done.store(true, std::memory_order_release);
    }

    void third(std::function<void()> printThird) {
        while (!second_done.load(std::memory_order_acquire)) {}
        printThird();
    }
};
```
一提交，好家伙1400ms，击败5%。看了眼题解用的是semaphore。仔细一想就明白了，实际上leetcode给的是**单核**的环境。用`atomic<bool>`相当于自旋。后两个线程都在自旋但一共只有一个cpu，这不肯定完蛋了。在我本机上一测果然如此啊，多核($\geq 3$)下两种实现其实效率差距不大的，单核下得差好多。

不过还有个小发现，即使核心数=线程数，用自旋还是比semaphore要慢，猜测是和缓存有关。请教了gemini老师，说是另外两个的核心会把这块内存fetch到自己的cache，但thread 1写入后缓存就失效了，还得重新fetch一遍。而如果用semaphore会减缓缓存不一致的问题。直接测试一下，用`taskset`绑定到单核运行发现比用多核更快了，还真是这样。不过gemini说context switch和cache coherency带来的开销区别不是确定的，可能换个机器结果就不同了。

于是最终题解如下
```cpp
class Foo {
    std::binary_semaphore sem1;
    std::binary_semaphore sem2;

public:
    Foo() : sem1(0), sem2(0) {}

    void first(std::function<void()> printFirst) {
        printFirst();
        sem1.release();
    }

    void second(std::function<void()> printSecond) {
        sem1.acquire();
        printSecond();
        sem2.release();
    }

    void third(std::function<void()> printThird) {
        sem2.acquire();
        printThird();
    }
};
```


### 1115.交替打印
题干:
给你一个类：

```java
class FooBar {
  public void foo() {
    for (int i = 0; i < n; i++) {
      print("foo");
    }
  }

  public void bar() {
    for (int i = 0; i < n; i++) {
      print("bar");
    }
  }
}
```

两个不同的线程将会共用一个 FooBar 实例：

线程 A 将会调用 foo() 方法，而
线程 B 将会调用 bar() 方法
请设计修改程序，以确保 "foobar" 被输出 n 次。

这个题很简单，没什么说法，直接上代码
```cpp
class FooBar {
private:
    int n;
    std::binary_semaphore foo_done;
    std::binary_semaphore bar_done;
public:
    FooBar(int n) : foo_done(0), bar_done(1) {
        this->n = n;
    }

    void foo(function<void()> printFoo) {
        for (int i = 0; i < n; i++) {
            bar_done.acquire();
        	printFoo();
            foo_done.release();
        }
    }

    void bar(function<void()> printBar) {
        for (int i = 0; i < n; i++) {
            foo_done.acquire();
        	printBar();
            bar_done.release();
        }
    }
};
```

当然，Go语言的channel非常适合这个场景
```go
type FooBar struct {
	n int
    fooDone chan struct{}
    barDone chan struct{}
}

func NewFooBar(n int) *FooBar {
	fb := &FooBar{
        n: n,
        fooDone: make(chan struct{}, 1),
        barDone: make(chan struct{}, 1),
    }
    fb.barDone <- struct{}{}
    return fb
}

func (fb *FooBar) Foo(printFoo func()) {
	for i := 0; i < fb.n; i++ {
        <-fb.barDone
        printFoo()
        fb.fooDone <- struct{}{}
	}
}

func (fb *FooBar) Bar(printBar func()) {
	for i := 0; i < fb.n; i++ {
		<-fb.fooDone
        printBar()
        fb.barDone <- struct{}{}
	}
}
```

### 1116.打印零与奇偶数
题干:
三个线程
* 线程 A：调用 `zero()` ，只输出 0
* 线程 B：调用 `even()` ，只输出偶数
* 线程 C：调用 `odd()` ，只输出奇数

打印出`0102...0n`序列。

这个题也很简单，`zero`根据迭代次数通知`odd`或`even`打印，然后`odd`/`even`回头再通知zero即可
```cpp
class ZeroEvenOdd {
private:
    int n;
    std::binary_semaphore zeroReady;
    std::binary_semaphore evenReady;
    std::binary_semaphore oddReady;

public:
    ZeroEvenOdd(int n) : zeroReady(1), evenReady(0), oddReady(0) {
        this->n = n;
    }

    void zero(function<void(int)> printNumber) {
        for (int i = 0; i < n; i++) {
            zeroReady.acquire();
            printNumber(0);
            if (i % 2 == 1) {
                evenReady.release();
            } else {
                oddReady.release();
            }
        }
    }

    void even(function<void(int)> printNumber) {
        for (int turn = 2; turn <= n; turn += 2) {
            evenReady.acquire();
            printNumber(turn);
            zeroReady.release();
        }
    }

    void odd(function<void(int)> printNumber) {
        for (int turn = 1; turn <= n; turn += 2){
            oddReady.acquire();
            printNumber(turn);
            zeroReady.release();   
        }
    }
};
```

#### 1117.H2O生成
题干: (个人觉得本题题干表述不清)
现在有两种线程，氧 `oxygen` 和氢 `hydrogen` ，你的目标是组织这两种线程来产生水分子。

存在一个屏障（barrier）使得每个线程必须等候直到一个完整水分子能够被产生出来。

氢和氧线程会被分别给予 `releaseHydrogen` 和 `releaseOxygen` 方法来允许它们突破屏障。

这些线程应该三三成组突破屏障并能立即组合产生一个水分子。

你必须保证产生一个水分子所需线程的结合必须发生在下一个水分子产生之前。

换句话说:
* 如果一个氧线程到达屏障时没有氢线程到达，它必须等候直到两个氢线程到达。
* 如果一个氢线程到达屏障时没有其它线程到达，它必须等候直到一个氧线程和另一个氢线程到达。

---

我一开始以为会这样调用
```cpp
H2O h;
int n = 10;
std::thread t1([&h, n]() {
    for (int i = 0; i < n; i++)
        h.hydrogen([]() { printf("H"); });
});
std::thread t2([&h, n]() {
    for (int i = 0; i < n; i++)
        h.hydrogen([]() { printf("H"); });
});
std::thread t3([&h, n]() {
    for (int i = 0; i < n; i++)
        h.hydrogen([]() { printf("O"); });
});

t1.join();
t2.join();
t3.join();
```

那题目都说barrier了，那就直接用`std::barrier`
```cpp
class H2O {
    std::barrier<> ready;
public:
    H2O() : ready(3) {}

    void hydrogen(std::function<void()> releaseHydrogen) {
        releaseHydrogen();
        ready.arrive_and_wait();
    }

    void oxygen(std::function<void()> releaseOxygen) {
        releaseOxygen();
        ready.arrive_and_wait();
    }
};
```

然后就WA了，显然leetcode并不是如我想的那样开三个线程...(本机跑了下代码本身是没问题的)

那就还是用semaphore吧，也很简单，hydrogen调用用一个`std::atomic_int`计数，到2的时候通知oxygen。不过这个很显然不是最优解，实际上即使hydrogen还没ready也不影响oxygen

```cpp
class H2O {
    std::counting_semaphore<3> hReady;
    std::atomic_int hReadyCnt;
    std::binary_semaphore oReady;
public:
    H2O() : hReady(2), oReady(0), hReadyCnt(0) {}

    void hydrogen(std::function<void()> releaseHydrogen) {
        hReady.acquire();
        hReadyCnt++;
        releaseHydrogen();
        if (hReadyCnt == 2) {
            oReady.release();
            hReadyCnt = 0;
        }
    }

    void oxygen(std::function<void()> releaseOxygen) {
        oReady.acquire();
        releaseOxygen();
        hReady.release(2);
    }
};
```

不过由于不知道leetcode到底怎么调用的，暂时就不再优化了，就这样吧~

#### 1195.交替打印字符串
实现一个有四个线程的多线程版  `FizzBuzz，` 同一个 `FizzBuzz` 实例会被如下四个线程使用：

* 线程A将调用 `fizz()` 来判断是否能被 3 整除，如果可以，则输出 `fizz`。
* 线程B将调用 `buzz()` 来判断是否能被 5 整除，如果可以，则输出 `buzz`。
* 线程C将调用 `fizzbuzz()` 来判断是否同时能被 3 和 5 整除，如果可以，则输出 `fizzbuzz`。
* 线程D将调用 `number()` 来实现输出既不能被 3 整除也不能被 5 整除的数字。

---

其实就是把函数调的过程改成A线程semaphore，B线程acquire而已，这样就很容易理解了
```cpp
class FizzBuzz {
private:
    int n;
    std::binary_semaphore canDoFizz;
    std::binary_semaphore canDoBuzz;
    std::binary_semaphore canDoFizzBuzz;
    std::binary_semaphore done;

    int fizzCount;
    int buzzCount;
    int fizzBuzzCount;
public:
    FizzBuzz(int n) : canDoBuzz(0), canDoFizz(0), canDoFizzBuzz(0), done(0) {
        this->n = n;
        fizzCount = (n / 15) * 4 + (n % 15) / 3;
        buzzCount = (n / 15) * 2 + (n % 15) / 5;
        fizzBuzzCount = n / 15;
    }

    // printFizz() outputs "fizz".
    void fizz(function<void()> printFizz) {
        for (int i = 0; i < fizzCount; i++) {
            canDoFizz.acquire();
            printFizz();
            done.release();
        }
    }

    // printBuzz() outputs "buzz".
    void buzz(function<void()> printBuzz) {
        for (int i = 0; i < buzzCount; i++) {
            canDoBuzz.acquire();
            printBuzz();
            done.release();
        }
    }

    // printFizzBuzz() outputs "fizzbuzz".
	void fizzbuzz(function<void()> printFizzBuzz) {
        for (int i = 0; i < fizzBuzzCount; i++) {
            canDoFizzBuzz.acquire();
            printFizzBuzz();
            done.release();
        }
    }

    // printNumber(x) outputs "x", where x is an integer.
    void number(function<void(int)> printNumber) {
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) {
                canDoFizzBuzz.release();
                done.acquire();
            } else if (i % 3 == 0) {
                canDoFizz.release();
                done.acquire();
            } else if (i % 5 == 0) {
                canDoBuzz.release();
                done.acquire();
            } else {
                printNumber(i);
            }
        }
    }
};
```
