---
title: WireguardVPN简单搭建指南
date: 2025-09-02 23:00:42
categories: 
    - dev
    - tools
---

### 前言
作为海外留子，各类音乐和视频软件中部分资源会限制境外IP的访问(版权原因)。那么这时候VPN/代理就非常必要了。那么作为开发者，与其每个月花几十块用别人搭建的，不如自己上手搭！

笔者直接搭建在了99一年租的阿里云服务器上。自然，这99块钱也不是必须的。如果您家里有公网IP(电信的话直接打电话即可申请)，也可以直接部署在自己家的电脑上。虽然笔者家里已经搭建了服务器，不过因为需要修改各种防火墙，不在家的话不太好改，因此暂时没有实验。

### 实操
环境: Ubuntu 24.04.1 LTS

首先安装Wireguard
```bash
sudo apt update
sudo apt install wireguard -y
```
我的版本: 
```bash
$ wg --version
wireguard-tools v1.0.20210914 - https://git.zx2c4.com/wireguard-tools/
```

开启ipv4和ipv6(可选)的forwarding，当然要保存到sysctl中，不然下次启动就失效了～
```bash
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.conf
```

创建一个目录放，`cd`进去生成密钥。`umask 077`是为了安全考虑设置权限，如果服务器就自己一个人用其实无所谓。
```bash
umask 077
wg genkey | tee server_private.key | wg pubkey > server_public.key
wg genkey | tee client_private.key | wg pubkey > client_public.key
```

可以用`cat`指令查看密钥内容，接下来的配置文件中会用到。

修改配置文件`/etc/wireguard/wg0.conf:`
```conf
[Interface]
PrivateKey = <你的server_private.key>
Address = 10.0.0.1/24
ListenPort = <选一个端口，如果开了防火墙，记得给这个端口的UDP放行>

# 下面这一长串玩意是gemini写的，解决了我iptables中有神秘的docker chain把包全扔了的问题
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE

[Peer]
PublicKey = <你的client_public.key>
AllowedIPs = 10.0.0.2/32
```

防火墙方面，注意Wireguard走的是UDP！Wireguard在UDP的基础上自己实现了上层协议。

服务器这边的设置就都完成啦，启动服务！
```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

---

接下来是客户端。首先去官方安装[Wireguard](https://www.wireguard.com/)的客户端，mac/IOS直接appstore下载即可。

客户端的配置文件，随便放在哪里都可以，进入wireguard APP后可以点import from file然后选择这个文件就行。
```conf
[Interface]
PrivateKey = <你的client_private.key>
Address = 10.0.0.2/24
DNS = 8.8.8.8 # 这是google的dns服务器，也可以不加或者用别的

[Peer]
PublicKey = <你的server_public.key>
Endpoint = <你的服务器ip>:<你选择的端口>
AllowedIPs = 0.0.0.0/0, ::/0 # 设置允许经过vpn的流量，默认全部
```

Import完就可以连接了 :tada:

实测阿里云的3M小水管平时基本还是够用的，虽然b站和wyy的搜索页面有时候会卡一下，但整体足够日常使用了。