# V2ray Shadowsocks 一键部署脚本

## 适用环境

-   系统支持：CentOS 7
-   虚拟技术：KVM
-   内存要求：512M+

## 关于脚本

-   本脚本已在 Vultr 上的 VPS 测试通过
-   本脚本会自动安装 V2ray（代理服务） BBR（网络加速）
-   脚本运行后不需要任何操作，安装完成后会自动重启系统，服务自动开启

## 相关问题

> 问：为什么用 V2ray 部署 Shadowsocks 服务 ？

答：SS 使用的人多，客户端比较成熟，但服务端却很糟糕，甚至没有 v2 稳定性好。

> 问：SS 服务是怎么配置的，配置参数是什么？

答：端口和密码是随机的，加密方式为 aes-256-gcm，认证方式为 AEAD。

> 问：BBR 是什么，有什么用 ？

答：BBR 是谷歌开源的拥塞控制算法，可以使你的网速提升好几个数量级。

> 问：为什么会下载失败？

答：因为众所周知的原因，国内的宽带很不稳定，可以多试几次。

## 使用方法

安装 wget 下载工具
```bash
yum install -y wget
```

下载执行一键部署脚本
```bash
wget https://raw.githubusercontent.com/scriptgeeker/deploy-v2ray/master/v2ss.py && sudo python v2ss.py
```

查看服务端配置

```bash
cat /etc/v2ray/config.json
```

查看客户端配置
```bash
cat /etc/v2ray/client.json
```

查看SS订阅链接

```bash
cat /etc/v2ray/sslink.info
```

## 服务状态

服务运行状态

```bash
systemctl status v2ray.service
```

防火墙开放端口

```bash
firewall-cmd--zone=public --list-ports
```

网络控制器内核
```bash
sysctl net.ipv4.tcp_congestion_control
```
