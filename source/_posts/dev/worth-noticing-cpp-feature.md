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

### 一个神秘的UB
在写project的时候，本地(macOS)编译器从clang16升级到clang18后会出现一个UB:
```cpp
const std::span<const std::byte> &data
...
auto ptr = reinterpret_cast<std::byte*>(&value);
std::copy(data.begin() + offset, data.begin() + offset + sizeof(int), ptr);
values_.push_back(value);
```

如果不用debugger真的很难定位到
```
(lldb) bt
* thread #1, queue = 'com.apple.main-thread', stop reason = Function type mismatch
  * frame #0: 0x00000001011e958c libclang_rt.asan_osx_dynamic.dylib`__ubsan_on_report
    frame #1: 0x00000001011e956c libclang_rt.asan_osx_dynamic.dylib`__ubsan::UndefinedBehaviorReport::UndefinedBehaviorReport(char const*, __ubsan::Location&, __sanitizer::InternalScopedString&) + 168
    frame #2: 0x00000001011e51dc libclang_rt.asan_osx_dynamic.dylib`__ubsan::Diag::~Diag() + 240
    frame #3: 0x00000001011e93ec libclang_rt.asan_osx_dynamic.dylib`handleFunctionTypeMismatch(__ubsan::FunctionTypeMismatchData*, unsigned long, __ubsan::ReportOptions) + 260
    frame #4: 0x00000001011e94c0 libclang_rt.asan_osx_dynamic.dylib`__ubsan_handle_function_type_mismatch_abort + 36
    ...
    frame #21: 0x00000001002eb420 SC3020-P1DB_benchmarks`Record::deserialize(this=0x0000603000003f10, data=size=72, schema=size=3) at Record.cpp:144:12
```

以上代码修改成下面这样后，UB消失了。实际上我也没搞懂为什么上面的代码会UB，ai说`std::copy`不能处理未对齐的内存，总之既然如此以后还是直接用`memcpy`为好。
```cpp
std::memcpy(&value, data.data() + offset, sizeof(int));
values_.emplace_back(value);
offset += sizeof(int);
```

## Unreal CPP
以下为Unreal cpp相关

### 指针的初始化
在旧版本中，只要指针成员带有`UPROPERTY()`这个macro，就会自动初始化为`nullptr`。在新版本用最好直接用`TObjectPtr`这个wrapper而不是裸指针
```cpp
// old
UPROPERTY()
AActor* MyActor;

// new
UPROPERTY()
TObjectPtr<AActor> MyActor;
```

`TObjectPtr`同样也可以手动赋值`nullptr`初始化，这样代码看起来更清晰，这是一个good practice。
注意UE的GC依赖于`UPROPERTY`这个macro，一般对于`TObjectPtr`都要加上`UPROPERTY()`。