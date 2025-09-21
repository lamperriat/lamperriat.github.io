---
title: C++的lambda重载与std::variant
date: 2025-09-21 16:33:11
tags: 
  - dev
  - cpp
---

这两天在做学校中数据库的project，使用`std::variant`的时候总觉得一堆if-else的写法非常不优雅，于是在stackoverflow上找到了[这篇帖子](https://stackoverflow.com/questions/78948483/runtime-type-info-for-accessing-stdvariant-data)，看到这个重载lambda的写法实属精妙至极。

先直接来看最终代码(C++20)

```cpp
template<class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };

using FieldValue = std::variant<int, float, std::string, bool>;

std::vector<std::byte> Record::serialize() const {
    std::vector<std::byte> data;
    for (const auto &field : values_) {
		std::visit(overloaded{
		    [&data](int value) {},
		    [&data](float value) {},
		    [&data](const std::string &value) {},
		    [&data](bool value) {}
        }, field);
    }
};
```

这种用法下编译器会做exhaustive check，即必须每个数据类型都被cover到。检查的原理是，在展开完代码后，`std::visit(__callable, value)`，对每个数据类型尝试调用`__callable(value)`来查看是否合法。

现在来看下`overloaded`使用了什么神奇的魔法吧。

首先我们知道在编译期lambda会被重写成一个唯一的类，类似于
```cpp
// before
auto f = [](int i) -> int {...};
// after
struct __SomeUniqueNameF {
    int operator()(int i) const {...};
};
```

在构建`overloaded{...}`的时候，得益于C++17加入的[Class Template Argument Deduction (CTAD)](https://en.cppreference.com/w/cpp/language/class_template_argument_deduction.html)特性，我们不需要手动写一个helper函数

```cpp
// no need after C++17
template <class... Ts>
overloaded<Ts...> make_overloaded(Ts... ts) {
    return overloaded<Ts...>{ts...};
}
```

那么，编译器会自动推断模版参数，我们的模版会被展开为
```cpp
struct overloaded : LambdaType1, LambdaType2, ... {
    // using Ts::operator()...; will be expanded to
    using LambdaType1::operator();
    using LambdaType2::operator();
    ...
};
```

因此，在`overloaded`这个struct中会包含所有我们定义的lambda，每个lambda的`operator()`都存在于这个新的struct中，完成了重载的工作。