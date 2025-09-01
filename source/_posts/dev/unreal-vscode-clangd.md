---
title: 使用VSCode和clangd进行虚幻引擎开发(UE5.4适用)
date: 2025-09-01 10:44:57
tags:
---


### 教程
实际上网上能找到的相关教程很少，因为一般来说希望用clangd就得下UE的源码，然后手动编译，手动配vscode，非常麻烦。但[boocs](https://github.com/boocs/)感谢写的插件[unreal clangd](https://github.com/boocs/unreal-clangd)，以上操作都变得十分简单。

视频教程: https://b23.tv/5gm84vH

由于视频教程本身已经非常详细，这里就不再重复。

使用clangd的好处
* 相比VS和IDEA明显更加轻便，功能上没有明显缺失
* 相比IDEA，虽然补全速度会稍慢，但内存占用显著降低

安装后的使用
* 首先在ue中更改代码编辑器为VSCode，而后生成Code project
* 打开VSCode，ctrl/cmd+shift+p后输入`unreal clangd`，然后点Create Unreal clangd project
* 接下来一直确认下去就行，等最后插件会重启vscode，然后打开`completionHelper.cpp`，此时clangd就应该开始indexing了

注意事项
* 遇到消不掉的红线大概率是需要重新编译(比如`.generated.h`文件需要更新之类的)，如果红线没什么大碍也可以写完再编
* 如果你怀疑插件是不是出bug了，请先重新编译，这能解决99%的问题。剩下1%需要重新走一遍删中间文件+重新生成project的过程
* 重新编译完后，如果还有红线，可以试试把include全删了再贴回来，让clangd重新parse一遍header，有时候不需要重新编译就能解决，或者直接重启vscode


*Happy Coding in VSCode!*

