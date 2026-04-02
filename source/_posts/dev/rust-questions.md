---
title: Learn Rust by Questions
date: 2026-03-18 12:23:22
tags:
  - dev
  - rust
---

在AI的时代，提出合适的问题有时候比解决问题更重要。

### 基础
Rust中的borrow对应C/C++中的什么概念?Rust中对应pointer to const和const pointer的分别是什么?

什么是internal mutability?什么时候我们会用到`xxxCell`一类的类型?

Rust中定义一个新的变量`let new_val = val;`这个statement，是否可以被认为实际上是让编译器知道这块数据有了一个名字`new_val`而原来的名字`val`不能再使用?语义上也是如此吗?

一个类型是否`Copy` trait，在进行`let new_val = val;`的时候，本质上的区别是什么?

如何创建一个指向堆上某个数据的borrow?

下面这段代码可以通过编译吗?这说明了Rust中的什么设计?
```rust
struct Wrapper {
    v: i32, 
}

fn main() {
    let w = Wrapper{v:10};
    println!("{}", w.v);
    
}
```

Trait的Associated types和Generic parameters的区别是什么?如何决定应该使用哪个?

如何在Rust中实现类似method overload的效果?


### 内存管理
Rust的默认内存管理是怎么样的?每次内存分配都会直接调用os的内存分配吗?还是会有runtime管理一个类似内存池的结构?内存管理的逻辑是否可以自定义?

### 多线程
Rust中的`MutexGuard`是`!Send`的?为什么?

如何减少切换os线程带来的性能损失?在computing-bound和io-bound的任务中分别如何解决?

channel本质上是一块有编译器保障的，每个线程都可以读写的内存，这个说法对吗?

### 并发
async runtime在async/await的异步编程中扮演了什么角色?

Rust中的`pin`有什么作用?为什么在async/await的异步编程中经常会使用到`pin`?

Rust中的async/await在底层是有栈的还是无栈的?带来的影响是什么?

Tokio如何处理channel中，一方关闭channel的情景的?channel的内存在什么情况下才会被free?

`Box::pin`是如何办到把一个在栈上的future搬到堆上去的?如果这个future对应的状态机中有self-referencing的结构会怎么样?

在async rust中，Task和future的关系是什么?