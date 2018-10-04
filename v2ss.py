#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Auto deploy V2ray shadowsocks
# System Required:  CentOS 7 X64
# Both PY2 and PY3 can run this script.

import os
import re
import json
import random
import string
import base64
import subprocess

# -------------- Global config ----------------- #

# install V2ray
GET_V2RAY = [
    "rm -rf $(find / -name 'v2ray')",
    "yum -y install zip unzip",
    "wget https://github.com/v2ray/v2ray-core/releases/download/v3.45/v2ray-linux-64.zip",
    "unzip v2ray-linux-64.zip",
    "mv './v2ray-v3.45-linux-64' '/usr/bin/v2ray'",
    "cp '/usr/bin/v2ray/systemd/v2ray.service' '/etc/systemd/system/'",
    "ln -s '/etc/systemd/system/v2ray.service' '/etc/systemd/system/multi-user.target.wants/v2ray.service'",
    "mkdir -p /etc/v2ray",
    "cp '/usr/bin/v2ray/vpoint_socks_vmess.json' '/etc/v2ray/config.json'",
    "systemctl enable v2ray.service",
]

GET_BBR = [
    "cat '/etc/redhat-release'",
    "rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org",
    "rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm",
    "yum --enablerepo=elrepo-kernel -y install kernel-ml",
    "grub2-set-default 0",
    "yum -y remove kernel kernel-tools",
    "echo 'net.core.default_qdisc = fq' >> '/etc/sysctl.conf'",
    "echo 'net.ipv4.tcp_congestion_control = bbr' >> '/etc/sysctl.conf'",
    "sysctl -p",
]

# client SS config
CLIENT_CONFIG = {
    "inbound": {"port": 1080, "protocol": "socks", "domainOverride": ["tls", "http"], "settings": {"auth": "noauth"}},
    "outbound": {"protocol": "shadowsocks", "settings": {"servers": []}}
}

# server SS config
SERVER_CONFIG = {
    "inbound": {"protocol": "shadowsocks", "settings": {}},
    "outbound": {"protocol": "freedom", "settings": {}}
}


# -------------- install and config V2ray ----------------- #

def exec_shell(cmds):
    for cmd in cmds:
        subprocess.call(cmd, shell=True)


def random_string(size=8, chars=string.ascii_letters):
    randstr = ''
    for i in range(size):
        randstr += random.choice(chars)
    return randstr


def get_ip_addr(pattern):
    ip_info = os.popen('ip addr').read()
    return re.findall(pattern, ip_info)[0]


os.chdir('/tmp')
exec_shell(GET_V2RAY)

ss_config = {
    'server_addr': get_ip_addr(r'inet ([0-9\.]+)\/\d+ brd'),
    'server_port': random.randint(6000, 9000),
    'password': random_string(size=16),
    'method': 'aes-256-gcm',
}

SERVER_CONFIG['inbound']['port'] = ss_config['server_port']
SERVER_CONFIG['inbound']['settings']['method'] = ss_config['method']
SERVER_CONFIG['inbound']['settings']['password'] = ss_config['password']

ss_info = json.dumps(SERVER_CONFIG, sort_keys=True, indent=4)

with open('/etc/v2ray/config.json', 'w') as fw:
    fw.write(ss_info + '\n')
with open('/etc/v2ray/server.json', 'w') as fw:
    fw.write(ss_info + '\n')

# -------------- Save client config info ----------------- #

CLIENT_CONFIG['outbound']['settings']['servers'].append({
    "address": ss_config['server_addr'],
    "password": ss_config['password'],
    "port": ss_config['server_port'],
    "method": ss_config['method'],
})

ss_info = json.dumps(CLIENT_CONFIG, sort_keys=True, indent=4)
ss_rule = '{method}:{password}@{server_addr}:{server_port}'
ss_link = 'ss://' + base64.b64encode(ss_rule.format(**ss_config).encode()).decode()

with open('/etc/v2ray/client.json', 'w') as fw:
    fw.write(ss_info + '\n')
with open('/etc/v2ray/sslink.info', 'w') as fw:
    fw.write(ss_link + '\n')

# -------------- install TCP BBR ----------------- #

# Adding open ports for firewalls
subprocess.call('firewall-cmd --zone=public --add-port=%d/tcp --permanent' % ss_config['server_port'], shell=True)

exec_shell(GET_BBR)

# Service enable after system restart
subprocess.call('sudo shutdown -r now', shell=True)
