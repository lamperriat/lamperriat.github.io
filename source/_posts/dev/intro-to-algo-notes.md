---
title: 'Notes: Introduction to Algorithms (English)'
date: 2025-08-30 11:34:08
categories: 
    - dev
    - notes
---

*本篇为课程笔记，仅供参考*

# Basics on Algo

heuristic: idea serving as a guide

Hard to solve prob

* approximation algo
* knowing extra info
* once-and-for-all

IO expressed in a simple, clear way with terms.

Traversals:

* pre order: create a tree
* post order: delete a tree
* in order: BST as a sorted array

Hash: prime $p$ should not be close to 2's powers. 

Proof of an algo: correctness and complexity.

Kruskal's Algorithm
Proof of correctness: see notes of mit6.402

Union Find:
idea: what matters is whether they are connected instead of how they are connected. 

Problem: counting inversions

Solution: divide-and-conquer. Based on merge sort.

# Complexity Theory

Random Access Machine (RAM) model:

* each simple operation takes one step
* loops are composed of several simple steps, repeated a certain number of times
* each memory access takes one step

Runtime: total number of steps.
worst, best, average complexity for fixed input size. 
The complexity is defined by a numerical function. 

# C2

## Complexity of Union-Find

Lemmas:

* A root node attached to another root will never be a root again
* A non-root node has fixed rank
* A node with rank $k$ has at least $2^k$ nodes in its subtree. (proof by induction, $f(k) \geq 2f(k-1)$, which is the case of union two trees of the same rank)
* Over $n$ elements there at at most $n/2^k$.

Def: *iterated logarithm* function, $\log^*$.
$$\begin{align*}
\log^*: &\mathbb R \to \mathbb N \\
x&\mapsto \begin{cases}
    0 \text{if}\ x\leq 1 \\
    1 + \log^* {\log}_2 x  \\
\end{cases}
\end{align*}$$

$m$ find operations cost $\mathcal{O}((m+n){\log}^{*}n)$.
Idea: Devide into blocks

Ackerman's func:

* one of the simplest *total computable* function that is not *primitive recursive*.
* total computable: can be computed with any input without approximation.
* not primitive recursive: cannot be done with a for loop (i.e. predictable iterations). Cannot do better than recursion.

Inverse Ackermann's func: $\alpha(x)$ is the inverse of $A(n,n)$.

Theorem: the amortized time for a sequence of $m$ operations in Union-Find can be performed in $\mathcal{O}(m\alpha(n))$

## Complexity Theory

Taxonomy of problems

* decision
* search
* counting
* optimization
* function

Turin machine. Elementary op

* replace with a symbol
* move l/r
* update state

A turing machine is exactly
$$M: (\Sigma \cup \{b\} )\times Q \rightarrow (\Sigma \cup \{b\}) \times \{-1,0,1\} \times Q $$

Deterministic computations

* initial state $q_{0}$
* finite fixed sequence of elementary operations

A function $f: \Sigma^* \to \Sigma^* $ is Turing computable if there exists a Turing machine $M$ which returns $f(x)$ for any input $x$.

A programming language is Turing-complete if it can be used to implement a Turing machine. weird examples: `sed`, `awk`, `css`, `latex`

RAM equivalent to Turing machine.
PRAM: Parallel RAM

Definition of time complexity: Given an input $x$ for a Turing machine $M$, the number of operations is $t_{M}(x)$. 
$$ T_{M} : x\mapsto \max_{|x|} t_{M}(x)$$

$|x|$ is the length of $x$. 

If $T$ Turing computable, $M$ be the Turing machine, there exists a polynomial $P$ s.t.
$$T_{M}(x) \leq P(x)$$

then $M$ is a deterministic polynomial algorithm.

$f: \Sigma^{*} \to \{0, 1\}$ be a Turing computable function, and $L = f^{-1}(1) $. $L$ is called a *language* and $f$ defines a decision problem $P$. One says the Turing machine computes $f$, solves $P$, or decides $L$. 

Definitions:

* $\mathcal P$: all the decision problems that can be solved by a deterministic polynomial algorithm.

* A decision problem $\Pi$ is computable by a non-deterministic polynomial algo iff there exists $M$ and poly $P$ s.t.
  
  * $x\in L(\Pi) $ iff there exists $y\in\Sigma^* $, such that $M$ computes 1 when it has input $x$ in 1 through $|x|$ and $y$ in -1 through $-y$. $y$ is kind of like a "hint". 
  * For all $x$ s.t. $f(x) = 1$. There exists $y$ s.t. $M$ computes 1 in time $P(|x|)$. 
  * The class of all such problems are defined as $\mathcal N \mathcal P$. All the decision problems that can be solved fast with a hint.

* co-$\mathcal N\mathcal P$: Same as $\mathcal N \mathcal P$, but has `False` as the answer. (NP has `True` as the answer.)

* $P_{1}$ can b e reduced in polynomial time to $P_{2}$, if there exists $f$ (in poly time), $x\in L(P_{1})$ iff $f(x)\in L(P_{2})$. Say, discrete log and ecdlp 

* A problem $\Pi$ is $\mathcal N\mathcal P$-hard iff for all $P$ in $\mathcal N\mathcal P$, $P$ can be reduced in polynomial time to $\Pi$. 

$P_{1} \ltimes P_{2}$: $P_{1}$ can be reduced in poly time to $P_{2}$. 

! If $P_{1}$ is harder, then $P_{1}$ can be easily transform into an easier problem, so it should be easy.
An easy problem can be easily made hard, but not the other way around.

$\Pi$ is NP hard iff for all $P$ in $\mathcal N\mathcal P$, $P$ can be reduced in poly time to $\Pi$. 
NP hard: hardest decision problem

Boolean Satisfiability Problem (SAT)
Find an input such that $f(x)$ is true. $x_{1} \land \lnot x_{1}$ is not satisfiable.

SAT is NP complete

Halting problem: Given a Turing machine and the initial input, decide whether it will end or not.
Halting problem is undecidable

True Quantified Boolean Formula. TQBF
Continuation passing style.

real number/transcendental number: real numbers that cannot be constructed with polynomials in $\mathbb Q$

Most elements in $\mathbb R$ are transcendental. However, we can hardly list many of them.

* TQBF: PASPACE but outside NP
* SAT/3-SAT: NP-complete
* Halting: Outside PSPACE
* PRIME: P
* Factorization/DLP: NP - P

CNF: Conj of disj

3-SAT: an CNF where each clasue has exactly 3 literals.
Transform problems: Easy to hard. A -> B: A is easier than B.
Want to show: SAT -> 3-SAT, which shows SAT is easier than 3-SAT, or 3-SAT is harder than SAT.  notation: $\ltimes$

Network flow:

* graph
* capacity of each edge
* current flow on each edge
* source and sink

# randomized algo

* deterministic
* monte carlo: may have false positive, e.g. prime test
* las vegas: running time is random, e.g. quick sort

probabilistic turing machine.
For language $L$, it's in Bounded-error Probabilistic Polynomial time complexity class (BPP) if:

* M runs in poly time
* M outputs 1 with prob $>1/2 + \varepsilon$ for $x$ in $L$
* M outputs 1 with prob $<1/2 - \varepsilon$ for $x$ not in $L$

## PIT

polynomial identity test
Decide whether a multivariate poly is identically zero.
Identially 0 is different from being 0 everywhere.
$x^2 + x$ in $\mathbb{F}_2$ is 0 everywhere, but not identically 0.

Schwartz-Zipple Lemma:
$P$ multivariate poly

## Min-Cut Problem

Do random at first, and deterministic at the end. Too likely to make a mistake if we keep select randomly at the end.

Do something twice, no impact in complexity (especially with multi thread), but the probabily of bad result is reduced.

Accumulative probability: Go until the probability is dangerous, fork into 2 (or more), do recursion.

Suppose the probabily of failure is $1/2$ at each branch, 

$$
P(n) = \frac{1}{4}+\frac{1}{2}P(n-1)+\frac{1}{4}P(n-1)^2
$$

# Mathematical Problems

Ring = Abelian group for addition + monoid for multiplication + Distributivity 

Field = Ring + multiplicative inverse

Some definitions

* $a\in R$ is a zero divisor if there exists nonzero $b$ such that $ab = 0$. Example: matrix multiplication, $\mathbb Z/\mathbb Z_6$

* If $0$ is the only zero divisor, then $R$ is an integral domain

* $\omega^n = 1$ implies $\omega$ is the $n$-th root of unity

* $\omega$ is a primitive $n$-th root of unity if it is the $n$-th root of unity and $\omega^{n/t}-1$ is not a zero divisor, i.e. $w^{n/t}\neq 1$ for prime divisors $t$. "Primitive" simply means it is the first to reach 1. 

Lemma: 

$R$ is a ring, $1<l<n$, $\omega$ is the $n$-th primitive root of unity. Then

* $w^l-1$ is not a zero divisor

* $\sum_{j=0}^{n-1}\omega^{jl}=0$

Proof: Let $d=\gcd(l,n)$, $sl+tn=d$, $d\mid n/r$ for some prime $r$. (for simplicity, $\neq0$ means not a zero divisor here)

$$
\omega^{n/r}-1=(\omega^d-1)\left(1+\omega^d +\cdots + \omega^{d(n/rd-1)}\right) \neq 0
$$

Hence $\omega^d-1\neq 0$. Note that $\omega^{sl}-1 = \omega^{d}-1$, then $\omega^l-1$ divides $\omega^d-1$, apply similar trick and get

$$
\omega^{ln-1}=(\omega^l-1)\sum_{j=0}^{n-1}\omega^{lj}=0
$$

finishing our proof.

DFT:

Write

$$
P(X)=\sum_{i=0}^{n-1}a_i X^i = \left(a_0, \cdots, a_{n-1}\right)
$$

The linear map

$$
\begin{aligned}
DFT_{\omega} &: R^n \to R^n \\
(a_0,\cdots, a_{n-1}) &\mapsto (P(1), P(\omega), \cdots P(\omega^{n-1})) 
\end{aligned}
$$

is called the discrete fourier transform

Condition for the matrix to be invertible: the determinant is **invertible**.

Conclusion:

$$
DFT_{\omega}^{-1} = \frac{1}{n}DFT_{\omega^{-1}}
$$

## Polynomial Fast Multiplication

Horner algorithm of evaluating polynomials

$$
P(X)=a_0+X(a_1+X(a_2+\cdots +X(a_{n-1}+Xa_{n})))
$$

What we can/cannot do...

Using DFT: evaluation = interpolation. one function for both.

Choose $1,\omega, \cdots \omega^{n-1}$ as the points to evaluate. 

How to compute DFT fast?

$$
P(X)=P_1 (X^2) + X P_2 (X^2)
$$

divide and conquer!

Suppose $n$ is even (2's power), we can get

$$
0=\omega^n - 1 = (\omega^{n/2}-1)(\omega^{n/2}+1)
$$

which implies

$$
\omega^{n/2} = -1
$$

Hence

$$
\begin{aligned}
P(\omega^i) &= P_1(\omega^{2i})+\omega^i P_2(\omega^{2i}) \\
P(\omega^{i+n/2}) &= P_1(\omega^{2i})-\omega^i P_2(\omega^{2i})
\end{aligned}
$$

These two equations can be used to reconstruct the polynomial from the sub-results

We can then derive the fast fourier transform algorithm (FFT)

Construct $\mathbb C$:

$\mathbb C=\mathbb R[i] = \mathbb R[x]/\left<x^2+1\right>$

$\mathbb Z[i] = \{a+bi: a,b\in\mathbb Z\}$: a ring

Most rings do not have a $\gcd$.

## Fast Integer Multiplication

Write integers into polynomials (base what?), and apply fast polynomial multiplication. 

Question: Why do we use $2^{\sqrt{N}}$ ?

If we directly use base-2:

$$
a = \sum_{i=0}^{N}A_i 2^i
$$

where $A_i\in\{0,1\}$

Fast poly mult takes $\mathcal O(N\log N)\times \mathcal O(1)$

Other steps take no more than $\mathcal O(N)$

Use base-$\sqrt{N}$: (Question: what algo is used for sub-multiplications?)

$$
a = \sum_{i=0}^{\sqrt{N}-1}A_i \left(2^{\sqrt{N}}\right)^i
$$

where $A_i < 2^{\sqrt N}$

Fast poly ($n^2$ mul): $\mathcal O(\sqrt{N}\log N) \times \mathcal O(\sqrt{N}...)$

Other steps take no more than $\mathcal O(\sqrt{N})$

But in practice, the former one works better.

# Other Topics

## Amotized Analysis

Aggregate/Accounting/Potential

Potential: See RB-tree time complexity proof in intro to algo

A *potential* is associated to the current state of the data structure $D$

$$
\hat{c_i} = c_i + \phi(D_i)-\phi(D_{i-1})
$$

