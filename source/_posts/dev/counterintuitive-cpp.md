---
title: 反直觉的C++
date: 2025-09-24 12:12:58
categories:
  - dev
  - cpp
---

cpp中存在许多乍一看不太符合直觉的特性，或者说，坑，因此为了防止未来的自己踩坑，在此列举一些。(注: 笔者并不精通cpp，可能存在错误)

### std::copy vs vector::insert

`std::copy`是一个怎么看都和`memcpy`挂钩的函数，听名字就很快啊，但事实真是如此吗？

首先上benchmark，测试在vector末尾进行`insert`
```cpp
void benchmark_insert(size_t chunk_size, size_t total_size) {
    std::vector<std::byte> source_data(chunk_size);
    std::vector<std::byte> out_data;
    // out_data.reserve(total_size);
    const size_t iterations = total_size / chunk_size;
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < iterations; ++i) {
        out_data.insert(out_data.end(), source_data.data(), source_data.data() + source_data.size());
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;
    std::cout << "vector::insert: " << std::fixed << std::setprecision(3) << elapsed.count() << " ms\n";
}

void benchmark_copy(size_t chunk_size, size_t total_size) {
    std::vector<std::byte> source_data(chunk_size);
    std::vector<std::byte> out_data;
    // out_data.reserve(total_size);
    const size_t iterations = total_size / chunk_size;
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < iterations; ++i) {
        std::copy(source_data.begin(), source_data.end(), std::back_inserter(out_data));
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;
    std::cout << "std::copy:      " << std::fixed << std::setprecision(3) << elapsed.count() << " ms\n";
}
```

测试环境
* Ubuntu Server 22.04
* x86-64

另外也在我本地的macOS上测试了一下

编译器版本
* Ubuntu clang version 18.1.3
* g++ (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0

标准C++20，O2优化

是否提前`reserve`都测试一下，结果如下

<table>
  <thead>
    <tr>
      <th>Compiler</th>
      <th>Reserve</th>
      <th>Chunk Size</th>
      <th>vector::insert (ms)</th>
      <th>std::copy (ms)</th>
    </tr>
  </thead>
  <tbody>
    <!-- clang -->
    <tr>
      <td rowspan="4">clang</td>
      <td rowspan="2">Yes</td>
      <td>16B</td>
      <td>173.282</td>
      <td>191.463</td>
    </tr>
    <tr>
      <td>4096B</td>
      <td>111.118</td>
      <td>186.165</td>
    </tr>
    <tr>
      <td rowspan="2">No</td>
      <td>16B</td>
      <td>374.504</td>
      <td>388.985</td>
    </tr>
    <tr>
      <td>4096B</td>
      <td>312.785</td>
      <td>408.664</td>
    </tr>
    <!-- g++ -->
    <tr>
      <td rowspan="4">g++</td>
      <td rowspan="2">Yes</td>
      <td>16B</td>
      <td>128.869</td>
      <td>272.869</td>
    </tr>
    <tr>
      <td>4096B</td>
      <td>108.652</td>
      <td>281.220</td>
    </tr>
    <tr>
      <td rowspan="2">No</td>
      <td>16B</td>
      <td>343.335</td>
      <td>480.225</td>
    </tr>
    <tr>
      <td>4096B</td>
      <td>309.249</td>
      <td>483.180</td>
    </tr>
    <!-- clang++ macOS -->
    <tr>
      <td rowspan="4">clang++ (macOS)</td>
      <td rowspan="2">Yes</td>
      <td>16B</td>
      <td>68.276</td>
      <td>357.153</td>
    </tr>
    <tr>
      <td>4096B</td>
      <td>8.853</td>
      <td>375.198</td>
    </tr>
    <tr>
      <td rowspan="2">No</td>
      <td>16B</td>
      <td>103.593</td>
      <td>377.530</td>
    </tr>
    <tr>
      <td>4096B</td>
      <td>25.889</td>
      <td>391.102</td>
    </tr>
  </tbody>
</table>


实际上，虽然说所有benchmark中都是`insert`更快，但这个差距的变化实在太大了。对该问题做出完善的解释已经超出了我的能力范围，非常抱歉。期待有大佬来解析一下。

基本猜想是，mac上差距很大是因为某些优化的失效，而`copy`更慢大概率是内存分配上的原因。

TODO: perf一下，顺便与deepwiki再聊一下，看看llvm的实现。