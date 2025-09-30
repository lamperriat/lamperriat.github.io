---
title: CRT与Lucas定理(Leetcode 2221)
date: 2025-09-30 16:49:37
categories:
  - math
  - algorithm
---

[题目链接](https://leetcode.cn/problems/find-triangular-sum-of-an-array)

我们不难发现这个题目的背景其实是一个倒着的杨辉三角，因此等价地我们希望求的是
$$
\sum \text{nums}[i] * \begin{pmatrix}
  n \\ i
\end{pmatrix}\mod 10
$$

其中$n$是`nums.size - 1`。

我们知道组合数可以写成递推的形式
$$
\begin{pmatrix}
  n \\ m
\end{pmatrix} = \frac{n-m+1}{m} \begin{pmatrix}
  n \\ m-1
\end{pmatrix}
$$

但是存在一个问题啊，直接求值以组合数的数量级肯定是扛不住的，但除以$m$这个操作，因为10不是质数，并不能直接写成乘以$m$的inverse。(哪怕可以我们也需要处理$10\mid m$的情况)。

那么有没有比较方便处理组合数取模的工具呢？那自然是有的，于是引出Lucas定理

**Theorem**(Lucas's Theorem)
对于非负的$m, n$和质数$p$，
$$
\begin{pmatrix}
  n \\ m
\end{pmatrix} = \prod_{i=0}^k \begin{pmatrix}
  n_i \\ m_i
\end{pmatrix} \mod p
$$

其中
$$
m = \sum_{i=0}^k {m_i}p^i, \quad n = \sum_{i=0}^k {n_i}p^i
$$

以上记号使用$\begin{pmatrix}
  n \\ m
\end{pmatrix}$在$n < m$时等于0的约定。

**Proof**: 证明并不是很困难，直接上生成函数

首先注意到
$$
(1+X)^{p^i} = 1+X^{p^i} \mod p
$$

因为$p\mid \begin{pmatrix} p^i n\end{pmatrix}$. 而后

$$
\begin{aligned}
\sum_{m} \begin{pmatrix} n\\ m\end{pmatrix} X^m &= (1+X)^n \\
&= (1+X)^{\sum n_i p^i} \\
&= \prod_{i=0}^k (1+X)^{n_i p^i} \\
&= \prod_{i=0}^k (1+X^{p^i})^{n_i} \\
&= \prod_{i=0}^k \sum_{s_i = 0}^{n_i} \begin{pmatrix} n_i \\ s+i\end{pmatrix} X^{s_i}p^i \\
&= \prod_{i=0}^k \sum_{m_i = 0}^{p-1} \begin{pmatrix} n_i \\ m_i\end{pmatrix} X^{m_i}p^i \\
&\stackrel{?}{=} \sum_{m=0}^n X^m\prod_{i=0}^k \begin{pmatrix} n_i\\ m_i\end{pmatrix}  
\end{aligned}
$$

我想除了最后一步以外应该都非常清晰。最后一步实际上也非常简单，我们可以把左侧展开，因为每一项求和相互独立，我们可以把所有求和拿到最左边
$$
\sum_{m_0=0}^{p-1} \sum_{m_1=0}^{p-1} \cdots \sum_{m_k=0}^{p-1} 
\prod_{i=0}^k \binom{n_i}{m_i} 
\; X^{\sum_{i=0}^k m_i p^i}
$$

这下是不是清楚多了？左边一大坨求和其实和右边对$m$求和是一样的。

---
由此我们可以回到我们的算法了。我们用CRT(Chinese Remainder Theorem)将10拆成$2\times 5$，然后应用Lucas定理分别计算组合数模2和5的值，得到以下代码

```cpp
class Solution {
public:
    inline int combMod2(int n, int m) {
        return (int)((n & m) == m);
    }

    int combMod5(int n, int m) {
        constexpr int fact5[5] = {1,1,2,1,4}; // 0! ~4!
        constexpr int inv5[5] = {0,1,3,2,4};
        int res = 1;
        while (n > 0) {
            int ni = n % 5;
            int mi = m % 5;
            if (mi > ni) {
                return 0; 
            }
            res = (res * fact5[ni] * inv5[fact5[mi]] * inv5[fact5[ni-mi]]) % 5;
            n /= 5;
            m /= 5;
        }
        return res;
    }

    int triangularSum(vector<int>& nums) {
        int n = nums.size() - 1;
        int sumM2 = 0;
        int sumM5 = 0;
        for (int i = 0; i <= n; i++) {
            sumM2 = (sumM2 + combMod2(n,i) * nums[i]) % 2;
            sumM5 = (sumM5 + combMod5(n,i) * nums[i]) % 5;
        }
        cout << sumM2 << " " << sumM5 << endl;
        return sumM5 % 2 == sumM2 ? sumM5 : sumM5 + 5;
    }
};
```

提交，直接0ms，击败100%! 