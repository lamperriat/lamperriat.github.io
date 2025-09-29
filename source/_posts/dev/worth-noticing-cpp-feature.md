---
title: C++的一些(可能没什么用的)特性(长期更新)
date: 2025-09-29 20:54:45
categories:
  - dev
  - cpp
---

### 关于nested class
在C++中，nested class被认为是一个member，因此自然地享有对所有member，包括private和protected member的访问权限。

```cpp
class Tree {
private:
    int private_data_ = 42; 
public:
    struct Node {
        void accessOuterMember(Tree& outer_tree) {
            outer_tree.private_data_ = 100; // OK
        }
    };
};
```

虽然这个feature看起来十分自然，但实际上如果设计成内部的class hold一个外部class的reference的话，这个feature就完全不成立了。