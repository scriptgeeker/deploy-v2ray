#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
V2ray-SS 一键部署脚本
'''

# -------------- 全局配置 ----------------- #

# 安装 Python 3.7
GET_PY_37 = [
    'yum -y install wget gcc make',
    'yum -y install bzip2-devel ncurses-devel sqlite-devel gdbm-devel xz-devel tk-devel readline-devel libffi-devel',
    'wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz && tar -zxvf Python-3.7.0.tgz',
    'cd Python-3.7.0 && ./configure prefix=/usr/local/python3 && make && make install',
    'ln -s /usr/local/python3/bin/python3.7 /usr/local/bin/python',
]

# 安装 V2ray x64
GET_V2_X64 = [
    'wget https://install.direct/go.sh',
    'sudo chmod +x go.sh && ./go.sh',
]

# 安装 BBR TCP
GET_BBR_TCP = [
    'rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org',
    'rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-3.el7.elrepo.noarch.rpm',
    'yum -y --enablerepo=elrepo-kernel install kernel-ml',
    'sudo grub2-set-default 0',
    'yum -y remove kernel kernel-tools',
]

# 客户端 SS 配置
CLIENT_CONFIG = {
    "inbound": {"port": 1080, "protocol": "socks", "domainOverride": ["tls", "http"], "settings": {"auth": "noauth"}},
    "outbound": {"protocol": "shadowsocks", "settings": {"servers": []}}
}

# 服务端 SS 配置
SERVER_CONFIG = {
    "inbound": {"protocol": "shadowsocks", "settings": {}},
    "outbound": {"protocol": "freedom", "settings": {}}
}

# -------------- Python 3 环境 ----------------- #

import os
import platform
import subprocess

EXEC_FILE = os.path.abspath(__file__)

# 判断 python 版本
if platform.python_version()[0] == '2':
    os.chdir('/tmp')
    for cmd in GET_PY_37:
        subprocess.call(cmd, shell=True)
    subprocess.call(EXEC_FILE, shell=True)
    exit()

# -------------- 安装配置 V2ray ----------------- #

import re
import json
import random
import string
import base64


# 随机字符串
def random_string(size=8, chars=string.ascii_letters):
    randstr = ''
    for i in range(size):
        randstr += random.choice(chars)
    return randstr

# 获取IP地址
def get_ip_addr(pattern):
    ip_info = os.popen('ip addr').read()
    return re.findall(pattern, ip_info)[0]


# 安装 V2ray
os.chdir('/tmp')
for cmd in GET_V2_X64:
    subprocess.call(cmd, shell=True)

# V2ray SS 配置
ss_config = {
    'server_addr': get_ip_addr(r'inet ([0-9\.]+)\/\d+ brd'),
    'server_port': random.randint(6000, 9000),
    'password': random_string(size=16),
    'method': 'aes-256-gcm',
}

SERVER_CONFIG['inbound']['port'] = ss_config['server_port']
SERVER_CONFIG['inbound']['settings']['method'] = ss_config['method']
SERVER_CONFIG['inbound']['settings']['password'] = ss_config['password']

# 写入配置文件
with open('/etc/v2ray/config.json', 'w') as fw:
    fw.write(json.dumps(SERVER_CONFIG, sort_keys=True, indent=4))

# -------------- 保存客户端配置信息 ----------------- #

CLIENT_CONFIG['outbound']['settings']['servers'].append({
    "address": ss_config['server_addr'],
    "password": ss_config['password'],
    "port": ss_config['server_port'],
    "method": ss_config['method'],
})

ss_info = json.dumps(CLIENT_CONFIG, sort_keys=True, indent=4)
ss_rule = '{method}:{password}@{server_addr}:{server_port}'
ss_link = 'ss://' + base64.b64encode(ss_rule.format(**ss_config).encode()).decode()

with open('/root/v2ss.info', 'w') as fw:
    fw.write('# -------------- config.json ----------------- #\n')
    fw.write(ss_info + '\n' * 3)
    fw.write('# -------------- shadowsocks ----------------- #\n')
    fw.write(ss_link + '\n' * 3)

# -------------- 安装 BBR 加速 ----------------- #

# 开机启动 V2ray
subprocess.call('sudo systemctl enable v2ray.service', shell=True)

# 关闭系统防火墙
subprocess.call('sudo systemctl disable firewalld.service', shell=True)

os.chdir('/tmp')
for cmd in GET_BBR_TCP:
    subprocess.call(cmd, shell=True)

with open('/etc/sysctl.conf', 'a') as fa:
    fa.write('\n' + 'net.core.default_qdisc = fq')
    fa.write('\n' + 'net.ipv4.tcp_congestion_control = bbr')

# 重启服务器
subprocess.call('sudo shutdown -r now', shell=True)
