---
title: '[Crypto] SPAKE2'
date: 2026-07-21 17:09:08
categories:
- dev
- crypto
---

本文将介绍一个很有意思的协议/算法 RFC9382: SPAKE2, a Password-Authenticated Key Exchange
该协议的目的非常简单。Alice和Bob都有一个相同的short token(或者说，password)，他们希望能从这个short token来认证对方，并获得一个强密钥，进而两人可以安全地加密通信。

相关的应用中，最常见的应该是文件传输类的。双方用一个临时的short token去进行pairing，而后获得一个安全的长密钥去传输文件。

注: 本文中默认所有的group都是基于Elliptic Curve的。这也是目前大部分实现所选用的方案。但算法本身对我们底层用什么group并没有要求。

### Motivation
学过密码学的朋友们应该对Diffie Hellman Key Exchange非常熟悉。这是一个非常知名的基于离散对数问题(discrete logarithm problem, DLP)的key exchange算法。简单来说

* $G$是一个群，它的order是$p$
* $\alpha$是$G$的一个generator

Alice生成一个随机数$x$，计算$\alpha^x$，发送给Bob。
Bob生成一个随机数$y$，计算$\alpha^y$，发送给Alice。
此时，Alice有$\alpha^y$和$x$，可以计算$\alpha^{xy}$
Bob有$\alpha^x$和$y$，也可以计算$\alpha^{xy}$

而假设中间人Evil试图攻击，他只能看到$\alpha^x$和$\alpha^y$，无法获得两人的shared secret $\alpha^{xy}$

当然，上述只是一个数学上的简单化后的描述。Diffie Hellman本身并不涉及对于identity的鉴别(很显然的，整个setup都没有和identity有关的东西)，Evil可以伪装成Alice和Bob进行key exchange。

Remark: 在这里我们简化对于DLP, CDH(computational Diffie-hellman), DDH(decisional Diffie-hellman), GDH(gap Diffie-hellman)的说明。对于该算法，底层应该选用满足GDH的群。关于CDH和DDH的介绍在大部分入门教材中都有。GDH指的就是DDH简单而CDH很难，即"难以直接计算结果，但可以简单确认结果是否正确"的群

### SPAKE2
基本的setup如下：
* $G$是一个群。一般来说是基于EC的一个大群
* $G'$是$G$的一个子群。$|G'|$是质数
* $P$是$G'$的一个generator
* $h$是$G'$的cofactor，即
$$
h = \frac{|G|}{|G'|}
$$

* $M, N\in G'$是**公开的**、固定的点
* $\mathcal O$是identity element，即曲线上无穷远处的点
* $w = \text{MHF}(token)\mod p$是双方共享的short token/password的安全哈希值(MHF: memory-hard password hashing function)

关于记号：我们用大写字母$P,M,N$表示$G'$中的元素，是因为一般而言$G$是基于elliptic curve的，所以这些元素都是曲线上的点。
另外，为了视觉上更清晰，我们将
$$
xP = P + P + \cdots + P
$$

写成$[x]P$，表明前面的$x$是scalar而后面的$P$是EC上的点。

核心步骤:
类似于Diffie Hellman，Alice选取一个随机数$x$，计算
$$
P_A = [x]P + [w]M
$$

把$P_A$发送给Bob。类似地，Bob选取一个随机数$y$，计算
$$
P_B = [y]P + [w]N
$$

把$P_B$发送给Alice。
然后，Alice根据Bob发送来的$P_B$，可以计算出
$$
P_B - [w]N = [y]P
$$

而Alice知道自己的随机数$x$，因此可以计算出$[xy]P$。
类似地，Bob根据Alice发送来的$P_A$，可以计算出
$$
P_A - [w]M = [x]P
$$

Bob知道自己的随机数$y$，因此也可以计算出$[xy]P$。

考虑cofactor，我们需要额外乘以$h$来保证无效输入最终会得到全0输出。关于这一点，我们稍后会详细说明。
总之，如果双方password相同，Alice会获得
$$
K_A = [hx](P_B - [w]N) = [hxy]P
$$

Bob会获得
$$
K_B = [hy](P_A - [w]M) = [hxy]P
$$

Remark: 在这个过程中，由于password被随机数mask了(比如，Alice计算的$[w]M$加上了随机生成的$[x]P$)，即使Evil截取了信息，也没有办法获得任何和password有关的信息。

上述过程中，只要两人用的password相同，就会获得相同的key。
那么现在假设Evil使用错误的password试图和Alice通信，即Alice使用$w=w_A$而Evil使用$w=w_B\neq w_A$。此时
$$
\begin{aligned}
K_A &= [hx](P_B - [w_A]N) = [hx]([y]P + [w_B]N - [w_A]N) \\
&= [hxy]P + [hx(w_B-w_A)]N
\end{aligned}
$$

类似地，
$$
K_B = [hxy]P + [hy(w_A - w_B)]M
$$

两者不会相等。(相等条件为$xN + yM=0\mod p$，概率约为$1/p$，在密码学上可忽略)

因此，接下来需要做两件事情
* Alice和Bob都要确认对方获得了和自己相同的key
* 通过一个KDF(key derivation function)来获得一个强密钥用于加密通话(session key)

Remark: 为什么不直接使用$K = K_A = K_B$来加密通话？
$K$本身只包含随机数、password等信息，而不包含其他信息，比如拿到这个密钥的context，比如identity, $P_A$, $P_B$. 我们希望确保两边对于所有的context都完全agree

双方计算transcript:
$$
\begin{aligned}
TT =& \text{len}(A)\ ||\ A\ || \\
&\text{len}(B)\ ||\ B\ || \\
&\text{len}(P_A)\ ||\ P_A\ || \\
&\text{len}(P_B)\ ||\ P_B\ || \\
&\text{len}(K)\ ||\ K\ || \\
&\text{len}(w)\ ||\ w
\end{aligned}
$$

Remark: Transcript中为什么需要加上长度信息？
如果没有长度，那么$\texttt{"ab"}\ ||\ \texttt{"c"}$ 和 $\texttt{"a"}\ ||\ \texttt{"bc"}$ 是相等的。这显然不合理。

这里的$A$和$B$是public的，Alice和Bob的identity。

Remark: 这个identity可以有很多种形式。比如说，可以是双方注册的email，可以是device-specific的一串string，可以是基于public key的identity，也可以是在一个app中，简单用"app-role-A"和"app-role-B"或者空的identity。空的identity只有在被authenticate的人没有任何ambiguity的情况下可以用。


然后我们计算$TT$的哈希，并分成长度相同的两份
$$
K_e\ ||\ K_a = \text{hash}(TT)
$$

比如，如果我们使用sha256，则$|K_e|=|K_a|=128$。
这里
* $K_e$是session key，也就是双方确认成功后，最终会用来加密会话的key。或者说是SPAKE2的输出密钥，对于具体的应用，可能在该密钥基础上进行其他操作获得最终密钥。
* $K_a$会被用来derive confirmation keys，用来确认对方获得了和自己相同的密钥

对于$K_a$，具体来说，Alice和Bob会同时计算一个KDF(key derivation function)，然后依然将结果分为相等长度的两份
$$
K_{cA}\ ||\ K_{cB} = \text{KDF}(K_a,\text{nil},\texttt{"ConfirmationKeys"}\ ||\ AAD,L)
$$

其中
* 用什么KDF由ciphersuite或上层协议统一规定
* $\text{nil}$是salt，默认为空
* AAD可以附加的数据(additional associated data)
* $L$是希望输出的长度

两人计算的结果相同，Alice用前半部分作为key，计算MAC(message authentication code)，发送给Bob，Bob用相同的key来verify。Bob则用后半部分计算MAC。具体来说
Alice计算 $c_A = \text{MAC}(K_{cA}, TT)$，发送给Bob。Bob计算确认获得的 $c_A$ 和自己计算出的 $\text{MAC}(K_{cA},TT)$ 相等。
类似地，Bob计算 $c_B = \text{MAC}(K_{cB}, TT)$，发送给Alice。Alice计算确认获得的 $c_B$ 和自己计算出的相等。

在双方都confirm对方获得的key和自己相同之后，便可以用session key开始加密通信了。

### Security 

现在来稍微介绍一下一些security相关的设计。

处理cofactor: 在ECC(elliptic curve cryptography)中，我们并不是直接用一个大的prime order group主要出于计算复杂性的考量。有些曲线虽然有大于1的cofactor，但计算方便，而一个比较小的cofactor，只要设计合理，对安全性并没有太大影响。

*注意*: 以下是对于cofactor处理的广义讨论，并不是RFC中对SPAKE2的设计

对于一个EC上的离散对数问题，假设我们的secret是$s$。假设group $G$的order是$hp$，$p$是质数而$h$是cofactor。那么潜在的风险是，曲线上存在一些点的order是$h$。对于attacker，他可以选择点$T$，$\text{ord}(T) = h$，如果我们的算法将其作为合法输入，那么部分信息会被暴露: 由于$h$很小，如果我们把$sT$发给attacker，那么attacker可以直接穷举获得$s\mod h$的值。但这本身其实只会暴露很少的信息。比如$h=8$的话，相当于只会暴露3bit的信息。

这个的解决方法之一就是直接乘以$h$。这样的话，如果输入是一个order为$h$的点，就会直接退化为$\mathcal O$，即单位元。我们只需要直接拒绝单位元输入就可以了。

相比起这个，更加危险的其实是非法的输入，比如不在曲线上的点。这些输入需要算法更精细地处理，比如确保所有非法输入都会获得全0输出等。不然的话，如果attacker可以反复实验各种非法输入，最终有可能可以通过CRT(Chinese Remainder Theorem)来恢复我们的secret。

$M$和$N$的选取: 值得注意的是，如果$M=[m]P$和$N=[n]P$的$m,n$被Evil知道了，那么这个setup的安全性会被降低。在RFC 9382的文档中，推荐使用RFC 9380: Hashing to Elliptic Curves 来获取$M,N$，保证所有人都可以确认没有人知道$M$和$N$的离散对数结果。
作为hash的输入，可以选用一个固定的string，也可以用A和B的identity。而$M$和$N$既可以相等(即算法的symmetric variant)，也可以不相等。

### Summary
SPAKE2的核心思想就是，让attacker不能offline attack我们的弱密钥。这和现在常用的email OTP或短信OTP在使用体验上其实很相似。密钥本身是不强的，但attacker只能线上进行尝试，每次尝试都有很大的代价(即 受到rate limiter或其他限制的影响)，变相增强了安全性。

已经存在P2P的文件传输应用采用SPAKE2或其他类似的算法/协议。作为用户，我们只需要在两台设备上同时输入一个短密钥，就可以用获得的强密钥去加密文件的传输，非常方便。