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