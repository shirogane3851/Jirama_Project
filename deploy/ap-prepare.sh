#!/bin/bash
STA=wlp3s0
AP=ap0

# Attendre jusqu'à 60 s que la station soit connectée et lire son canal
for i in $(seq 1 60); do
  CH=$(iw dev $STA info | awk '/channel/ {print $2}')
  [ -n "$CH" ] && break
  sleep 1
done
[ -z "$CH" ] && { echo "$STA non connectée, abandon"; exit 1; }

# Créer ap0 si elle n'existe pas, avec sa MAC propre
ip link show $AP &>/dev/null || iw dev $STA interface add $AP type __ap
ip link set $AP address 98:22:ef:2d:97:51

# IP et activation
ip addr flush dev $AP
ip addr add 192.168.50.1/24 dev $AP
ip link set $AP up

# Config hostapd avec le canal détecté
sed "s/__CH__/$CH/" /etc/hostapd/hostapd.conf.tpl > /run/hostapd-ap0.conf

sysctl -w net.ipv4.ip_forward=0
