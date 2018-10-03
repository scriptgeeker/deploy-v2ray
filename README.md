# Shadowsocks 一键部署脚本

## 适用环境

-   系统支持：CentOS 7
-   虚拟技术：KVM
-   内存要求：512M+

## 关于脚本

-   本脚本已在 Vultr 上的 VPS 测试通过，VPS 的虚拟方式为 KVM 架构
-   本脚本会自动安装 Python3（执行脚本） V2ray（代理服务） BBR（网络加速）
-   V2Ray 集成有 Shadowsocks 模块，脚本会自动配置 SS 参数，端口和密码随机生成
-   安装完成会重启系统，服务会自动启动，SS 订阅链接保存在 /root/v2ss.info 文件中

## 使用方法

root 用户执行

```shell
wget https://raw.githubusercontent.com/scriptgeeker/deploy-v2ray/master/v2ss.py && chmod +x v2ss.py && ./v2ss.py
```

查看订阅链接

```shell
cat /root/v2ss.info
```

## 服务状态

代理服务是否运行

```shell
systemctl status v2ray.service
```

防火墙是否关闭

```shell
systemctl status firewalld.service
```

网络加速是否开启

```shell
sysctl net.ipv4.tcp_congestion_control
```
