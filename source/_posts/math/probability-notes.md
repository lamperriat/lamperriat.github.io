---
title: 'Notes: Probabilistic Methods in Engineering (English)'
date: 2025-08-28 12:58:14
categories: math
---

*本篇为课程笔记，仅供参考*

### Elementary Probability

**Def**: Set $A$ is *countable* if $A$ is finite or there exists a bijection from $\mathbb N$ to $A$.

**Def**: A *sample space* is a set $\Omega$ that each physical outcome of the experiment corresponds to exactly one element in $\Omega$. An element in $\Omega$ is a *sample point*.

**Def**: A suitable subset $A$ of a sample spcae is an event. The empty set is *impossible event*. $\Omega$ itself is the *certain event*.

* If $\Omega$ is countable, the event space can be $\mathcal P(\Omega)$.

* Otherwise the event space is typically a proper subset of $\mathcal P(\Omega) $

The second bullet point will be explained after the following axiom.

**Axiom**: Axiom of probability. Let $\mathcal F$ be the collection of all events, a function $P:\mathcal F\to [0, 1]$ is a probability measure (aka probability function, probability) if

* $P[\Omega] = 1$

* For a collection of mutually exclusive events (countably many) $\{A_k\}_{k\in\mathbb N}\subseteq \mathcal F$, 

$$
P[\bigcup_{k\in\mathbb N} A_k] = \sum_{k\in\mathbb N}P[A_k]
$$

Probability space $(\Omega, \mathcal F, P)$

---

**Extra**: Now we see why we need the second bullet point. To begin with, 

> At a purely formal level, one could call probability theory the study of measure spaces with total measure one, but that would be like calling number theory the study of strings of digits which terminate. —Terence Tao

Actually, deriving the probability of an event is the same as deriving a measure of a set. For non-countable set, we can construct a special set that is not (Lebesgue) measurable. Under Lebesgue measure, $\ell([0, 1])=1$. Let's construct a non-measurable set, Vitali set.

The idea is to partition $[0,1]$ into equivalent classes. Knowing that rational numbers is a normal subgroup of real numbers under addition, we can construct

$$
{\sim }=\{(x,y): x - y\in \mathbb Q\land x,y \in [0,1]\}
$$

By Axiom of Choice, we can take one element from each equivalent class, and elements will form a new set, say $V$. 

Noticing that the set of all rational numbers in $[-1,1]$, i.e. $[-1,1]\cap \mathbb Q$ is countable, and it can then be described as $\{r_i\}_{i=1}^{\infty}$. 

Define $V_k := r_k +V$. $V_i \cap V_j = \varnothing$ for all $i, j$ since if $x\in V_i$ and $x\in V_j$, $r_i +V = r_j+V$ which implies there exists $v_i, v_j\in V$ such that $r_i -r_j = v_i - v_j$, contradicting with the property of $V$. 

We claim that

$$
[0,1]\subseteq \bigcup_{i=1}^{\infty}V_k \subseteq [-1,2]
$$

The second inclusion is obvious. For the first inclusion, for $x\in[0,1]$, there exists $v\in V$ such that $x\sim v$. Hence $r := x-v\in \mathbb Q$. Meanwhile $x, v\in [0,1]$, hence $r=x-v\in[-1,1]$. As $x = v+r$ and $r\in [-1,1]\cap \mathbb Q$, $x\in V_i$ for some $i$. 

Apply length to the three expressions, we get

$$
1\leq \ell(\bigcup_{i=1}^{\infty} V_k)\leq 3
$$

In that case, the axiom of probabilty cannot be true. Otherwise

$$
\ell(\bigcup_{i=1}^{\infty} V_k) = \sum_{i=1}^{\infty}\ell(V)
$$

cannot be bounded.

---

Some theorems that can be derived from the axiom

* $P[\varnothing] = 0$

* $P[A^C] = 1-P[A]$

**Theorem**: Principle of Inclusion-Exclusion

$$
P[A_1\cup A_2]=P[A_1]+P[A_2]-P[A_1\cap A_2]
$$

Can be generalized to $n$ sets. Usually, intersections preserve the algebraic structure better than union (say, group, vector spaces, ...) and as a result we might be able to calculate the probability more easily.

### Condition Probability

**Def**: The probability of $B$ given $A$ ($P[A]\neq 0$) is

$$
P[B\mid A] = \frac{P[A\cup B]}{P[A]}
$$

This is not feasible to non-countable spaces. However, a common way to address those problems is that we define a thing, and when it's not feasible, we use the property of the previous definition to define it again. 

>  Tell me who your friends are, and I will tell you who you are.

For $P[A]=0$, we need conditional expectation with indicator function. 

**Def**: $A$ and $B$ are independent if

$$
P[A\cap B] = P[A]P[B]
$$

**Threorem**: $A$ and $B$ are independent is equiavelent to

* $P[A]\neq 0$, $P[B\mid A] = P[B]$

* $P[B]\neq 0$, $P[A\mid B]=P[A]$

**Def**: A finite collection of events is pairwise independent if every two of them (every pair) are independent., i.e. for all $i\neq j$

$$
P[A_i]P[A_j] = P[A_i\cap A_j]
$$

**Def**: A finite collection of events is mutually independent if every event is independent of any intersection of other events, i.e. for all $k\leq n$, $1\leq i_1\leq\cdots\leq i_k\leq n$

$$
P[\bigcap_{j=1}^k A_{i_j}] = \prod_{j=1}^k P[A_{i_j}]
$$

Mutually independency is stronger than pairwise independency. Considering the set

$$
\Omega = \{000, 011, 101, 110\}
$$

$A_i$: the i-th digit is zero. $P[A_i] = 1/2$, $P[A_i\cap A_j]=1/4$. But

$$
P[A_0\cup A_1 \cup A_2] = 1/4
$$

Mutually exclusive events cannot be mutually independent unless one of them has probability 0. 

**Theorem**(Total Probability): $I\subseteq \mathbb  N$, $\{A_i\}_{i\in I}\in\mathcal F$ is a partition of sample space, then

$$
P[B] = \sum_{i\in I}P[B\cap A_i] = \sum_{i\in I}P[B\mid A_i]P[A_i]
$$

Note that in set algebra, 

$$
B = B\cap \Omega = B\cap \bigcup A_i = \bigcup (B\cap A_i)
$$

---

A function $f: \mathbb R\to \mathbb R$ is a pmf iff

* $f(x)\geq 0$ for all $x$

* $\sum_{x\in\mathbb R}f(x) = 1$

The notation in the second expression is interesting, since the notation $\sum_{x\in S} x$ is usually used for countable set. Let's take a deeper look at it.

The infinite sum of a function $f: S\to \left[0, \infty\right)$ is defined as

$$
\sum_{x\in S} f(x) := \sup \left\{\sum_{x\in F} f(x): F\subseteq S, F \text{ is finite} \right\}
$$

which is actually a generaliztion of

$$
\sum_{i=0}^{\infty} f(x) := \lim_{n\to\infty} \sum_{i=0}^n f(x)
$$

We need the first condition due to Riemann rearrangement theorem.

It turns out that when the result is finite, the *support* of $f$ is at most countably infinite. The support of $f$ is

$$
\mathrm{supp}\ f := \{x\in S: f(x)\neq 0\} 
$$

Proof (by me):

Let $A := \mathrm{supp}(f)$. For each element $a\in A$, the subset $\{x\in A: x>a\}$ must be finite (otherwise the sum is infinite). We can then assign an index to $a$. The index is the size of the subset. In this way, we can assign an index to all elements in $A$, hence $A$ is countable.

Proof 2:

Let $S_n := \{x\in A: f(x)\geq 1/n\}$. $S_n$ is finite. $A = \bigcup S_n$ is a countable union of finite sets, which is also countable. 

### Discrete Distributions

Monte hall problem (three doors)

* 1/3: choose car
* 2/3: empty

A random variable is neither random nor a variable. its a function

$$
X: \Omega \to\mathbb R, \quad \omega \mapsto X(\omega)
$$

The probability that $X$ takes on a value in $S$ is

$$
\Pr[X\in S]:=P[\{\omega\in\Omega: X(\omega)\in S\}]
$$

equivalently: $P[X^{-1}(S)]$ ($X^{-1}$ is an abuse of notation)

example: rolling a dice. $X$ maps "x-face up" to 1 to 6. And we want to calculate the probability that $X(\omega) = 6$

CDF (cumulative distribution function, or simply DF)

$$
F_X(x) = \Pr[X\leq x] = P[\{\omega\in\Omega:X(\omega)\leq x\}]
$$

- non-decreasing

- right-continuous

A random variable is discrete if the image of $X$ is countable, the probability of $X$ taking on some value $x$ is given by the PMF (probability mass function)

$$
px : \mathbb R\to[0,1], px(x) := P[X=x]
$$

continuous if there exists $f_X:\mathbb R\to\mathbb R$ such that

$$
F_X(x) = \int_{-\infty}^x f_X(y)dy
$$

The function $f_x$ is then called the probability density functiuon (PDF)

cantor devil's staircase

Let $X$ be a discrete rv with pmf $p_x$. The expectation is given by

$$
\mathbb E[X] = \sum x_i p_x(x_i)
$$

$X$ has finite expectation (expectation exists) if the sum converges absolutely. Otherwise we say the expectation does not exist.

St. Petersburg Paradox

Flip a coin until you lose. Each time the prize doubles. The expectation is infinity but no one would like to pay to play the game.

**Def/Theorem**(LOTUS, Law of the unconscious statistician):

Given rv $X: \Omega\to \mathbb R$ with pmf $p_x$, a function $\phi: \mathbb R\to\mathbb R$, then $\phi\circ X$ is also a rv. If $\phi(X)$ has finite expectation, then

$$
\mathbb E[\phi(X)] = \sum_{i} \phi(x_i)p_x(x_i)
$$

Intuition: say $\phi : x\mapsto x^2$. $\Omega = \{-1, 1\}$. Although $-1$ is maped to $1$, we can simply add them and treat them as if in the new pmf they are different. Inverse image forms a partition. 

**Theorems**: 

* $\mathbb E[\lambda X+\mu Y] = \lambda \mathbb E[X]+\mu\mathbb E[Y]$. Linear even for infinite sum. 

* If $\phi: \mathbb R\to\mathbb R$ is convex, then $\varphi(\mathbb E[X])\leq \mathbb E[\varphi(X)]$. (Jensen's inequality)

* If $X\leq Y$ (*almost everywhere* for continuous variable), then $\mathbb E[X]\leq\mathbb E[Y]$

Indicator function $1_A$. 

$$
P[X\in A] = P[A] = \mathbb E[1_A]
$$

TFAE

* $X$ and $Y$ are independent

* $P[X\in A, Y\in B] = P[X\in A]P[Y\in B]$ for all subsets $A, B$

* $\mathbb E[g(X)h(Y)]=\mathbb E[g(X)]\mathbb E[h(Y)]$ for all functions $g, h$

**Def**: Variance

$$
\mathrm {Var}\ X = \sigma^2 = \mathbb E[(X-\mu)^2] 
$$

where $\mu$ is the mean ($\mathbb E[X]$)

$$
\mathrm{Var}\ X = \mathbb E[X^2] - (\mathbb E[X])^2
$$

By $\mathrm{Var}\ X\geq 0$, we can get an equality.

**Theorem**: If $X, Y$ are independent(looser condition: corelated), 

$$
\mathrm{Var}\ (X+Y) = \mathrm{Var}\ X + \mathrm{Var}\ Y
$$

**Def**: Geometric distribution: 

$$
p_X(x) = (1-\theta)^{x-1}\theta, \quad 0 < \theta \leq 1, \quad x = 1,2,3,\cdots
$$

We write $X\sim \text{Geometric}(\theta)$

CDF: 

$$
F_X(x) = 1 - (1-\theta)^{\lfloor x\rfloor}
$$

Moment Generating Function

**Def**: The $k$-th ordinary moment for $X$: $\mathbb E[X^k]$

**Def**: The moment generating function (mgf): $m_X(t) = \mathbb E[e^{tX}]$

(kind of like Laplace transform, also similar to the generating function we have seen)

The distribution of a rv is uniquely characterized by the mgf.

The $k$-th moment is then given by (Taylor expansion)

$$
\mathbb E[X^k] = \frac{d^k}{dt^k} \Big|_{t=0} m_X(t)
$$

mgf of Geometric distribution

$$
m_X(x) = \frac{e^t\theta}{1-e^t(1-\theta)}
$$

**Def**: Binomial distribution

$$
p_X(x) = \begin{pmatrix}
n \\ x
\end{pmatrix} \theta^x (1-\theta)^{n-x}
$$

$X\sim \text{Binomial}(\theta)$. Using binomial theorem, we can verify it is valid.

CDF:

$$
F_X(t) = \sum_{x=0}^{\lfloor t\rfloor}\begin{pmatrix}n\\x \end{pmatrix}\theta^x (1-\theta)^{n-x}
$$

mgf: (again via binomial theorem)

$$
m_X(t) = (1-\theta + \theta e^t)^n
$$

**Def**: Negative binomial distribution (trials are observed until exactly $r$ successes are obtained, $X$ is the number of trials needed to obtain $r$ successes)

$$
p_X(x) = \begin{pmatrix} x-1\\r-1 \end{pmatrix} (1-\theta)^{x-r}\theta^r
$$

When $r=1$, it is geometric distribution. $r-1$ because the last time must be success

**Def**: Negative binomial distribution

mgf:

$$
m_X(t) = \frac{(\theta e^t)^r}{(1-(1-\theta)e^t)^r}
$$

**Def**: Hypergeometric Distribution

Sample from a inite population

- with replacement (re-place: literally place it back): binomial

- without replacement (draws are not independent): hypergeometric distribution

A rv has a hypergeometric distribution with parameters $N, n, r$ if its pmf is given by

$$
p_X(x) = \frac{\begin{pmatrix}r\\x\end{pmatrix} 
\begin{pmatrix} N-r\\n-x \end{pmatrix} }
{\begin{pmatrix} N\\n \end{pmatrix}}
$$

drawing a random sample of size $n$ without replacement. $r$: success, $N$: total. $X$ is the number of objects in the sample we interested in.

The distribution is valid is equivalent to Vandermonde's identity/convolution

Proof: expand

$$
(1+t)^N = (1+t)^r (1+t)^{N-r}
$$

**Theorem**: For hypergeometric distribution

- $\mathbb E[X] = nr/N$

- $\mathrm{Var}\ X = nr(N-r)(N-n)/N^2(N-1)$

To get both, we will need the property that $p_X(x)$ sums to 1.

We can also use

$$
\begin{aligned}
\mathrm{Var}\ X &= \mathbb E\left[\left(\sum X_i\right)^2\right] 
- \left(\mathbb E\left[\sum X_i\right]\right)^2 \\
&= \sum \mathbb E[X_i^2] -2\sum \mathbb E[X_iX_j] 
- \left(\sum\mathbb E[X_i]^2+2\sum\mathbb E[X_i]\mathbb E[X_j]\right) \\
&=\sum \mathrm{Var}\ X_i + 2\sum \mathrm{Cov}(X_i, X_j)
\end{aligned}
$$

where

$$
\mathrm{Cov}(X_i, X_j) = \mathbb E[X_iX_j] - \mathbb E[X_i][X_j]
$$

**Def**: Poisson distribution

$$
p_X(x) = \frac{e^{-k}k^x}{x!}
$$

Easy to verify by expanding $e^k$

mgf:

$$
m_X(t) = e^{k(e^t-1)}
$$

$\mathbb E[X] = \mathrm{Var}\ X = k$

**Theorem**: The sum of two Poisson rv is still Poisson

Given independent rv X, Y, $m_{X+Y}(t) = m_X(t)m_Y(t)$

By using $\mathbb E[X] \mathbb E[Y] = \mathbb E[XY]$ for independent rv. Then we can check $m_{X+Y}(t)$ for $X, Y$ are both Poisson.

Possion from binomial: Consider rv $X_n\sim\text{Binomial}(n, \theta_n)$, and let the mean $n\theta_n = \lambda$ be dixed. The mgf of $X_n$ is

$$
M_{X_n}(t) = (1-\theta_n + \theta_n e^t)^n = \left(1+\frac{\lambda}{n}(e^t-1)\right)^n
$$

by taking the limit $n\to\infty$, we can get $X\sim\text{Poisson}(\lambda)$

$$
\lim_{n\to\infty} e^{-n}\sum_{k=0}^n \frac{n^k}{k!} = \frac{1}{2}
$$

Let rv $N_r\sim\text{NegBinomial}(r, \theta_r)$, shift $Y_r = N_r - r$, we can get

$$
\lim_{r\to\infty} M_{Y_r}(t) = e^{\lambda (e^t - 1)}
$$

Poisson distribution: related to possion process.

General Poisson Process: model temporal or spacial objects

- Variable of interest: $N$, the number of occurrences/arrivals

- Continuous interval: Length of $s$ units (time, length, space, ...)

Example: during 3 months, the emission of radioactive gases; waiting for buses; ...

$N = \{N_t\}_{t\geq 0}$ is a counting process that counts how many times something happens from time 0 to time $t$. Actually

$$
N: \Omega\times \mathbb R\to \mathbb N
$$

- Usually we fix $\Omega$ and see how it changes with $t$, which is a *sample path*.

- If we fix $t$, we will get a random variable

A counting process is Poisson if

- $N_0 = 0$

- For almost all $\omega$, each jump is of size one

- For all $t,s\geq 0$, $N_{t+s} - N_s$ is independent of $\{N_u\}_{0\leq u\leq t}$

- For all $t,s\geq 0$, the distribution of $N_{t+s} - N_s$ is independent of $t$.

Let $f(t) = \Pr[N_t = 0]$, we can get $f(s+t) = f(s)f(t)$

By adding continuous/boundness, we can get $f(t) = e^{-\lambda t}$

Idea: By taking log, its equivalent to solve $g(t+s)=g(t)+g(s)$, we can easily get the function is linear on all rational numbers. Then by taking Cauchy sequence (say by continuity), we can conclude $g$ is linear.

Another property: instant two jumps are practically impossible,

$$
\lim_{t\to 0^+} \frac{1}{t} \Pr[N_t\geq 2]=0
$$

The case left is $\Pr[N_t=1] = 1-\Pr[N_t=0]-\Pr[N_t\geq 2]$.

$$
\lim_{t\to 0^+} \frac{1}{t} \Pr[N_t=1] = \lambda
$$

mgf: $G_t(\alpha) = \mathbb E[e^{\alpha N_t}]$. $G_0(\alpha)=1$.

$$
G_{t+s}(\alpha) = G_t(\alpha) G_s (\alpha)
$$

There exists some $g$ s.t. $G_t(\alpha) = e^{tg(\alpha)}$(need some effort), we have

$$
\begin{aligned}
g(\alpha) &= \lim_{t\to0^+} \frac{1}{t}(G_t(\alpha)-G_0(\alpha)) \\
&= \lim_{t\to0^+} (\frac{1}{t} \Pr[N_t=0] - 1) +  
\lim_{t\to0^+}e^{\alpha} \frac{1}{t} \Pr[N_t=1] + \cdots \\
&= -\lambda + e^{\alpha}\lambda
\end{aligned}
$$

Hence $G_t(\alpha) = e^{\lambda t(e^{\alpha} -1)}$, and $N_t \sim \text{Poisson}(\lambda t)$

$$
\Pr[N_{t+s} - N_t =k] = \Pr[N_s = k] = \frac{e^{-\lambda s}(\lambda s)^k}{k!}
$$

$\lambda$: average num of occurrences per unit; $s$: length of observation (unit)

Other ways to characterize Poisson process:

- $N_0 = 0$

- For all $s, t\geq 0$,

$$
\Pr[N_{t+s} - N_t =k]= \frac{e^{-\lambda s}(\lambda s)^k}{k!}
$$

- For disjoint time intervals, the increments $N_{t_{n+1} -t_n}$ are independent increments.

Another way:

- $N_0 = 0$

- $\displaystyle \lim_{h\to 0^+}\frac{1}{h}\Pr[N_{t+h} = 1] =\lambda$, where $\lambda$ is the rate/intensity of the process, i.e. the probability of one jump is $\lambda h + o(h)$

- $\displaystyle \lim_{h\to 0^+}\frac{1}{h}\Pr[N_{t+h} \geq 2] =0$, i.e. probability of two or more jumps is $o(h)$

From the definition, we can (need some efforts, again use $\Pr[N_{t+h}-N_t=0]=\Pr[N_h=0]$) derive the following system of ODEs. $p_k(t) := \Pr[N_t =k]$

$$
\begin{aligned}
\frac{dp_0(t)}{dt} &= -\lambda p_0(t),& p_0(0) &= 1; \\
\frac{dp_k(t)}{dt} &= -\lambda p_k(t)+\lambda p_{k-1}(t),& p_k(0) &= 0; \\
\end{aligned}
$$

A trick is to use $t-h$ to eliminate the one-side limit.

Waiting paradox: It's more easily to fall in a longer waiting interval 

### Continuous Distribution

If $F_X$ is continuous, $\Pr[X=x] = 0$ for any $x$

$f_X$(probability density) is unique up to a set of measure zero. $f_1$ and $f_2$ agrees almost everywhere (a.e.) if $f_1(x) = f_2(x)$ for all $x$ except for a set of measure 0.

**Def**: A subset $N\subseteq \mathbb R$ has measure zero if for all $\varepsilon > 0$, there exists a sequence of intervals s.t.

$$
N\subseteq \bigcup I_k, \;\sum \mathrm{len}(I_k) < \varepsilon
$$

Intuition: can be convered by intervals of arbitrary small length.

Example: Any countable set has measure 0. We simply assign length $\varepsilon/2^k$ for each single point, and we add up the lengths, its still smaller than $\varepsilon$.

Example: All subsets of $\mathbb R^n$ whose dimension is smaller than $n$ has measure 0 in $\mathbb R^n$.

Example: The Cantor set is uncountable but has measure 0 in $\mathbb R$.

Sard's lemma: the set of critical values of a smooth function has measure 0.

**Def**: A function $f_X: \mathbb R\to\left[0, \infty\right)$, where $X$ is a continuous rv

* $\int_{-\infty}^{\infty} f_X(x)dx = 1$

* $\Pr[a\leq X\leq B] = \int_a^b f_X(x)dx$

By fundamental theorem of calculus $f_X = F_X'$.

Assume absolutely integrable, the expectation is

$$
\mathbb E[X] = \int_{-\infty}^{\infty} xf_X(x)dx
$$

LOTUS: same as the discrete version.

Similarly, the mgf for $X$ is (kind of like Laplace transform)

$$
\mathbb E[e^{tX}] = \int_{-\infty}^{\infty} e^{tx} f_X(x)dx
$$

The $k$-th moment is $\mathbb E[X^k]$.

**Def**: Gamma function

$$
\Gamma(\alpha) = \int_0^{\infty} z^{\alpha - 1}e^{-z}dz, \alpha > 0
$$

**Def**: Gamma distribution, a continuous rv $X$ with density

$$
f(x) = \frac{1}{\Gamma(\alpha)\beta^{\alpha}} x^{\alpha - 1}e^{-x/\beta},\quad x,\alpha,\beta>0
$$

Note that

$$
\begin{aligned}
\int_0^{\infty} f(x) &=  \frac{1}{\Gamma(\alpha)\beta}\int_0^{\infty} 
(x/\beta)^{\alpha - 1}e^{-x/\beta }dx \\
&= \frac{1}{\Gamma(\alpha)}\int_0^{\infty} (x/\beta)^{\alpha - 1}e^{-x/\beta}d(x/\beta)\\
&=1
\end{aligned}
$$

(rigorously, we should stick to the substitution rule)
We write $X\sim\text{Gamma}(\alpha, \beta)$. The multiplier is used to normalize.

* mgf: $m_X(t) = (1-\beta t)^{-\alpha}, t<1/\beta$

* $\mathbb E[X]=\alpha \beta$, $\mathrm{Var}\ X = \alpha\beta^2$

An easy way to get it is using binomial theorem to expand mgf.

**Def**: Gamma distribution with $\alpha = 1$

$$
f(x)=\frac{1}{\beta}e^{-x/\beta}
$$

Consider a Poisson process with parameter $\lambda$, Let $W_1$ denote the time of occurence of the first event, then $W_1\sim\text{Exponential}(1/\lambda)$. We can show this by calculating the cdf

Equivalent definition: A Poisson process is a *arrival process* with independent and identically distributed interarrival times $W_k$ follwing an exponential distribution. 

**Def**: $X\sim \text{Gamma}(k/2, 2)$ is said to have a $\chi^2$-distribution with $k$ degrees of freedom.

**Def**: A rv $X$ with pdf

$$
f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}, \quad x\in\mathbb R
$$

is said to have a normal distribution or Gaussian distribution. $X\sim\mathcal{N}(\mu, \sigma^2)$

mgf:

$$
m_X(t) = e^{\mu t+\sigma^2 t^2/2}
$$

by doing completion of square. 

By Taylor expansion, we can get the mean and variance easily.

We can scale the rv, 

$$
\frac{X-\mu}{\sigma}\sim\mathcal{N}(0,1^2)
$$

Proof: 

Using CDF, $F_Z(z) = F_X(\mu + \sigma z)$, and $f_Z(z) = F_Z'(z) = f_X(\mu+\sigma z)\cdot \sigma$. Similarly, we can derive the transformation of variables later.

Interpretation for mgf of normal distribution $X\sim\mathcal N(0,1^2)$. Let $m_k := \mathbb E[z^k]$

$m_1 = 0, m_2 = 1, m_3 = 0, m_4 =3 , ...$

$m_i$ is the number of matchings in an $i$-node graph. By expanding $m_X(t) = e^{t^2/2}$,

$$
m_X(t) = \sum_{k=0}^{\infty} \frac{(t^2/2)^k}{k!} =
 \sum_{k=0}^{\infty} \frac{t^{2k}}{2^kk!}
$$

which gives

$$
m_k = \frac{(2k)!}{2^kk!}
$$

**Theorem**(Transformation of Variables): Let $X$ be a rv with density $f_X$. $Y=g(x)$, $g$ is strictly monotonic and $C^1$, then

$$
f_Y(y) = \begin{cases}
\displaystyle f_X(g^{-1}(y)) \left|\frac{dg^{-1}(y)}{dy}\right|, &y\in \mathrm{im}\ g \\
0, & \mathrm{o/w}
\end{cases}
$$

Proof: again use CDF. It's hard to use density, and cumulative one is much easier to deal with. WLOG, we can assume $g$ is decreasing/increasing

For standard normal distribution, there does not exist an anti-derivative in elementary form. We use $\Phi$ to denote the anti-derivative.

$$
\Phi: \mathbb R\to[0, 1], \quad \Phi(x) = \int_{-\infty}^x \frac{1}{\sqrt{2\pi}}e^{-t^2/2}
$$

Error function $\mathrm{erf}$,

$$
\mathrm{erf}: \mathbb R\to[-1,1], \quad \mathrm{erf}(z)=\frac{2}{\sqrt \pi}\int_{0}^z e^{-t^2}dt
$$

Note that $\mathrm{erf}\to 1$ as $z\to\infty$. $\mathrm{erfc}=1-\mathrm{erf}(z)$

$$
\Phi(X) = \frac{1}{2} \left(1+\mathrm{erf}\frac{x}{\sqrt 2}\right) = \frac{1}{2}\mathrm{erfc}\left(\frac{-x}{\sqrt 2}\right)
$$

68-95-99.7 rule:

- $\Pr[|x-\mu| < \sigma] = 0.68$

- $\Pr[|x-\mu| < 2\sigma] = 0.95$

- $\Pr[|x-\mu | < 3\sigma] = 0.997$

**Theorem**(Markov's inequality):

Given rv $X$ with $\mathbb E[X] < \infty$, for any $\varepsilon > 0$,

$$
\Pr[|X|\geq \varepsilon] \leq \frac{\mathbb E[X]}{\varepsilon}
$$

> Extreme cases are bounded by average.

Proof: Let $A = \{\omega \in \Omega: |X(\omega)| \geq \varepsilon\}$,

$$
\mathbb E[|X|] \geq \mathbb E[\varepsilon 1_A(X)] = \varepsilon \Pr[|X|\geq \varepsilon]
$$

We can visualize the inequality by drawing complementary CDF.

Note that

$$
\mathbb E[X] = \int_0^{\infty} F_X^C(x)dx = \int_{0}^{\infty} \Pr[X>x]dx
$$

Discrete version:

$$
\mathbb E[X] = 0\cdot\Pr[x=0] + 1\cdot \Pr[x=1]+ 2\cdot \Pr[x=2] + \cdots
$$

Hence

$$
\begin{aligned}
\mathbb E[X] = \Pr[x=0] &+ \Pr[x=1]+ \Pr[x=2] +\cdots\\
&+\Pr[x=1] + \Pr[x=2] + \cdots 
\end{aligned}
$$

**Theorem**(Chebyshev's Inequality): Let $X$ be a rv with $\mu, \sigma$, for any $k>0$,

$$
\Pr[|X-\mu| < k\sigma] \geq 1 - \frac{1}{k^2}
$$

Kind of a second order description (compared to Markov)

Proof:

$$
\Pr[|X-\mu| \geq \varepsilon] = \Pr[|X-\mu|^2 \geq \varepsilon^2] \leq \frac{\sigma^2}{\varepsilon^2}
$$

take $\varepsilon = k\sigma$

Special case of CLT: using normal distribution to approximate binomial distribution.

Given $S_n \sim \text{Binomial}(n , \theta)$, for fixed $a,b\in\mathbb R$.

$$
\lim_{n\to\infty} \Pr\left[a < 
\frac{S_n - n\theta}{\sqrt{n\theta (1-\theta)}} < b \right] = 
\frac{1}{\sqrt{2\pi}}\int_a^b e^{-x^2 / 2}dx
$$

Shifted and normalized rv follows normal distribution.

Roughly speaking, $X\sim\text{Binomial}(n, \theta)$, approximately $X\sim\mathcal N(n\theta, n\theta(1-\theta))$ for large $n$. For practical purpose, we would use $\Pr[Y\leq x+1/2]$ to approximate. (i.e. choose the point in the middle, half-unit correction)

$$
\Pr[a\leq X\leq b] \approx 
\Phi\left(\frac{b+1/2-n\theta}{\sqrt{n\theta(1-\theta)}}\right)
- \Phi\left(\frac{a-1/2-n\theta}{\sqrt{n\theta(1-\theta)}}\right)
$$

We want $\theta < 0.5\land n\theta > 5$ or $\theta > 0.5\land n(1-\theta)>5$

Stirling's formula. Proof using Guassian integral:

$$
n! = \int_0^{\infty} x^n e^{-x} dx = \int_0^{\infty} e^{-(x-n\ln x)}  dx
$$

Let $f(x) := x-n\ln x$, We can approximate $f$ using a quadratic function.

$$
f(x) \sim n-n\ln n + \frac{1}{2n} (x-n)^2
$$

This makes sense because when $x$ is large, $f(x)$ tends to $-\infty$ and contributes little to the integral.

at $x=n$. Hence

$$
n! \approx e^{-n-n\ln n} \int_{\mathbb R} e^{-\frac{(x-n)^2}{2n}}dx = n^n e^{-n}\sqrt{2\pi n}
$$

**Def**: Weibull distribution

$$
f_X(x) = \alpha \beta x^{\beta - 1} e^{-\alpha x^{\beta}}, \quad x,\alpha, 
\beta > 0
$$

$\mu = \alpha^{-1/\beta} \Gamma(1+1/\beta)$

$\sigma^2 = \alpha^{-2/\beta} \Gamma(1+2/\beta) - \mu^2$

$\beta = 1$: exponential distribution

Consider a rv $T\geq 0$, time to fail with failure density $f$. 

Hazard function $h$ gives the instantaneous failure rate at $t$. 

$$
h(t)\Delta t = \Pr[t<T\leq t+\Delta t | T>t] = \frac{f(t)\Delta t}{R(t)}
$$

where $R := \Pr[T>t]$ is the reliability function, which gives the probability that not fail before $t$. Note that $f(t) = -R'(t)$, 

$$
h(t) = -\frac{R'(t)}{R(t)}, \quad R(0) = 1
$$

The IVP admits the solution $R(t) = e^{-\int_0^t h(t)dt}$

* $\beta = 1$: const hazard. failure due to random factors

* $\beta > 1$: hazard increasing, failure due to system wearing out

* $\beta < 1$: early failure due to malfunctioning system

Series system: one component fails, the system fails (serial connection of circuit)

### Joint Distribution

A multivariate random variable,or random vector is

$$
\mathbf {X} = (X_1, \cdots, X_n): \Omega \to E
$$

where $X_i$ are random variables. $E\subseteq\mathbb R^n$ is countable

Joint pmf

$$
p_{\mathbf X}(\mathbf x) = \Pr[X_1=x_1, \cdots, X_n = x_n]
$$

 Marginal pmf: $p_{X_k}(t)$, i.e. each $X_i$ itself as an rv 

Independent: $p_{XY}(x,y) = p_X(x)p_Y(y)$

Conditional probability: 

$$
p_{X\mid Y}(x\mid y) = \frac{p_{XY}(x,y)}{p_Y(y)}
$$

or we can use $p_{X\mid Y=y}(x)$, which makes it easier to understand. actually

$$
\Pr[X=x \mid Y=y] = \frac{\Pr[X=x,Y=y]}{\Pr[Y=y]}
$$

The expectation is derived component-wise.

Consider rv $(X, Y)$. The conditional expectation of the rv $X\mid (Y=y)$ is

$$
\mathbb E[X\mid Y=y] = \sum_x xp_{X\mid Y=y}(x)
$$

The mapping $\mathbb E[X\mid Y=\cdot ]$ induces a rv from $\mathrm{im}\ Y$ to $\mathbb R$, which is

$$
\mathbb E[X\mid Y]: \mathrm{im}\ Y \to \mathbb R, \quad
y\mapsto \mathbb E[X\mid Y=y]
$$

Note that

$$
\begin{aligned}
\mathbb E[\mathbb E[X\mid Y]] &= \sum_{y} \mathbb E[X\mid Y=y] p_Y(y) \\
&= \sum_y\left(\sum_x xp_{X\mid Y=y}(x)\right)p_Y(y) \\
&= \sum_x x\left(\sum_y p_{X\mid Y=y}(x)p_Y(y) \right) \\
&= \sum_x x \left(\sum_y p(x, y) \right) \\
&= \mathbb E[X]
\end{aligned}
$$

which is kind of like integrate over a $\mathbb R^2$ shape first horizontally then vertically or the opposite.

The mapping $y\mapsto \mathrm{Var}(X\mid Y=y)$ also induces an rv, $\mathrm{Var}(X\mid Y)$

$$
\mathrm{Var} (X\mid Y) = \mathbb E[X^2\mid Y] - \mathbb E[X\mid Y]^2
$$

**Theorem**(The Law of Total Variance): 

$$
\mathrm{Var}\ X = \mathbb E[\mathrm{Var}(X\mid Y)] + \mathrm{Var}(\mathbb E[X\mid Y])
$$

Proof:

Since

$$
\mathbb E[X^2] = \mathbb E[\mathbb E[X^2\mid Y]]
= \mathbb E[\mathrm{Var}(X\mid Y) + \mathbb E[X\mid Y]^2]
$$

and

$$
\mathbb E[X] = \mathbb E[\mathbb E[X\mid Y]]
$$

Taking $\mathrm{Var} = \mathbb E[X^2] - \mathbb E[X]^2$ and we can get the result.

Similarly we can define a continuous random vector. 

**Def**: The covariance, $\mathrm{Cov}(X, Y)$ or $\sigma_{XY}$ is

$$
\mathrm{Cov}(X, Y) = \mathbb E[(X- \mu_X)(Y-\mu_Y)]
= \mathbb E[XY] - \mathbb E[X] \mathbb E[Y]
$$

$\mathrm{Cov}(X, X) = \mathrm{Var}\ X$. $\mathrm{Cov}(X, Y) = 0$(uncorelated) if $X$ and $Y$ are independent. (i.e. independence is stronger) Converse in general is not true (true if $X, Y$ are both guassian).

Covariance is a kind of inner product (in Hilbert space)

Covariance matrix: $(C_X)_{ij} = \mathrm{Cov}(X_i,X_j)$. $C_X\in\mathbb R^{n\times n}$.

Note that

- $C_X$ is symmetric and positive semidefinite ($v^TC_xv\geq 0$, proof: rewrite it into a variance of some rv)

- Given $m\times n$ matrix $A$, the covariance matrix of $AX$ is $C_{AX} = AC_XA^T$ (proof: simply write it out)

**Def**: Pearson Coefficient of Correlation:

$$
\rho_{XY} = \frac{\mathrm{Cov}(X,Y)}{\sigma_X \sigma_y}
$$

(i.e. normalized covariance, similar to $\cos \theta = \frac{\left<x,y\right>}{||x||\cdot ||y||}$)

- $-1\leq \rho_{XY}\leq 1$

- $\rho_{XY} = 1$ iff there exists $\beta_0, \beta_1$ s.t. $Y=\beta_0 +\beta_1 X$ a.s., perfect positive correlation

- $\rho_{XY} = -1$: perfect negative correlation

- $\rho_{XY}=0$: uncorrelated ($\neq$ unrelated), or IF a relation exists, then it is not linear

a.s.: almost surely, i.e. $\Pr[X=Y]=1$, or x=y a.w.

$\rho = \pm 1$ is "too good to be true". Correlation is not transitive. (inner product illustration: is $v_1$ and $v_2$ form a $60^{\circ}$ angle, and so does $v_2$ and $v_2$, but this does not imply $v_1$ and $v_3$ forms a $60^{\circ}$ angle)

Conditional density:

$$
f_{X\mid Y}(x\mid y) = f_{X\mid Y=y}(x) = \frac{f_{XY}(x,y)}{f_Y(y)}, f_Y(y) > 0
$$

Counterintuitive fact: Consider a semi circle on $\mathbb R^2$, centered at origin. We can represent coordinates using polar or cartesian coordinate.

Case 1: $\Pr[Y > 1/2 \mid X= 0]$

$$
\iint_D f_{XY}(x,y) dxdy  = 1 \Rightarrow f_{XY}(x,y) = \frac{2}{\pi}
$$

Marginal density:

$$
f_X(0) = \int_{0}^1 f_{XY}(0,y) dy = \frac{2}{\pi} 
$$

Conditional

$$
f_{Y\mid X=0}(y) = \frac{f_{XY}(0,y)}{f_X(0)} = 1
$$

Integrate it and we can get $\Pr[Y > 1/2 \mid X= 0] = 1/2$, an intuitive result.

Case 2: $\Pr[R > 1/2 \mid \theta = 0]$

$$
\int_0^{\pi} \int_0^1 f_{R\Theta}(r, \theta) drd\theta = 
1 \Rightarrow f_{R\Theta}(r, \theta)  = \frac{2r}{\pi}
$$

Then,

$$
f_{\Theta}\left({\frac{\pi}{2}}\right) = \frac{1}{\pi}
$$

We can finally get $\Pr[R > 1/2 \mid \theta = 0] = 3/4$

Both are correct, probability density is a limit, they are different ways to partition the semi-circle, and take the limit. Different $\sigma$-fields are generated

Similar example: Borel-Kolmogorov Paradox

Given rv $(X, Y)$, $\mathbb E[X\mid Y=y]$ is called the curve of regression of $X$ on $Y$.

$$
\mathbb E[Y\mid X] = \argmin_{h} \mathbb E[(Y-h(X))^2]
$$

since

$$
\mathbb E[(Y-h(X))^2] = \mathbb E[(Y-\mathbb E[Y\mid X])^2] + 
\mathbb E[(\mathbb E[Y\mid X]-h(X))^2]

$$

Note that

$$
\begin{aligned}
\mathbb E[Y\mathbb E[Y\mid X]] &= \sum_{x, y} y p(x,y)
\left( \sum_{y'} y'p(x, y')\right) \\
&= \sum_x \left(\sum_y\left(yp(x, y)\left( \sum_{y'} y'p(x, y')\right) 
 \right)\right) \\
&=  \sum_x \left(\sum_y yp(x, y) \right)^2 \\
&= \mathbb E[\mathbb E[Y\mid X]^2]
\end{aligned}
$$

Actually there is an easier approach

$$
\begin{aligned}
\mathbb E[Y\mathbb E[Y\mid X]] &= 
\mathbb E[\mathbb E[Y\mathbb E[Y\mid X] \mid X ]] \\
&= \mathbb E[\mathbb E[Y] \mathbb E[Y \mid X] \mid X] \\
&= \mathbb E[\mathbb E[Y\mid X]^2]
\end{aligned}
$$

Now everything should be clear: $\mathbb E[(Y-\mathbb E[Y\mid X])^2]$ can actually be written as

$$
\mathbb E[Y^2 - 2Y\mathbb E[Y\mid X] + \mathbb E[Y\mid X]^2] = 
\mathbb E[Y^2 - \mathbb E[Y\mid X]^2]
$$

Hence

$$
\begin{aligned}
\mathbb E[(Y-h(X))^2] &= \mathbb E[Y^2 - 2Yh(X) + h(X)^2] \\
&= \mathbb E[Y^2 -  \mathbb E[Y\mid X]^2] \\&
+ \mathbb E[ \mathbb E[Y\mid X]^2 -2Yh(X) + h(X)^2]
\\&= \mathbb E[(Y-\mathbb E[Y\mid X])^2] + \mathbb E[(\mathbb E[Y\mid X]-h(X))^2]
\end{aligned}
$$

Properties

- $\mathbb E[\alpha \mid Y] = \alpha$

- Linearity

- $\mathbb E[X\mid Y]\geq 0$ a.s. if $X\geq 0$ a.s.

- $\mathbb E[\mathbb E[X\mid Y]] = \mathbb E[X]$

- If $X, Y$ independent, $\mathbb E[XZ\mid Y] =\mathbb E[X]\mathbb E[Z\mid Y]$

conditional expectation is a kind of projection. 

**Def**: Guassian rv $X\sim \mathcal N(\mu, \Sigma)$ has mean $\mu\in\mathbb R^n$ and positive semi-definite covariance matrix $\Sigma \in \mathbb R^{n\times n} \succeq 0$. The density is

$$
f_X(x) = \frac{1}{(2\pi)^{n/2} (\det \Sigma)^{1/2}} \exp\left(
-\frac{1}{2} (x-\mu)^T \Sigma^{-1}(x-\mu)\right)
$$

For bivariate normal rv,

$$
\Sigma = \begin{pmatrix}
\sigma_X^2 & \rho \sigma_X\sigma_Y \\
\rho \sigma_X\sigma_Y & \sigma_Y^2
\end{pmatrix}
$$

Property: $X_1\sim\mathcal N(\mu_1, \Sigma_1)$ and similar for $X_2$, $f_{X_1}f_{X_2}$ is the density for a new Gaussian rv with

$$
\mu = \Sigma(\Sigma_1^{-1} \mu_1+\Sigma_2^{-1}\mu_2), \quad
\Sigma = (\Sigma_1^{-1} +\Sigma_2^{-1})^{-1}
$$

Two Guassian rv are indepenent iff $\mathrm{Cov}(X, Y) = 0$

Let $Z$ be Guassian, and $Z = \begin{bmatrix}X\\Y\end{bmatrix}$

Guassian rv is closed under Linear transformation:

$$
AZ+b\sim \mathcal N(A\mu_Z + b, A\Sigma_Z A^T)
$$

A special case is marginalization $X\sim\mathcal N(\mu_X, \Sigma_{XX})$

Also closed under conditioning

$$
X\mid (Y=y)\sim\mathcal N(\mu_X + \Sigma_{XY}\Sigma_{YY}^{-1}(Y-\mu_Y)
, \Sigma_{XX} - \Sigma_{XY}\Sigma_{YY}^{-1}\Sigma_{YX})
$$

the latter part is schur complement. related to block matrix inverse

Fact: A rv is a Guassian rv iff all linear comnbination of its components are Guassian rb

Change of variable in calculus

$g: C^1$, injective on $D$

$$
\int_{g(D)} f(y)dy = \int_D f(g(x))\left|\det(J_g(x))\right|dx
$$

Suppose $X$ have joint density $f_X$, $Y = g(X)$ has the density

$$
f_Y(y) = \begin{cases}
f_X(g^{-1}(y))|\det(J_{g^{-1}}(y))|&, y\in\mathrm{im}\ g \\
0&, \text{o/w}
\end{cases}
$$

Note that $\det(J_{g^{-1}}) = 1/\det(J_g)$ by inverse function theorem.

Let $X, Y$ be indepent rv with density $f_X, f_Y$, the density for the sum $Z = X+Y$ is

$$
F_Z(z) = \int_{-\infty}^{\infty}\int_{-\infty}^{z-y} f_X(x)f_Y(y)dxdy
$$

and $f_Z(z) = \int_{-\infty}^{\infty}f_X(z-y)f_Y(y)dy = f_X * f_Y$, which is the convolution. Multiplication of numbers are just convolution (try to multiply $11111 * 11111$)

**Theorem**(Central Limit Theorem):

Let $X_i$ be iid rv, $S_n = X_1 +\cdots +X_n$,

$$
\lim_{n\to\infty} \left(\frac{S_n -\mathbb E[S_n]}{\sqrt{\mathrm{Var}\ S_n}}\leq z\right)
= \frac{1}{\sqrt{2\pi}} \int_{-\infty}^z e^{-x^2/2}dx
$$

This can be used to derive

$$
\lim_{n\to\infty} e^{-n} \sum_{k=0}^n \frac{n^k}{k!} = \frac{1}{2}
$$

Let $N\sim \text{Poisson}(n)$, then

$$
\Pr[N\leq n] = e^{-n} \sum_{k=0}^n \frac{n^k}{k!} 
$$

Note that $N = X_1 + X_2 + \cdots + X_n$, where $X_k\sim\text{Poisson(1)}$, apply CLT and we can get the result 

**Theorem**(WLLN: Weak Law of Large Number)
Let $X_1, \cdots, X_n$ be iid rv's with mean $\mu$ and finite variance $\sigma^2$, then for all $\varepsilon > 0$


$$
\lim_{n\to\infty} \Pr\left[\left|\frac{1}{n}\sum_{k=1}^n 
\left(X_k - \mu\right) \right|\right] = 0
$$







By Chebyshev we can show the probability is bounded by $\sigma^2/n\varepsilon^2$

**Theorem**(SLLN: Strong Law of Large Number)
Let $X_1, X_2, \cdots$ be iid rv's, $S_n = X_1 + \cdots + X_n$


$$
\Pr\left[\left\{\omega: \lim_{n\to\infty} \frac{S_n(\omega)}{n} = \mu \right\} \right]
$$


### Statistics

= probability reverse

Statistical problem

- a large group of objects called population
  
- study the behavior of a rv related
  
- population too large, have to draw samples
  

Random sample: a sample of size $n$ from the distribution $X$ is a collection of independent rv with the same distribution as $X$

**Def**(Statistic): is a rv that is a function of elements of a random sample.

**Def**: Let $X_1, \cdots, X_n$ be a random sample from $X$, the statistic $\sum X_i/n$ is called the sample mean, $\overline{X}$

- $\mu_X$ is the theoretical average value of $X$
  
- it is hoped that the observed $\overline{X}$ is close to $\mu_X$
  

The median for $X$ is the number $M$ s.t.

$$
\Pr[X < M] \leq 0.50\land \Pr[X\leq M] \geq 0.50
$$

The sample median is the middle observation if $n$ is odd, the avg of two middle observations if $n$ is even

**Def**: The sample variance is

$$
S^2 = \sum_{i=1}^n \frac{(X_i - \overline{X})^2}{n-1}
$$

roughly speaking, this is because accuracy + precision is conserved. We want

$$
\mathbb E[S^2] =\sigma^2
$$

Note that

$$
\begin{aligned}
\mathbb E[S^2] &=\mathbb E\left[ \sum_{i=1}^n \frac{(X_i - \overline{X})^2}{n-1}\right] \\
&= \frac{1}{n-1}\mathbb E\left[ \sum_{i=1}^n\left( (X_i - \mu)^2 +2\mu X_i - \mu^2 + 
\overline{X}^2 -2\overline{X}X_i\right)\right] \\
&= \frac{1}{n-1}\mathbb E\left[ \sum_{i=1}^n (X_i - \mu)^2 +2\mu n\overline{X}
-n\mu^2+n\overline{X}^2 -2n\overline{X}^2\right]\\
&= \frac{1}{n-1}\left(\mathbb E\left[ \sum_{i=1}^n (X_i - \mu)^2\right] -\mathbb E\left[n\left(
\overline{X} - \mu\right)^2\right]\right)
\end{aligned}
$$

Note that

$$
\mathbb E[(\overline{X} - \mu)^2] = \mathbb E\left[\left(\frac{\sum X_i-n\mu}{n}\right)^2\right]
= \frac{n\sigma^2}{n^2} = \frac{\sigma^2}{n}
$$

Hence

$$
\mathbb E[S^2] = \frac{1}{n-1}\left(n\sigma^2 - n\frac{\sigma^2}{n}\right) = \sigma^2
$$

computational formula

$$
S^2 = \frac{n\sum X_i^2 - (\sum X_i)^2}{n(n-1)}
$$

**Def**: Sample range is the defference between the largest and smallest observation.

Population mean and variance: not sample. variance divided by $n$.

### Estimation

A statistic used to estimate a population parameter $\theta$ is called a point estimator $\hat{\theta}$. Desired properties:

- unbiased ($\mathbb E[X] = \theta$)
  
- small variance
  

Example: the sample average is an unbiased estimator of $\mu$.

Proof:

$$
\mathbb E\left[\frac{1}{n}\sum_{i=1}^n X_i\right] = 
\frac{1}{n}\sum_{i=1}^n \mathbb E\left[ X_i\right] = \mu
$$

**Theorem**: $\overline{X} = \sigma^2/n$

Proof: Similar, variance is also linear for independent rv

**Def**: The standard deviation of $\overline{X}$ is $\sigma/\sqrt{n}$, called the standard error of the mean

**Theorem**: Let $S^2$ be sample variance based on a sample of size $n$, $S^2$ is an unbiased estimator for $\sigma^2$

(proved above)

Task: revover parameter of a given distribution from observations. and Maximum Likelihood.

An estimator of $M_k$ for $\mathbb E[X^k]$ is the sample average.

Method of Moments: in many cases, moments can be repressed as a function of $\theta$, get a reasonable estimator by replacing theoretical moments by estimators, and solve for $\theta$.


MLE(Maximum Likelihood Estimators): find the parameter that maximize the likelihood given the result.

Likelihood $\neq$ Probability.

Given a pdf or pmf $f(\cdot \mid \theta)$, the likelihood function is $f(x\mid\cdot)$, written as $L(\cdot)$

Procedure:
* Obtain random sample
* Define $L(\theta) = \prod f(x_i)$
* $\hat{\theta} = \argmax L(\theta)$

$s(\theta) = \frac{d}{d\theta}\log L(\theta)$ is sometimes called the score function. (use gradient for multiple parameters)

Interval Estimation

A $100(1-\alpha)\%$ confidence interval for a parameter $\theta$ is a random interval $[L_1, L_2]$ s.t.
$$
\Pr[L_1\leq \theta L_2] = 1- \alpha
$$


---
Unknown variance: replace $\sigma$ with $S$
$$
Z = \frac{\overline{X}-\mu}{S/\sqrt{n}}
$$

Let $Z\sim\mathcal{N}(0,1)$, $V\sim\chi_d^2$, independent, then
$$
T = \frac{Z}{\sqrt{V/d}}
$$
is said to follow a $T$-distribution. With $d$ degrees of freedom. 
$$
f(t) = \frac{\Gamma(\frac{d+1}{2})}{\Gamma(\frac{d}{2}\sqrt{\pi d})}\left(1+\frac{t^2}{d}\right)^{-\frac{d+1}{2}}
$$

Symmetric bell-shaped curve. Converges to standard normal distribution as $d$ increases. 
W.S.Gosset. Irish brewing. 

**Theorem**: Let $X_1, \cdots, X_n$ be random sample from a normal distribution, the rv
$$
\frac{\overline{X}-\mu}{S/\sqrt{n}}
$$
follows a $T$ distribution with $n-1$ degrees of freedom

* Fisher's Test of Significance
* Neyman-Pearson's Test of Acceptance
* Null Hypothesis Significance Testing (NHST)

Fisher
1. Select an appropriate test
2. Set up the null hypothesis $H_0: \theta \in \Theta_0$, some set for possible values of $\theta$. Say $\theta \leq \theta_0$. 
3. Calculate the theoretical probability of the results under $H_0$ ($p$-value, the probability of obtaining a real value at least as extreme as the one obtained). e.g. $p = \Pr[T\geq t\mid H_0]$ for one sided right-tail test-statistic distribution. 
4. Assess and interpret.

Level of significance (sig or $\alpha$): $H_0$ is rejected if $p\leq \alpha$. 

Pearson: 
1. Set up the expected effect size
2. Select an optimal test
3. Set up main/null hypothesis $H_M$ i.e. $H_0$
4. Set up the alternative/research hypothesis $H_A$ i.e. $H_1$. $H_0$ and $H_1$ should be disjoint.
5. Calculate the sample size $N$ required for good power $1-\beta$
6. Calculate the critical value of the test
7. Calculate the test value, and decide in favor of $H_0$ or $H_1$

Decision:
* fail within critical region: reject main hypo, accetp alternative
* fail outside critical region with good power: accept main hypo
* poor power: conclude nothing

Effect size (ES): the discrepancy between $H_0$ and $H_1$. 
* Type I error ($\alpha$): false positive, $H_0$ wrongly rejected 
* Type II error ($\beta$): false negative, $H_0$ is wrongly retained

Make $\beta$ as small as possible but not smaller than $\alpha$

A $100(1-\alpha)\%$ CI on $\mu$ is $\overline{X}\pm z_{\alpha/2}\sigma/\sqrt{n}$ where

$$
\Pr[Z\geq z_r] = r
$$

**Theorem**: Let $X_1, \cdots X_n$ be a random sample from a normal distri

The rv

$$
(n-1)S^2/\sigma^2 = \sum (X_i - \overline{X})^2/\sigma^2
$$

has a $\chi^2$-distrbibution with $n-1$ degrees of freedom (dof)

Facts

- $Z\sim \mathcal{N}(0,1)$, then $Z^2\sim\chi_1^2$ (1 dof)
  
- Sum of $n$ independent $\chi_1^2$ rv is a $\chi_n^2$ rv
  
- Cochran's theorem: given iid std normal rv, $\sum (Z_i -\overline{Z})^2\sim \chi_{n-1}$. Proof of this requires some linear algebra techniques.
  

**Theorem**: For $\sigma^2$, a $100(1-\alpha)\%$ is

$$
L_1 = (n-1)S^2/\chi_{n-1,\alpha/2}^2, \quad L_2 = (n-1)S^2/\chi_{n-1,1-\alpha/2}^2
$$

where $\chi_{n-1,\alpha/2}^2$ means the $z$ s.t. $\Pr[Z \geq z] =\alpha/2$

Note that the notation $\chi_{n, \alpha}^2$ is actually `ppf(n, 1-alpha)`

---

Power is the probability of correctly rejecting the null hypo. opposite of type II error, i.e. $1-\beta$.

This is not the same as Modus Tollens in logic.

> If a person is American, then he is probably not a member of Congress. A person is a member of Congress, then he is probably not an American.

Results in critical region (what is the critical region?)

- fisher: a rare event occurred OR $H_0$ is false
  
- Neyman-Pearson: $H_1$ explains better than $H_0$.
  
- NHST: depends on author
  

$T$-Test: unknown variance. reject at significance level $\alpha$ if

- $H_0: \mu = \mu_0$ if $|T_{n-1}|>t_{\alpha/2,n-1}$
  
- $H_0: \mu \leq \mu_0$ if $|T_{n-1}|>t_{\alpha,n-1}$
  
- $H_0: \mu \geq \mu_0$ if $|T_{n-1}|<-t_{\alpha,n-1}$
  

Test the variance: chi-squared test

$$
\chi_{n-1}^2 = \frac{(n-1)S^2}{\sigma_0^2}
$$

- $H_0: \sigma = \sigma_0$, $\chi_{n-1}^2 > \chi_{\alpha/2,n-1}^2$ or $\chi_{n-1}^2 < \chi_{1-\alpha/2,n-1}^2$
  
- $H_0: \sigma \leq \sigma_0$, $\chi_{n-1}^2 > \chi_{\alpha,n-1}^2$
  
- $H_0: \sigma \geq \sigma_0$, $\c

---

INSERT FROM another note

---

smith satterthwaite test
$$
\gamma = \frac{S_1^2/n_1 + S_2^2/n_2}{\frac{(S_1^2/n_1)^2}{n_1 - 1} + \frac{(S_2^2/n_2)^2}{n_2 - 1}}
$$
