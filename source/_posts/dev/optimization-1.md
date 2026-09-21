---
title: Compiler Optimization Case Study
date: 2026-09-21 14:21:50
categories:
- dev
- optimization
---

今天照常做leetcode (3524)的时候，我写下了这样的实现:
```rs
pub fn result_array(nums: Vec<i32>, k: i32) -> Vec<i64> {
    let k = k as usize;
    let mut acc = vec![0i64; k];
    let mut prev = vec![0i64; k];
    let mut cur = vec![0i64; k];
    for v in nums.iter().rev() {
        let v = *v as usize;
        for i in 0..k {
            cur[i * v % k] += prev[i];
        }
        cur[v % k] += 1;
        for i in 0..k {
            prev[i] = cur[i];
            acc[i] += cur[i];
            cur[i] = 0;
        }
    }
    acc
}
```

非常简单，对吧。然后我在好奇一个事情，如果我们把`cur`的定义移动到loop的内部，编译器是否能看出来实际上可以reuse `cur`而不需要每次都重新分配这件事呢？

我们在compiler explorer上研究一下。首先找到我们的loop的起始点，我发现compiler explorer对rust的支持并没有C++那么好，因此有些指令会对应不上，只能手动看。
先来看把`cur`的定义移动到loop内的情况:
```asm
.LBB0_42: ; loop的起始
        mov     edx, 8
        lea     rsi, [8*r15]
        call    qword ptr [rip + __rustc[4b1ee1ef74718a7b]::__rust_dealloc@GOTPCREL]
        mov     rax, qword ptr [rsp + 40]
        cmp     qword ptr [rsp + 32], rax
        je      .LBB0_43
.LBB0_17:
        test    ebp, ebp
        je      .LBB0_23
        call    qword ptr [rip + __rustc[4b1ee1ef74718a7b]::__rust_no_alloc_shim_is_unstable_v2@GOTPCREL]
        mov     esi, 8
        lea     rdi, [8*r15]
        call    qword ptr [rip + __rustc[4b1ee1ef74718a7b]::__rust_alloc_zeroed@GOTPCREL]
        test    rax, rax
        je      .LBB0_19
        mov     rdi, rax
        mov     rax, qword ptr [rsp + 40]
        add     rax, -4
        mov     qword ptr [rsp + 40], rax
        movsxd  rcx, dword ptr [rax] ; 这里是 let v = *v as usize
```

然后是放在loop外的情况
```asm
.LBB0_25:
        add     r14, -4
        cmp     r9, r14
        je      .LBB0_19
.LBB0_26:
        test    ebp, ebp
        je      .LBB0_30
        movsxd  rcx, dword ptr [r14 - 4]
```
这样看就很明显了，编译器并不能自动把allocation移动到外面。因此手动把临时的堆变量移动到loop外来复用的确可以减少allocation。

然后我们来看一下最后这个loop。我的写法就是典型的cstyle index-based loop，还有一种使用iterator的写法，即
```rs
for ((p, a), c) in prev
    .iter_mut()
    .zip(acc.iter_mut())
    .zip(cur.iter_mut())
{
    *p = *c;
    *a += *c;
    *c = 0;
}
```

这两者语义上显然是等价的。但用`zip`隐含了"等长度"这一信息，对编译器也许有一些hint的作用。不过实际发现，两者生成的assembly是一样的。看起来编译器的优化还是相当强大的。
编译结果：
```asm
.LBB0_43:
        movdqu  xmm1, xmmword ptr [rdi + 8*rax]
        movdqu  xmm2, xmmword ptr [rdi + 8*rax + 16]
        movdqu  xmmword ptr [r13 + 8*rax], xmm1
        movdqu  xmmword ptr [r13 + 8*rax + 16], xmm2
        movdqu  xmm3, xmmword ptr [r12 + 8*rax]
        movdqu  xmm4, xmmword ptr [r12 + 8*rax + 16]
        paddq   xmm3, xmm1
        paddq   xmm4, xmm2
        movdqu  xmmword ptr [r12 + 8*rax], xmm3
        movdqu  xmmword ptr [r12 + 8*rax + 16], xmm4
        movups  xmmword ptr [rdi + 8*rax], xmm0
        movups  xmmword ptr [rdi + 8*rax + 16], xmm0
        add     rax, 4
        cmp     r10, rax
        jne     .LBB0_43
        mov     rax, r10
        cmp     rbx, r10
        je      .LBB0_25
.LBB0_45:
        mov     rcx, rax
        or      rcx, 1
        test    bl, 1
        je      .LBB0_47
        mov     rdx, qword ptr [rdi + 8*rax]
        mov     qword ptr [r13 + 8*rax], rdx
        add     qword ptr [r12 + 8*rax], rdx
        mov     qword ptr [rdi + 8*rax], 0
        mov     rax, rcx
.LBB0_47:
        cmp     rbx, rcx
        je      .LBB0_25
.LBB0_48:
        mov     rcx, qword ptr [rdi + 8*rax]
        mov     qword ptr [r13 + 8*rax], rcx
        add     qword ptr [r12 + 8*rax], rcx
        mov     qword ptr [rdi + 8*rax], 0
        mov     rcx, qword ptr [rdi + 8*rax + 8]
        mov     qword ptr [r13 + 8*rax + 8], rcx
        add     qword ptr [r12 + 8*rax + 8], rcx
        mov     qword ptr [rdi + 8*rax + 8], 0
        add     rax, 2
        cmp     rbx, rax
        jne     .LBB0_48
        jmp     .LBB0_25
```

这里，第一部分是simd，第二步是是手动的unrolling处理剩下的元素。