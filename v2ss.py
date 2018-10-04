#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Auto deploy V2ray shadowsocks
# System Required:  CentOS 7
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
    'wget https://raw.githubusercontent.com/scriptgeeker/deploy-v2ray/master/lib-sh/v2ray.sh',
    'sudo chmod +x v2ray.sh && ./v2ray.sh',
]

# install TCP BBR
GET_BBR_TCP = [
    'wget https://raw.githubusercontent.com/scriptgeeker/deploy-v2ray/master/lib-sh/bbr.sh',
    'sudo chmod +x bbr.sh && ./bbr.sh',
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

def random_string(size=8, chars=string.ascii_letters):
    randstr = ''
    for i in range(size):
        randstr += random.choice(chars)
    return randstr


def get_ip_addr(pattern):
    ip_info = os.popen('ip addr').read()
    return re.findall(pattern, ip_info)[0]


os.chdir('/tmp')
for cmd in GET_V2RAY:
    subprocess.call(cmd, shell=True)

ss_config = {
    'server_addr': get_ip_addr(r'inet ([0-9\.]+)\/\d+ brd'),
    'server_port': random.randint(6000, 9000),
    'password': random_string(size=16),
    'method': 'aes-256-gcm',
}

SERVER_CONFIG['inbound']['port'] = ss_config['server_port']
SERVER_CONFIG['inbound']['settings']['method'] = ss_config['method']
SERVER_CONFIG['inbound']['settings']['password'] = ss_config['password']

with open('/etc/v2ray/config.json', 'w') as fw:
    fw.write(json.dumps(SERVER_CONFIG, sort_keys=True, indent=4))

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

# Auto start v2ray service
subprocess.call('sudo systemctl enable v2ray.service', shell=True)

# Adding open ports for firewalls
subprocess.call('firewall-cmd --zone=public --add-port=%d/tcp --permanent' % ss_config['server_port'], shell=True)

os.chdir('/tmp')
for cmd in GET_BBR_TCP:
    subprocess.call(cmd, shell=True)

# Service enable after system restart
subprocess.call('sudo shutdown -r now', shell=True)
