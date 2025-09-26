---
title: '数据结构: Loser Tree/Tournament Tree'
date: 2025-09-26 14:20:12
categories: 
  - dev
  - algorithm
---

在对磁盘中数据进行排序的时候，external sort是一个非常著名的算法。简单来说就是扩展版的merge sort。
那么我们在merge $k$个block的时候，首先想到的自然是用一个Priority Queue，这样的确可以提高效率，不过在这个情景下，还存在一个更有趣的数据结构，即本篇的主题
Loser Tree(Tournament Tree)。

他的结构是这样的，比如我们有4个已经排序好的block要进行合并(每个竖排是一个排序好的block)
```
A    B    C    D
3    1    2    6
4    5    5    7
6    9    8    10
```

那么我们可以往上构建两层像index一样的结构。我们把比较的过程看成比赛(tournament)，这就像我现在小组(block)里面比赛完，然后选出优胜的，再和别的组去比。
```
         ?
         |
         ?
    /        \
   ?          ?
 /   \      /   \
3     1    2     6
A     B    C     D
3<-   1<-  2<-   6<-
4     5    5     7
6     9    8     10
```

然后，两两之间比较，输的一方(也就是数值更小的一方)*晋级上一层*，赢的一方(数值大的一方)*留在原地*。
```
         ?
         |
       1 vs 2
    /        \
   3          6
 /   \      /   \
3     1    2     6
A     B    C     D
3<-   1<-  2<-   6<-
4     5    5     7
6     9    8     10

         1
         |
         2
    /        \
   3          6
 /   \      /   \
3     1    2     6
A     B    C     D
3<-   1<-  2<-   6<-
4     5    5     7
6     9    8     10
```

那么，我们要获取最小值，直接取得最顶上的元素即可。而后我们可以移动对应的block中的元素位置，进行一次更新
```
         ?
         |
         2 
    /        \
   3          6
 /   \      /   \
3     5<-  2     6
A     B    C     D
3<-   1    2<-   6<-
4     5<-  5     7
6     9    8     10
```

接下来只要一直和父结点比较即可。整体的流程和binary heap还是非常相似的。调教了一下claude做了个[简单的动画](./loser-tree-anim.html)。也可以在下面直接观看。

<iframe src="./loser-tree-anim.html" width="800" height="650" style="border:1px solid #ccc;"></iframe>

那么，Loser Tree对比普通的binary heap有什么好处呢？

其实最主要的就是，减少了一半的比较次数。对于loser tree，上升的方向是确定的，每次只需要和父亲比较；而对于binary heap，需要与左孩子和右孩子分别比较，因此会多出一倍的比较次数。同时，上升路径的确定在代码执行层面降低了CPU分支预测出错的概率，根据下面引用的大佬的实测这的确可以带来可观的提升。
(本来想自己写代码测一测的，但有点懒，以后有空再说吧~)


References:
* https://www.ahl27.com/posts/2024/12/loser-trees-io/