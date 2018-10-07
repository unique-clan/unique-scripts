#!/bin/sh

if [ "$(id -u)" -ne "0" ]; then
  echo "Please run as root"
  exit
fi

ipt()
{
  iptables "$@"
  ip6tables "$@"
}

# delete all rules
ipt -P INPUT ACCEPT
ipt -P FORWARD ACCEPT
ipt -P OUTPUT ACCEPT
ipt -F
ipt -X

# drop hostile ips
#ipt -A INPUT -s 1.2.3.4 -j DROP

# drop teeworlds serverinfo requests
ipt -N TWSERVERINFO
ipt -A INPUT -p udp --dport 8303:8350 -m string --algo bm --from 34 --to 54 --hex-string '|FF FF FF FF|gie3' -j TWSERVERINFO
ipt -A INPUT -p udp --dport 8303:8350 -m string --algo bm --from 34 --to 54 --hex-string '|FF FF FF FF|fstd' -j TWSERVERINFO
ipt -A TWSERVERINFO \
    -m hashlimit --hashlimit-upto 10/s --hashlimit-burst 60 --hashlimit-mode srcip --hashlimit-name twserverinfo \
    -m limit --limit 100/s --limit-burst 60 -j ACCEPT
ipt -A TWSERVERINFO -m limit --limit 1/m -j LOG --log-prefix "iptables drop TWSERVERINFO: "
ipt -A TWSERVERINFO -j DROP

# list rules
ipt -L

echo ""
echo "======================="

if ! dpkg-query -s iptables-persistent >/dev/null 2>&1; then
  echo "Please install iptables-persistent"
  echo "apt-get install iptables-persistent"
  exit
fi

echo "Saving rules"

iptables-save  > /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6
