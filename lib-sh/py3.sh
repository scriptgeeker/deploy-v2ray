#!/usr/bin/env bash
#
# Auto install Python3
#
# Copyright (C) 2017 evrmji
#
# Thanks:
# https://teddysun.com
# And a lot of things copy from there
#
# System Required:  CentOS 6+


PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

green='\033[0;32m'
red='\033[0;31m'
yellow='\033[0;33m'
plain='\033[0m'

[[ $EUID -ne 0 ]] && echo -e "[${red}Error${plain}] This script must be run as root!" && exit 1

cur_dir=$( pwd )

python3_url="https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz"
python3_file="Python-3.6.4"
install_path="/usr/local/"

get_char() {
    SAVEDSTTY=`stty -g`
    stty -echo
    stty cbreak
    dd if=/dev/tty bs=1 count=1 2> /dev/null
    stty -raw
    stty echo
    stty $SAVEDSTTY
}

get_opsy() {
    [ -f /etc/redhat-release ] && awk '{print ($1,$3~/^[0-9]/?$3:$4)}' /etc/redhat-release && return
    [ -f /etc/os-release ] && awk -F'[= "]' '/PRETTY_NAME/{print $3,$4,$5}' /etc/os-release && return
    [ -f /etc/lsb-release ] && awk -F'[="]+' '/DESCRIPTION/{print $2}' /etc/lsb-release && return
}

check_sys() {
    local checkType=$1
    local value=$2

    local release=''
    local systemPackage=''

    if [ -f /etc/redhat-release ]; then
        release="centos"
        systemPackage="yum"
    elif cat /etc/issue | grep -Eqi "debian"; then
        release="debian"
        systemPackage="apt"
    elif cat /etc/issue | grep -Eqi "ubuntu"; then
        release="ubuntu"
        systemPackage="apt"
    elif cat /etc/issue | grep -Eqi "centos|red hat|redhat"; then
        release="centos"
        systemPackage="yum"
    elif cat /proc/version | grep -Eqi "debian"; then
        release="debian"
        systemPackage="apt"
    elif cat /proc/version | grep -Eqi "ubuntu"; then
        release="ubuntu"
        systemPackage="apt"
    elif cat /proc/version | grep -Eqi "centos|red hat|redhat"; then
        release="centos"
        systemPackage="yum"
    fi

    if [ ${checkType} == "sysRelease" ]; then
        if [ "$value" == "$release" ]; then
            return 0
        else
            return 1
        fi
    elif [ ${checkType} == "packageManager" ]; then
        if [ "$value" == "$systemPackage" ]; then
            return 0
        else
            return 1
        fi
    fi
}

detect_depends(){
    local command=$1
    local depend=`echo "${command}" | awk '{print $4}'`
    ${command}
    if [ $? != 0 ]; then
        echo -e "[${red}Error${plain}] Failed to install ${red}${depend}${plain}"
        exit 1
    fi
}

depends_install(){
    if check_sys packageManager yum; then
        echo -e "[${green}Info${plain}] Checking the EPEL repository..."
        if [ ! -f /etc/yum.repos.d/epel.repo ]; then
            yum install -y -q epel-release
        fi
        [ ! -f /etc/yum.repos.d/epel.repo ] && echo -e "[${red}Error${plain}] Install EPEL repository failed, please check it." && exit 1
        [ ! "$(command -v yum-config-manager)" ] && yum install -y -q yum-utils
        if [ x"`yum-config-manager epel | grep -w enabled | awk '{print $3}'`" != x"True" ]; then
            yum-config-manager --enable epel
        fi
        echo -e "[${green}Info${plain}] Checking the EPEL repository complete..."

        yum_depends=(
            zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc wget make xz
        )
        for depend in ${yum_depends[@]}; do
            detect_depends "yum -y -q install ${depend}"
        done
    elif check_sys packageManager apt; then
        apt_depends=(
            zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc wget make xz
        )
        for depend in ${apt_depends[@]}; do
            detect_depends "apt-get -y install ${depend}"
        done
    fi
}

download() {
    local filename=$(basename $1)
    if [ -f ${1} ]; then
        echo -e "[${green}Info${plain}] ${filename} [${green}found${plain}]"
   else
        echo -e "[${green}Info${plain}] ${filename} not found, download now..."
        wget --no-check-certificate -c -t3 -T60 -O ${1} ${2}
        if [ $? -ne 0 ]; then
            echo -e "[${red}Error${plain}] Download ${filename} failed."
            exit 1
        fi
    fi
}

download_files(){
    download "${python3_file}.tar.xz" "${python3_url}"
}

install_start(){
    download_files
    rm -fr ${cur_dir}/${python3_file}
    echo -e "[${green}Info${plain}] unzip ${python3_file} \c"
    tar vxf ${python3_file}.tar.xz  &> /dev/null && echo  -e  "${green}success...${plain}" || echo -e "${red}failed...${plain}"
    cd ${python3_file}
    echo -e "[${green}Info${plain}] prepare compile \c"
    ./configure --prefix=${install_path}${python3_file}  &> /dev/null && echo  -e  "${green}success...${plain}" || echo -e "${red}failed...${plain}"
    echo -e "[${green}Info${plain}] compiling \c"
    make -j 4  &> /dev/null && echo  -e  "${green}success...${plain}" || echo -e "${red}failed...${plain}"
    echo -e "[${green}Info${plain}] install \c"
    make install -j 4 &> /dev/null && echo  -e  "${green}success...${plain}" || echo -e "${red}failed...${plain}"
    ln -s ${install_path}${python3_file}/bin/pip3  /usr/bin/pip3
    ln -s ${install_path}${python3_file}/bin/python3 /usr/bin/python3
    echo "PATH=${install_path}${python3_file}/bin/:\$PATH " >> /etc/profile
    echo "PYTHONPATH=\$PYTHONPATH:${install_path}${python3_file}/lib/python3/" >> /etc/profile
    source /etc/profile
    if [ $? -ne 0 ]; then
        echo -e "[${red}Failed${plain}] ${python3_file} link failed."
        exit 1
    else
        echo -e "[${green}Success${plain}] ${python3_file}  link finish."
    fi
    if python3  --version &> /dev/null; then
        echo -e "[${green}Success${plain}] ${python3_file} Finish install."
    else
        echo -e "[${red}Failed${plain}] ${python3_file} Install failed."
        exit 1
    fi

}

install_finish(){
    rm -fr ${cur_dir}/${python3_file}
    rm -fr ${cur_dir}/${python3_file}.tar.xz
    version=$( python3 --version )
    echo -e "[${green}Info${plain}] Python Version: ${version}"
    echo -e "You can input \"python3\" to enter ${python3_file} and input \"pip3\" to manage your python3 packages."

}

install_python(){
    clear
    echo "---------------------------------------"
    echo " Auto install Python3"
    echo "                                       "
    echo " System Required:  CentOS/REHL 6+,"
    echo "  Debian(untest)"
    echo "------------  Information  ------------"
    echo " User   : $USER   Host: $HOSTNAME"
    echo " OS     : `get_opsy`"
    echo " Arch   : `uname -m`"
    echo " Kernel : `uname -r`"
    echo "--------------------------------------"

    depends_install
    install_start
    install_finish
}

uninstall_python(){
    printf "Are you sure uninstall ${red}${python3_file}${plain}? [y/n]\n"
    read -p "(default: n):" answer
    [ -z ${answer} ] && answer="n"
    if [ "${answer}" == "y" ] || [ "${answer}" == "Y" ]; then
        if check_sys packageManager yum; then
            chkconfig --del ${service_name}
        elif check_sys packageManager apt; then
            update-rc.d -f ${service_name} remove
        fi
        rm -fr ${install_path}${python3_file}
        rm -f /usr/bin/python3
        rm -f /usr/bin/pip3

        echo -e "[${green}Info${plain}] ${python3_file}$ uninstall success"
        echo -e "[${green}Info${plain}] ${red}Something in /etc/profile can't be clean! ${plain}"
    else
        echo
        echo -e "[${green}Info${plain}] ${python3_file}$ uninstall cancelled, nothing to do..."
        echo
    fi
}

action=$1
[ -z $1 ] && action=install
case "$action" in
    install|uninstall)
        ${action}_python
        ;;
    *)
        echo "Arguments error! [${action}]"
        echo "Usage: `basename $0` [install|uninstall]"
        ;;
esac